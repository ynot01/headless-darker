#! /bin/bash
wineserver -k
killall -SIGKILL winedevice.exe
killall -SIGTERM wineserver
killall -SIGTERM Tavern.exe
killall -SIGTERM TavernDart.exe
killall -SIGTERM TavernWorker.exe
killall -SIGTERM DungeonCrawler.exe
killall -SIGTERM GameThread
killall -SIGTERM services.exe
killall -SIGTERM explorer.exe
killall -SIGTERM conhost.exe
killall -SIGTERM tabtip.exe
killall -SIGTERM plugplay.exe
killall -SIGTERM rpcss.exe
killall -SIGTERM svchost.exe
killall -SIGTERM xalia.exe
killall -SIGTERM steam.exe
