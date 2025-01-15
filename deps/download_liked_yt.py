import queue
import threading
from threading import Thread
import deps.YTMusicScriptLib as ytmsl
from concurrent.futures import ThreadPoolExecutor


def main():

    ytmsl.setUpMusicFolder()
    previousDownloads = ytmsl.importPreviousDownloads()
    tracks = ytmsl.fetchPlaylist()

    driver = ytmsl.setUpDriver()

    # Lock for previousDownloads
    lock = threading.Lock()

    # Holds futures for threads
    futures = []

    # Printer Thread Setup
    messageQueue = queue.Queue()
    # Daemon so it stops when script ends
    printerThread = Thread(target=ytmsl.printer, args=(messageQueue,), daemon=True, name='Printer')
    printerThread.start()

    # Holds order of songs
    orderedSongs = queue.PriorityQueue()

    print("Starting downloads....")
    position = 0      # Puts songs in order so order is always preserved in iTunes
    newSongCount = 0
    with ThreadPoolExecutor(max_workers=700) as executor: 
        for track in tracks:
            if track.get("videoID") not in previousDownloads:
                try:
                    url = ytmsl.getDownloadURL(track.get("videoID"), driver)
                    if url != None:
                        newSongCount += 1
                        position += 1
                        futures.append(executor.submit(ytmsl.task, track, url, previousDownloads, lock, messageQueue, orderedSongs, position))
                    else: 
                        artists = ""
                        for artist in track.get("artists"):
                            artists += artist.get("name") + ", "
                        print("Could not convert " + track.get("title") + " - " + artists)
                except Exception as e:
                    print("Error: ", e)
        # Downloaded all the songs, close driver
        driver.close()
        
        # Get futures so we can see any errors
        for future in futures:
            try:
                result = future.result() # could throw an exception if the thread threw an exception
                if result != None:
                    print(result)
            except Exception as e:
                print('Thread threw exception:', e)


    # Update pickle database file
    print("Updating database....")
    ytmsl.updatePickleFile(previousDownloads)

    # Printer Thread Setup
    print("Adding songs to iTunes Music Library....")
    # Daemon so it stops when script ends
    orderThread = Thread(target=ytmsl.order, args=(orderedSongs,), daemon=True, name='Order')
    orderThread.start()
    orderThread.join()

    print("Done! Downloaded " + str(newSongCount) + " new songs.")




