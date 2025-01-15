import time
import eyed3
import pickle
import os.path
import deps.YTMusicScriptLib as ytmsl
from requests import get
from ytmusicapi import *
from selenium import webdriver
import deps.Helpers as Helpers
import config.Config as Config
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
from threading import Thread
import deps.YTMusicScriptLib as ytmsl

# TODO: Change liked playlist routine to copy instead of move to iTunes playlist, 
# then use the songs in Music folder to add to playlist?


def main():
    playlistName = input()
    ytmsl.setUpMusicFolder(playlistName)

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