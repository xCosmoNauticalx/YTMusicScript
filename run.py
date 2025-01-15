import sys
import deps.download_liked_yt as download_liked_yt
import deps.YTMusicScriptLib as ytml
import config.Config as Config
import deps.Helpers as Helpers
import deps.download_single as download_single

if __name__ == "__main__":

    # Check command-line args for RunMode
    if len(sys.argv) > 1:
        Config.runMode = Helpers.getRunMode(sys.argv[1])
    
    print("Welcome to the Youtube Music Script!")
    print("Please choose an option from below:")
    print("1: Download songs from Liked playlist")
    print("2: Download songs from a specific playlist")
    print("3: Download a single song")
    print("4: Update auth token")
    print("5: Update folder locations")
    #Download single song without adding to previous downloads

    response = int(input())
    while (not 1 <= response <= 5):
        print("Invalid response, please try again: ")
        response = int(input())
    

    if response == 1:
        download_liked_yt.main()
        sys.exit()
    elif response == 2:
        # TODO
        print("This has not been implemented yet")
    elif response == 3:
        print("Enter the track ID for the song:")
        trackID = input()
        download_single.main(trackID)
    elif response == 4:
        # TODO
        print()
    elif response == 5:
        # TODO
        print()
  