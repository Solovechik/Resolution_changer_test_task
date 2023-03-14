import os.path
import re
import subprocess
from winreg import HKEY_LOCAL_MACHINE, OpenKey, QueryValueEx
import ctypes


class ResolutionChanger:
    GAME_PATHS_TO_SEARCH = (
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App ',
        r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App ',
    )

    STEAM_PATHS_TO_SEARCH = (
        r'SOFTWARE\WOW6432Node\Valve\Steam',
        r'SOFTWARE\Valve\Steam'
    )

    def __init__(self, app_number: str):
        self.__app_number = app_number

    def change_game_resolution(self) -> None:
        """
        Changes a user's screen resolution.
        """
        game_folder = self.__get_user_folder(self.GAME_PATHS_TO_SEARCH, 'InstallLocation', self.__app_number)
        width, height = self.__get_user_resolution()

        with open(fr'{game_folder}\game\dac\cfg\video.txt', 'r', encoding='UTF-8') as file_to_read:
            game_config = file_to_read.read()
            game_config = re.sub(r'(?P<g1>.*setting\.defaultres\W*)(\d+)(.*)', fr'\g<g1>{width}\3', game_config)
            game_config = re.sub(r'(?P<g1>.*setting\.defaultresheight\W*)(\d+)(.*)', fr'\g<g1>{height}\3', game_config)

        with open(fr'{game_folder}\game\dac\cfg\video.txt', 'w', encoding='UTF-8') as file_to_write:
            print(game_config, file=file_to_write)

    def launch_steam(self) -> None:
        """
        Searches and launches steam app.
        """
        steam_folder = self.__get_user_folder(self.STEAM_PATHS_TO_SEARCH, 'InstallPath')
        subprocess.Popen(fr'{steam_folder}\Steam.exe')

    @staticmethod
    def __get_user_resolution() -> tuple[int, ...]:
        """
        Gets a user's resolution.
        :return: User's screen resolution.
        """
        user = ctypes.windll.user32
        screensize = user.GetSystemMetrics(0), user.GetSystemMetrics(1)

        return screensize

    @staticmethod
    def __get_user_folder(paths_to_search: tuple[str, ...], registry_key_name: str, app: str = '') -> str:
        """
        Returns a path to a folder by given registry paths and key.
        :param paths_to_search: Possible paths to search.
        :param registry_key_name: Windows registry key name.
        :return: A path to a directory.
        """
        folder = None

        for path in paths_to_search:
            try:
                with OpenKey(HKEY_LOCAL_MACHINE, path + app) as key:
                    folder = QueryValueEx(key, registry_key_name)[0]
            except FileNotFoundError:
                pass

        if folder is None or not os.path.exists(folder):
            raise Exception("Folder can't be found!")

        return folder


if __name__ == '__main__':
    dota = ResolutionChanger('1046930')
    dota.change_game_resolution()
    dota.launch_steam()
