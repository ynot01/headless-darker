import asyncio
from datetime import UTC, datetime
from os import environ, path
from pathlib import Path
from re import split
from subprocess import Popen, run
from sys import platform, stdout
from time import sleep
from traceback import print_tb
from urllib import parse
from xml import parsers

from aiohttp import ClientSession
from discord import File, Object, Webhook
from dotenv import load_dotenv
from requests import exceptions, get
from rss_parser import RSSParser

_print = print


def print(*args, **kwargs):  # type: ignore
    _print(f'[{datetime.now(UTC)}]', *args, **kwargs)  # type: ignore
    stdout.flush()


STEAM_COMPAT_DATA_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamapps',
    'compatdata',
    '2016590',
)
STEAM_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
)
TAVERN_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamapps',
    'common',
    'Dark and Darker',
    'Tavern.exe',
)
PROTON_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamapps',
    'common',
    'Proton - Experimental',
    'proton',
)
STEAMCMD_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamcmd',
    'steamcmd.sh',
)
USMAP_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamapps',
    'common',
    'Dark and Darker',
    'DungeonCrawler',
    'Binaries',
    'Win64',
    'Mappings.usmap',
)
UE4SS_PATH = path.join(
    Path.cwd(),
    'UE4SS',
)
WIN64_PATH = path.join(
    Path.home(),
    '.local',
    'share',
    'Steam',
    'steamapps',
    'common',
    'Dark and Darker',
    'DungeonCrawler',
    'Binaries',
    'Win64',
)
UPDATE_CHECK_MINUTES = 10


def main():
    print('Checking requirements...')
    if check_requirements() > 0:
        return
    print(
        'All requirements passed. '
        f'Now checking for an update every {UPDATE_CHECK_MINUTES} minutes.'
    )
    checked_times = 0
    current_build = 0
    while True:
        # Check if Dark and Darker has a newer build
        fetch_build = get_latest_build()
        if checked_times < 3:
            checked_times += 1
            if checked_times == 3:
                print('Checking for update... (Silencing this message)')
            else:
                print('Checking for update...')
        if fetch_build <= current_build:
            sleep(
                60 * UPDATE_CHECK_MINUTES
            )  # Build did not change, wait x minutes
            continue
        if current_build == 0:
            current_build = fetch_build
            sleep(60 * UPDATE_CHECK_MINUTES)
            continue
        print('Dark and Darker has updated!')
        current_build = fetch_build

        print('Running SteamCMD...')
        steamcmd_proc = run(
            [
                'bash',
                STEAMCMD_PATH,
                '+login '
                f'{environ.get("STEAM_USERNAME")} '
                f'{environ.get("STEAM_PASSWORD")} '
                f'{get_steamguard()}',
                '+app_update 2016590',
                '+quit',
            ],
            capture_output=True,
            text=True,
        )
        while (
            steamcmd_proc.returncode > 0
            or 'ERROR' in steamcmd_proc.stdout
            or 'already up to date' in steamcmd_proc.stdout
        ):
            print('SteamCMD STDOUT: \n', steamcmd_proc.stdout)
            print('SteamCMD STDERR: \n', steamcmd_proc.stderr)
            print(
                'SteamCMD exited with code',
                steamcmd_proc.returncode,
                'Retrying in 30 seconds...',
            )
            sleep(30)
            steamcmd_proc = run(
                [
                    'bash',
                    STEAMCMD_PATH,
                    '+login '
                    f'{environ.get("STEAM_USERNAME")} '
                    f'{environ.get("STEAM_PASSWORD")} '
                    f'{get_steamguard()}',
                    '+app_update 2016590',
                    '+quit',
                ],
                capture_output=True,
                text=True,
            )
        print('Updated Dark and Darker successfully.')

        print('Copying UE4SS to Dark and Darker...')
        copy_proc = run(
            [
                'cp',
                '-rf',
                f'{UE4SS_PATH}/.',
                WIN64_PATH,
            ],
            capture_output=True,
            text=True,
        )
        if copy_proc.returncode > 0:
            raise ValueError(
                'Copy operation failed! '
                f'Return code: {copy_proc.returncode}\n'
                f'STDOUT:\n{copy_proc.stdout}\n'
                f'STDERR:\n{copy_proc.stderr}'
            )
        print('UE4SS installed successfully.')

        # Removes USMap file, if one already exists
        Path.unlink(Path(USMAP_PATH), True)

        while not path.exists(USMAP_PATH):
            print('Running Dark and Darker...')
            proton_env = environ.copy()
            proton_env['PROTON_LOG'] = '1'
            proton_env['WINEDEBUG'] = '+timestamp,+pid,+tid'
            ',+seh,+debugstr,+module'
            proton_env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = STEAM_PATH
            proton_env['STEAM_COMPAT_DATA_PATH'] = STEAM_COMPAT_DATA_PATH
            Popen(
                [
                    'xvfb-run',
                    '-e',
                    '/dev/stdout',
                    '-n',
                    '98',
                    PROTON_PATH,
                    'run',
                    TAVERN_PATH,
                    '-server=localhost',
                    '-steam=1',
                    '-taverntype=steam',
                    '-tavernapp=dad',
                    '-nullrhi',
                    '-nullrhi',
                    '-nosound',
                    '-unattended',
                ],
                text=True,
                env=proton_env,
            )
            missing_times = 0
            # Check if USMap file exists
            while missing_times <= 5 and not path.exists(USMAP_PATH):
                sleep(10)
                print('Checking for USMap file...')
                missing_times += 1
            print('Assuming this run failed. Restarting Dark and Darker...')
            nuke_wine()
        nuke_wine()

        print('Found USMap!')

        print('Sending USMap to webhook...')
        asyncio.run(send_usmap_to_webhook(current_build))
        print('Sent USMap to webhook!')
        # Loop here


# Nukes wine processes
def nuke_wine():
    run(['killall', '-SIGKILL', 'winedevice.exe'])
    run(
        [
            'killall',
            '-SIGTERM',
            'wineserver',
            'Tavern.exe',
            'TavernDart.exe',
            'TavernWorker.exe',
            'DungeonCrawler.exe',
            'GameThread',
            'services.exe',
            'explorer.exe',
            'conhost.exe',
            'tabtip.exe',
            'plugplay.exe',
            'rpcss.exe',
            'svchost.exe',
            'xalia.exe',
            'steam.exe',
        ]
    )


async def send_usmap_to_webhook(build: int):
    version = get_latest_version()
    with open(USMAP_PATH, 'rb') as map_file:
        discord_file = File(
            fp=map_file,
            filename=parse.quote(
                f'{version}.usmap', safe='/', encoding=None, errors=None
            ),
        )
        async with ClientSession() as session:
            webhook = Webhook.from_url(
                f'{environ.get("WEBHOOK_URL")}', session=session
            )
            threadid = environ.get('DISCORD_THREAD_ID')
            roleid = environ.get('DISCORD_ROLE_ID')
            roleid = (
                f'<@&{roleid}> - Click Channels & Roles to get this role'
                if roleid
                else ''
            )
            if threadid and int(threadid) > 0:
                await webhook.send(
                    f'New usmap from version {version}'
                    f' - Steam build {str(build)}\n'
                    '-# Source: <https://github.com/ynot01/headless-darker>\n'
                    f'{roleid}',
                    file=discord_file,
                    thread=Object(threadid),
                )
            else:
                await webhook.send(
                    f'New usmap from version {version}'
                    f' - Steam build {str(build)}\n'
                    '-# Source: <https://github.com/ynot01/headless-darker>\n'
                    f'{roleid}',
                    file=discord_file,
                )


def get_steamguard() -> str:
    steamguard_proc = run(
        ['steamguard', '--username', f'{environ.get("STEAM_USERNAME")}'],
        capture_output=True,
        text=True,
    )
    while steamguard_proc.returncode > 0:
        print('Steamguard-CLI STDOUT: \n', steamguard_proc.stdout)
        print('Steamguard-CLI STDERR: \n', steamguard_proc.stderr)
        print(
            'Steamguard-CLI exited with code',
            steamguard_proc.returncode,
            'Retrying in 30 seconds...',
        )
        sleep(30)
        steamguard_proc = run(
            ['steamguard', '--username', f'{environ.get("STEAM_USERNAME")}'],
            capture_output=True,
            text=True,
        )
    return steamguard_proc.stdout


def check_requirements() -> int:
    if platform != 'linux':
        print(
            'This project is only supports Linux servers and your platform is',
            platform,
        )
        if platform == 'win32' or platform == 'cygwin' or platform == 'msys':
            print(
                'On Windows, you can try running the project via WSL: '
                'https://learn.microsoft.com/en-us/windows/wsl/install'
            )
        return 1
    load_dotenv()
    if environ.get('STEAM_USERNAME') is None:
        print('STEAM_USERNAME environment variable was not defined')
        return 1
    if environ.get('STEAM_PASSWORD') is None:
        print('STEAM_PASSWORD environment variable was not defined')
        return 1
    if not path.isdir(STEAM_PATH):
        print('Steam was not found at $HOME/.local/share/Steam/')
        return 1
    if not path.exists(TAVERN_PATH):
        print(
            'Tavern.exe was not found at '
            "$HOME/.local/share/Steam/steamapps/common/'Dark and Darker'/"
        )
        return 1
    if not path.isdir(UE4SS_PATH):
        print(
            'UE4SS folder not found in current working directory. '
            'Please run from the project root!'
        )
        return 1
    if not path.exists(PROTON_PATH):
        print(
            'proton executable was not found at '
            "$HOME/.local/share/Steam/steamapps/common/'Proton - Experimental'/"
        )
        return 1
    if not path.exists(STEAMCMD_PATH):
        print(
            'steamcmd.sh was not found at '
            '$HOME/.local/share/Steam/steamapps/steamcmd/'
        )
        return 1
    if not path.exists(
        path.join(
            Path.home(),
            '.config',
            'steamguard-cli',
            'maFiles',
            f'{environ.get("STEAM_USERNAME")}.maFile',
        )
    ):
        print(
            'steamguard-cli credential file was not found at '
            f'$HOME/.config/steamguard-cli/maFiles/{environ.get("STEAM_USERNAME")}.maFile'
        )
        return 1
    if not path.exists(
        path.join(
            Path.home(),
            '.config',
            'steamguard-cli',
            'maFiles',
            'manifest.json',
        )
    ):
        print(
            'manifest.json was not found at '
            '$HOME/.config/steamguard-cli/maFiles/'
        )
        return 1
    return 0


def get_latest_version() -> str:
    try:
        version_url = 'http://cdn.darkanddarker.com/Dark%20and%20Darker/Build/BuildVersion.txt'
        return get(version_url).text.rstrip()
    except exceptions.RequestException as err:
        print_tb(err.__traceback__)
        print(err.__class__, ':', err)
        return 'UnknownVersion'


def get_latest_build() -> int:
    try:
        rss_url = 'https://steamdb.info/api/PatchnotesRSS/?appid=2016590'
        response = get(rss_url)
        rss = RSSParser.parse(response.text)

        largest_build = 0
        for item in rss.channel.items:
            splitbuild = split('#', item.guid.content)
            if len(splitbuild) > 1:
                buildnum = int(splitbuild[1])
                if buildnum > largest_build:
                    largest_build = buildnum
        return largest_build
    except exceptions.RequestException as err:
        print_tb(err.__traceback__)
        print(err.__class__, ':', err)
        return 0
    except parsers.expat.ExpatError as err:
        print_tb(err.__traceback__)
        print(err.__class__, ':', err)
        return 0


if __name__ == '__main__':
    main()
