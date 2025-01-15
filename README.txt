To download music from "liked" playlist on YouTube:

First Run:
    1. Make sure Chrome is installed
    2. Open a Terminal window
    3. Install Python 3
	a. pip install python3
    4. Install dependencies:
        1. pip install ytmusicapi
        2. pip install selenium
        3. pip install eyed3
    5. Open up Config.py:
	a. Change initialFilePathBase to the FULL path to where you want your music stored 
	  (ex: "/Users/kelseygarcia/Hobbies/Programming/YTMusicScript/Music/"
	b. Change thumbnailFilePathBase to the FULL path to where you want to store the artwork
	  (ex: "/Users/kelseygarcia/Hobbies/Programming/YTMusicScript/") 
	  ** Note: This is a temporary location, artwork files will be removed when script is done **
	c. If you want songs to be transferred to iTunes, change iTunesFilePathBase to your "Add to iTunes folder (ex. "/Users/kelseygarcia/Music/Music/Media/Automatically Add to Music.localized/") and uncomment lines 67 - 71 in run.py 
	    ** Note that this will change the location of your music from what you defined in 		    initialFilePathBase, but you still need to set it **

To download music:
    1. Update your Youtube Music auth token:
   	a. In CHROME, navigate to music.youtube.com, make sure you're signed in
	b. Right click anywhere on the page and click "inspect" to bring up dev tools
    	c. Under the "Network" tab, filter for "/browse" and select one of the requests that come up 	    (You may need to refresh the browser for the browse token to show up)
    	d. Right-click the browse token in the left-hand pane (under Name) and hit Copy -> "copy as 	   cURL"
    	e. Go to https://curlconverter.com/json/ and past the cURL command
    	f. Copy everything in the HEADER SECTION ONLY, starting at "accept": */*
    	g. Paste into headers_auth.json file in the same directory as the script (Make sure to 		   enclose json header content in curly braces)
    2. Run script:
        1. Open Terminal at folder script is in (Left-click folder and select "New Terminal at Folder"
        2. python3 download_liked_yt.py