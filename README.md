# headless-darker

Automated Dark and Darker wiki tool

Runs Dark and Darker headless for use in a Linux server

Current used UE4SS version is `zDEV-UE4SS_v3.0.1-632-gb734711.zip`

Make sure to move dwmapi.dll to the UE4SS folder when updating UE4SS

UE4SS is licensed under MIT - https://github.com/UE4SS-RE/RE-UE4SS

## USMap Generation Concept

1. Loop every 1 minute check if Dark and Darker has an update
2. Update Dark and Darker
3. Run `bash copy_win64.sh` or python equivalent
4. Run `bash start_tavern.sh` or python equivalent
5. Loop every 5 seconds check if Mapping.usmap exists
6. Run `bash kill_proton.sh` or python equivalent
7. Go back to step 1

## Requirements

- Steam should be installed at `$HOME/.local/share/Steam/`
- Dark and Darker should be installed at `$HOME/.local/share/Steam/steamapps/common/'Dark and Darker'`
- Proton Experimental should be installed at `$HOME/.local/share/Steam/steamapps/common/Proton\ -\ Experimental/`
- [uv](https://github.com/astral-sh/uv) should be installed

## Usage

`uv run main.py`