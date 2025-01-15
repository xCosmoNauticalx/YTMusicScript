import queue
import config.Config
import threading
from threading import Thread
import deps.YTMusicScriptLib as ytmsl
from concurrent.futures import ThreadPoolExecutor

def main(videoID):

    ytmsl.setUpMusicFolder()
    driver = ytmsl.setUpDriver()

    try:
        track = ytmsl.getSingle(videoID)
        url = ytmsl.getDownloadURL(videoID, driver)
        ytmsl.singleTask(track, url)
        print("Downloaded" + track.get("title") + " - " + track.get("artists"))
    except Exception as e:
        print(f"Error: {e}")