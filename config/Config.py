from enum import Enum

# User variables ** CHANGE THESE ONLY **
initialFilePathBase = "/Users/kelseygarcia/Hobbies/Programming/YTMusicScript/Music/"
thumbnailsFilePathBase = "/Users/kelseygarcia/Hobbies/Programming/YTMusicScript/"
iTunesFilePathBase = "/Users/kelseygarcia/Music/Music/Media/Automatically Add to Music.localized/"

# ** DO NOT CHANGE THE BELOW VALUES **
pdFile = 'databases/previousDownloads.pkl'

class RunMode(Enum):
    VERBOSE = 1
    DEBUG = 2
    REGULAR = 3

runMode = RunMode.REGULAR


