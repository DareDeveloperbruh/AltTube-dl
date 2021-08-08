# AltTube-dl v3.1 | Video Downloader for BitView.net, VidLii.com
AltTube-dl is an easy to use Python script that allows users to download videos from BitView.net and VidLii.com, 2008-YouTube-like alternative video-hosting sites.  
Python is **not** required to run this tool, unless you choose to download alttube-dl.py.

# Instructions
*For most users*
1. [Download AltTube-dl.zip](https://github.com/DareDeveloperbruh/AltTube-dl/releases/download/v3.1/alttube-dl.zip)
2. [Download ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z)
3. Make a folder on your Desktop called "AltTube-dl" and drag the contents of AltTube-dl.zip into it.
4. Double click the ffmpeg ZIP file, click the "ffmpeg-4.4-essentials_build" folder, then click the "bin" folder and drag "ffmpeg.exe" into the AltTube-dl folder on your Desktop.

Please note that, because AltTube-dl executable files are produced using the commonly used cx_freeze, antivirus providers might flag it as suspicious. However, the code is completely open-source and can be ran in Python 3 using alttube-dl.py.
If Windows SmartScreen stops you from running AltTube-dl, click More info, and click Run anyway.  
For power users, you can add the AltTube-dl folder to the PATH environment variable for easy access from anywhere in Windows.

# Using --nostalgia for Low Quality Fun, and how to use Startup Flags
AltTube-dl comes with quite a few startup flags that allow you to quickly download videos and set options using a single command.

1. Go into the folder AltTube-dl.exe is located in.
2. Click on the address bar at the top of the folder window.
3. Type "cmd".
4. Now you can type alttube-dl, then type any startup flag  below

Example: `alttube-dl -save CustomName.mp4`

-h: Shows the help prompt  
--nos, --nostalgia: Allows you to emulate old YouTube by using ffmpeg to lower the video quality after downloading. Takes 144, 240, 360 as options  
--standard: Downloads lower-quality video to significantly increase download speed (**Scroll down and check out the "How to Speed Up Downloads" section**)  
--u, --url: Allows you to put in the URL before the program starts  
--save: Allows you to input the folder name and the name of the video files  
--overwrite: Automatically overwrites existing video file with the same name without asking user  

# How To Speed Up Downloads for Long/Large Videos
Due to the speed of BitView and VidLii's servers, you could experience slow download speeds when downloading more intensive videos. Here's a method to fix that:

**Please note that using the --standard flag will significantly reduce the video/audio quality due to how standard-defnition videos are stored on VidLii's servers.
**If you would like to preserve video/audio quality, don't use --standard.**

1. Go into the folder AltTube-dl.exe is located in.
2. Click on the address bar at the top of the folder window.
3. Type "cmd".
4. Type "alttube-dl --standard". This will download the lower-quality version of the video, which will be faster to download.

# Using AltTube-dl from the Command Prompt
To use bitview-dl from the Command Prompt, you can run the program without any arguments

`alttube-dl.exe` or  
`python alttube-dl.py`

You can also include the video URL, name, and/or video quality straight away. All parameters are optional.

`alttube-dl.exe --url https://www.bitview.net/watch.php?v=kNUlHEYy7rb --save sm64 --nostalgia 240` or  
`alttube-dl.exe --url https://www.vidlii.com/watch?v=2Erf7SW7QkD --save sm64 --nostalgia 240`  

***NOTE: Videos will always be saved as .mp4.***

# Running AltTube-dl.py instead of .exe
Some users may feel more comfortable using an open, easily edited script instead of a .exe file. To run bitview.py, you'll need Python, and some dependencies from PyPI  
  
Dependencies  
Requests  
ffmpeg-python  
colorama
tqdm