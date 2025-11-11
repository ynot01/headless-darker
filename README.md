# headless-darker

Automated Dark and Darker wiki tool

Runs Dark and Darker headless for use in a Linux server

Current used UE4SS version is `zDEV-UE4SS_v3.0.1-632-gb734711.zip`

Make sure to move dwmapi.dll to the UE4SS folder when updating UE4SS

UE4SS is licensed under MIT - https://github.com/UE4SS-RE/RE-UE4SS

## Requirements

- A Linux environment (Tested on Ubuntu 24.04, but others will probably work)
- A 2FA-enabled Steam account that owns Dark and Darker
- Steam should be installed at `$HOME/.local/share/Steam/`
- Dark and Darker should be installed at `$HOME/.local/share/Steam/steamapps/common/'Dark and Darker'` (Run `app_update 2016590` in steamcmd)
- Proton Experimental should be installed at `$HOME/.local/share/Steam/steamapps/common/'Proton - Experimental'/` (Run `app_update 1493710` in steamcmd)
- Steam Linux Runtime 3.0 (sniper) should probably be installed (Run `app_update 1628350` in steamcmd)
- [steamguard-cli](https://github.com/dyc3/steamguard-cli) should be installed, and credentials stored in `$HOME/.config/steamguard-cli/maFiles/`
- [uv](https://github.com/astral-sh/uv) should be installed for a reliable Python environment
- xvfb-run (`sudo apt install xorg xserver-xorg xvfb libx11-dev libxext-dev libxcursor-dev -y`)
- bash

## Usage

`uv run main.py`