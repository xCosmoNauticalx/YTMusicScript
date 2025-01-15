import sys
import argparse
from config.Config import RunMode
import config.Config as Config

# def createArgParser():
#     argParser = argparse.ArgumentParser(description="Downloads music from a Liked playlist on Youtube")
#     argParser.add_argument("-v", action='store_const', nargs='?', const=RunMode.VERBOSE, default=RunMode.REGULAR)


def printHelpMenu():
    print("This script downloads music from your Liked Youtube playlist, combines them with their album" +
          " artwork and stores them on your machine")
    print("If run without arguments, you will only see each song listed as it has finished downloading")
    print("Use flag --verbose to print out additional information at each step of the process")
    print("Use flag --debug to view debug statements to identify an issue")
    print("Use flag --help to print this menu")
    sys.exit(1)


def getRunMode(arg):
    if(arg == "--verbose"):
        return RunMode.VERBOSE
    elif(arg == "--debug"):
        return RunMode.DEBUG
    elif(arg == "--help"):
        printHelpMenu()
    else:
        print("Invalid RunMode option. Run with --help to see valid arguments")
        sys.exit(1)


def isDebugMode():
    if (Config.runMode == RunMode.DEBUG):
        return True
    else:
        return False