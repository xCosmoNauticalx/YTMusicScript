import time
import eyed3
import pickle
import os.path
from requests import get
from ytmusicapi import *
from selenium import webdriver
import deps.Helpers as Helpers
import config.Config as Config
from eyed3.id3.frames import ImageFrame
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ************* Have each download add to dictionary instead of writing to file, and then when done downloading all of them, 
# Write the dictionary to the file (overwrite?). This way less time is used opening/closing the file


# Create folder to hold music if it doesn't exist
def setUpMusicFolder(name="Music"):
    print(f"Checking for {name} folder....")
    path = os.path.dirname(__file__) + f"/{name}/"
    if not os.path.exists(path):
        os.mkdir(path)
        print(f"{name} folder created!")
    else:
        print(f"{name} folder found!")


# Download file from url, this stops the program unitl the file is downloaded, no need to poll with Selenium
def download_file(url, file_path):
    try:
        with get(url, stream = True) as response:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024): 
                    if chunk:
                        file.write(chunk)
    except Exception as e:
        print("Error downloading file: ", e)
    



# Import previous downloads into dict for easy searching
def importPreviousDownloads():
    print("Checking for previous downloads....")
    previousDownloads = {}
    try:
        with open(Config.pdFile, 'x') as file:
            print("No previous downloads found, database file created.")
            file.close()
    except:
        with open(Config.pdFile, 'rb') as file:
            print("Found previous downloads")
            previousDownloads = pickle.load(file)
            file.close()

    return previousDownloads


# Write videoID to file containing songs that were previously downloaded so we don't download them again next time
def updatePickleFile(previousDownloads):
    with open(Config.pdFile, 'wb') as file:
        pickle.dump(previousDownloads, file)
        file.close()


def getSingle(videoID):
    # Authorized request to user's liked playlist
    print("Fetching Song from Youtube....")
    ytmusic = YTMusic()
    try:
        track = ytmusic.get_song(videoID)
        track = track.get("videoDetails")
    except Exception as e:
        print(f"Error getting song through api: {e}")

    return {"videoID": videoID, "title": track.get("title"), "artists": track.get("author"), "thumbnails": track.get("thumbnails")}


# Retrieve liked playlist from YouTube
def fetchPlaylist():
    # Authorized request to user's liked playlist
    print("Fetching YouTube playlist....")
    ytmusic = YTMusic('config/headers_auth.json')
    try:
        playlist = ytmusic.get_liked_songs(limit=1)

        trackCount = playlist.get("trackCount")
        playlist = ytmusic.get_liked_songs(limit=trackCount)
    except Exception as e:
        print("Error importing playlist: ", e)
        exit(1)

    # Pull out the videoID, title, and artist(s) for each track
    tracks = []
    for track in playlist["tracks"]:
        tracks.append({"videoID": track.get('videoId'), "title": track.get('title'),  "artists": track.get("artists"), "album": track.get("album"), "thumbnails": track.get("thumbnails")})
    print("YouTube playlist imported!")
    return tracks



def getDownloadURL(videoID, driver):
    try:
        if (Helpers.isDebugMode()):
            print("Navigating to Converter website")

        driver.get("https://ytmp3.nu/en/ChSg?r=r")
        # Create url to download video
        videoURL = "https://music.youtube.com/watch?v=" + videoID + "&list=LM"

        if (Helpers.isDebugMode()):
            print("Created Song url: " + videoURL)

        # Type track url into urlbox
        urlBox = driver.find_element(By.ID, 'url')
        urlBox.send_keys(videoURL)

        if (Helpers.isDebugMode()):
            print("Url entered into text box")

        # Click confirm to start conversion
        confirmButton = driver.find_element(By.XPATH, '/html/body/form/div[2]/input[2]')

        if(Helpers.isDebugMode()):
            print("Confirm button found")

        confirmButton.click()

        if(Helpers.isDebugMode()):
            print("Confirm button clicked")
       

        # Wait for download to be available - Give it at least 5 minutes
        download = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/a[1]'))
        )

        if(Helpers.isDebugMode()):
            print("Download url retrieved")

        # return url of download file
        return download.get_attribute('href')
    except Exception as e:
        print("Error getting download URL: ", e)
    


def cleanTrackInfo(track):
    # Set up track, get album name and thumbnail
    videoTitle = track["title"]
    title = ""
    artists = "" 
    
    # Check if title and artist are in video title, separate them if so. Assumes artist comes before title
    # If not, title and artists are in dict already
    if " - " in videoTitle:
        index = videoTitle.find(" - ")
        artists = videoTitle[0:index]
        title = videoTitle[index + 3:]
        if title[0] == " ":
            title = title[1:]
    else:
        title = videoTitle
        # Get artist name(s)
        numArtists = len(track["artists"])
        i = 1;   
        for artist in track["artists"]:
            artistName = artist.get("name")
            if '/' in artistName:
                artistName = artistName.replace('/', "|")
            artists += artistName
            if i != numArtists:
                artists += ", "
            i += 1
    
    # Check for slashes that will mess with filepath
    if '/' in title:
        title = title.replace("/", ",")
    # Remove extra bullshit people put in the title
    if "[HQ]" in title:
        title = title.replace("[HQ]", "")
    if "(Official Lyric VIdeo)" in title:
        title = title.replace("(Official Lyric VIdeo)", "")

    # Handle where album is unkown
    try:
        album = track["album"].get("name")
    except:
        album = "Unknown Album"

    # Create track file name
    trackFileName = title + " - " + artists + ".mp3"

    # Get thumbname url
    thumbnail = track["thumbnails"][len(track["thumbnails"]) - 1].get("url")

    return {"title": title, "artists": artists, "album": album, "fileName": trackFileName, "thumbnailURL": thumbnail, "videoID": track.get("videoID")}



# Add track info to .mp3 tag
def addMP3Tag(downloadFP, thumbnailFP, track):
    audiofile = eyed3.load(downloadFP)
    if (audiofile.tag == None):
        audiofile.initTag()
    audiofile.tag.title = track.get("title")
    audiofile.tag.artist = track.get("artists")
    audiofile.tag.album = track.get("album")
    audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(thumbnailFP,'rb').read(), 'image/jpeg')
    audiofile.tag.save()

# Delete the thumbnail file after it's been added to the tag
def deleteThumbnailFile(fileName):
    os.remove(fileName)
        

def setUpDriver():
    # Selenium setup, changes download folder (May no longer be needed with download_file method)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options)
    return driver

# task for printing thread
def printer(queue):
    while True:
        # get messages
        message = queue.get()
        # print the message
        if message != None:
            print(message)

# Adds music to iTunes Library in order they are in on YouTube
def order(queue):
    while not queue.empty():
         file = queue.get()[1]
         try:
            os.rename(str(os.path.dirname(__file__) + "/Music/" + file), str(Config.iTunesFilePathBase + file))
            # Sleep for a second so songs (hopefully) get added to library in order
            time.sleep(4)
         except Exception as e:
            print(f"Potential duplicate prevented transfer of {file}: {e}")
            print("Make sure this song is in iTunes")
        
    

def singleTask(track, url):
    # Clean up track info & remove what we don't need
    track = cleanTrackInfo(track)
    print(track)
    
    downloadFilePath = Config.initialFilePathBase + track.get("fileName")
    thumbnailFilePath = Config.thumbnailsFilePathBase + track.get("title") + " - " + track.get("artists") + ".jpeg"
    track["filePath"] = downloadFilePath

    # 2 threads to download song and thumbnail
    futures = []
    with ThreadPoolExecutor(max_workers=2) as executor: 
        futures.append(executor.submit(download_file, track.get("thumbnailURL"), thumbnailFilePath))
        futures.append(executor.submit(download_file, url, downloadFilePath))
        

    # Get futures so we can see any errors
        for future in futures:
            try:
                result = future.result() # could throw an exception if the thread threw an exception
                if result != None:
                    print(result)
            except Exception as e:
                print('Thread threw exception:', e)
                print("Could not process " + track.get("title") + " - " + track.get("artists"))

    addMP3Tag(downloadFilePath, thumbnailFilePath, track)
    deleteThumbnailFile(thumbnailFilePath)


# Thread task to download songs
def task(track, url, previousDownloads, lock, messageQueue, orderedSongs, position):

    # Clean up track info & remove what we don't need
    track = cleanTrackInfo(track)
    
    downloadFilePath = Config.initialFilePathBase + track.get("fileName")
    thumbnailFilePath = Config.thumbnailsFilePathBase + track.get("title") + " - " + track.get("artists") + ".jpeg"
    track["filePath"] = downloadFilePath

    # 2 threads to download song and thumbnail
    futures = []
    with ThreadPoolExecutor(max_workers=2) as executor: 
        futures.append(executor.submit(download_file, track.get("thumbnailURL"), thumbnailFilePath))
        futures.append(executor.submit(download_file, url, downloadFilePath))
        

    # Get futures so we can see any errors
        for future in futures:
            try:
                result = future.result() # could throw an exception if the thread threw an exception
                if result != None:
                    print(result)
            except Exception as e:
                messageQueue.put('Thread threw exception:', e)
                print("Could not process " + track.get("title") + " - " + track.get("artists"))

    addMP3Tag(downloadFilePath, thumbnailFilePath, track)
    deleteThumbnailFile(thumbnailFilePath)

    # Save to previous downloads - thread-safe
    lock.acquire()
    previousDownloads[track.get("videoID")] = track.get("title") + " - " + track.get("artists")
    lock.release()

    # Put song into ordered queue and send track info to message queue
    orderedSongs.put((position, track.get("fileName")))
    messageQueue.put(f'{track.get("title")} - {track.get("artists")}')



def getTenMostRecentlyDownloaded():
    previousDownloads = list(importPreviousDownloads().values())

    for i in range(len(previousDownloads)-1, len(previousDownloads)-10, -1):
        print(previousDownloads[i])