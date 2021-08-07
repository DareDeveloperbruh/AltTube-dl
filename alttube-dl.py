from colorama import init, Fore, Style
import ffmpeg
import requests
import os
import getopt
import sys
from random import choice

class Video:
    def __init__(self, URL, location=0) -> str:

        self.URL = URL
        self.saveLocation = 0
        
        if location != 0:
            self.saveLocation = os.path.abspath(location)
            self.name = os.path.basename(self.saveLocation)
            self.saveFolder = os.path.dirname(self.saveLocation)

        siteTuple = ("<title>", "</title>", 'src: "', ".mp4")
        restrictedChar = r'/\:*?"<>|'

        linkStart, linkEnd = siteTuple[2], siteTuple[3]
        titleStart, titleEnd = siteTuple[0], siteTuple[1]

        ## Downloads webpage using requests library, immediately pulls text attribute. Handles exceptions.
        print("Retrieving webpage...")
        try:
            page = requests.get(URL, allow_redirects=True).text
        except Exception as e:
            print(e, "\n\nAn exception has occurred. Ensure you are pasting a full, valid BitView or VidLii URL, including 'https://www'")
        
        ## Uses string methods to retrieve direct video URL from the page source.
        print("Retrieving direct video URL...")
        self.sourceURL = self.substringParse(page, linkStart, linkEnd)
        print("Source URL: " + self.sourceURL)

        ## Uses same method for title, but uses str.translate() to remove invalid characters.
        if not self.saveLocation:
            print("Retrieving video name...")
            self.name = self.substringParse(page, titleStart, titleEnd, 1).translate({ord(i):None for i in restrictedChar})
        
    def downloadVid(self, overwrite=0, silent=0):
    
        ## OSDict establishes which os.system() command is used to show the saveFolder location.
        OSDict = {
            "nt": ("USERPROFILE", "explorer"),
            "posix": ("HOME", "xdg-open")
        }
        self.folderCommand = OSDict[os.name][1]
        
        ## Establishes location of AltTube-Downloads folder, not full video path, if location was not already specified with startup flags.
        if not self.saveLocation:
            env = os.getenv(OSDict[os.name][0])
            self.saveFolder = os.path.join(env, "Videos", "AltTube-Downloads")
            if self.saveFolder != os.getcwd() and not os.path.exists(self.saveFolder):
                os.makedirs(self.saveFolder)
            
            self.saveLocation = os.path.join(self.saveFolder, f"{self.name}.mp4")
            
        ## Checks if video already exists
        if os.path.exists(self.saveLocation) and not overwrite:
                while 1:
                    askforOverwrite = input(f"\n\nWould you like to overwrite this existing file:\n{self.saveLocation}\nType Y or N; or type start to play the existing file. Y/N/start ")
                    if askforOverwrite.lower() == "y":
                        break
                    elif askforOverwrite.lower() == "n":
                        newName = input("Input a new file name: ").replace(".mp4", "")
                        if not os.path.exists(os.path.dirname(self.saveLocation) + newName):
                            self.saveLocation = os.path.join(self.saveFolder, f"{newName}.mp4")
                            self.name = f"{newName}.mp4"
                            break
                        else:
                            continue
                    elif askforOverwrite.lower() == "start":
                        os.system(f"{self.folderCommand} {self.saveLocation}")
                        continue
                    else:
                        continue
                        
        ## Downloads video from direct video URL
        print("Downloading video...\nVideos may take around 1-10 seconds to download.")
        DLrequest = requests.get(self.sourceURL, allow_redirects=True)
        print("Downloaded!")


        
        
        ## Saves video to full path
        with open(self.saveLocation, "wb") as f:
                print(f"Saving to {self.saveLocation}")
                f.write(DLrequest.content)

        ## Uses any non-zero value as variable silent to control when saveFolder is shown. In this case, the quality selection value is used to stop the folder from opening.
        ## The folder will later be opened in ffmpegEdit().
        if not silent:
            os.system(f'{self.folderCommand} "{self.saveFolder}"')

    def substringParse(self, string, start, end, title = 0):

        """The substringParse function takes 3 strings, the initial, start, and end,
        then returns the substring that is in between the start and end.

        For example, substringParse("test message stuff", "test", "stuff") will return
        "message".

        The optional title argument changes how the string is trimmed, allowing for the title of a video
        to be pulled from the webpages source code.

        This function is in place to reduce clutter in the __init__ function."""

        start = string.find(start)+len(start)
        
        if not title:
            end = string.find(end)+len(end)
        else:
            end = string.find(end)
        
        return string[start:end]

    def ffmpegEdit(self, quality):

        self.qualityInfo = {
            "144": ("30k", "50k"),
            "240": ("40k", "55k"),
            "360": ("45k", "60k")
        }
        
        print(f"Changing video quality to {quality}p with ffmpeg.")
        nostalName = os.path.join(self.saveFolder, f"{self.name} - {quality}p.mp4")
        
        vbit = self.qualityInfo[quality][0]
        abit = self.qualityInfo[quality][1]

        stream = ffmpeg.input(self.saveLocation)
        stream = ffmpeg.filter(stream, "scale", -2, quality)
        stream = ffmpeg.output(stream, nostalName, map="0:a", video_bitrate=vbit, audio_bitrate=abit, preset="veryfast")
        stream = ffmpeg.overwrite_output(stream)
        try:
            ffmpeg.run(stream)
        except FileNotFoundError:
            print(f"\n{Fore.RED}{Style.BRIGHT}Unable to change quality of video to {quality}p. Make sure ffmpeg is in the PATH environment variable, or that it is in the current folder.\n\nFor a tutorial on how to add ffmpeg and AltTube-dl to PATH for easier access, check out the AltTube-dl GitHub page.\n\nPress enter to continue.{Style.RESET_ALL}")
            input()
            os.system(f"{self.folderCommand} {self.saveFolder}")
def argParser():

    quality = 0
    location = 0
    overwrite = 0
    silent = 0
    nostalMsg = f"{Fore.GREEN}{Style.BRIGHT}To get that sweet, low quality nostalgia, open Command Prompt and type this:\nalttube-dl --nostalgia 240\nYou can select between 144p, 240p, or 360p video qualities and lower bitrates!\n{Style.RESET_ALL}\n{Fore.GREEN}{Style.BRIGHT}For more information, type alttube-dl -h into Command Prompt, or check out the AltTube-dl GitHub page. {Style.RESET_ALL}\n"
    options = ["-h", "url=", "save=", "nostalgia=", "overwrite"]

    arguments, values = getopt.getopt(sys.argv[1:], "hu:s:nos:o", options)
    if len(sys.argv) > 1:
        for current_arg, current_val in arguments:
            print(current_arg, current_val)
            if current_arg in ("-h"):
                info()
            elif current_arg in ("-u", "--url"):
                url = current_val
            elif current_arg in ("--save"):
                location = current_val
            elif current_arg in ("-nos", "--nostalgia"):
                if current_val in ("144", "240", "360"):
                    quality = current_val
                    nostalMsg = f"{Fore.GREEN}{Style.BRIGHT}Nostalgia video quality activated!\n\nThis video will be saved as {quality}p{Style.RESET_ALL}\n"
                else:
                    quality = 0
                    nostalMsg = f"{Fore.RED}{Style.BRIGHT}Invalid nostalgia video quality selected. Only 144p, 240p, and 360p can be selected.\n\nThis video will be saved using default settings.{Style.RESET_ALL}\n"
            elif current_arg in ("--overwrite"):
                overwrite = 1

    print(f"AltTube-dl by Dare Developer, v3.0\n\n{nostalMsg}")

    if "url" not in locals():
        url = input("Type a URL: ")

    inputVid = Video(url, location=location)
    inputVid.downloadVid(overwrite=overwrite, silent=1 if quality else 0)
    if quality:
        inputVid.ffmpegEdit(quality)

def info():
    vids = ("https://www.bitview.net/watch.php?v=nWqfqRjy4g6", "https://www.vidlii.com/watch?v=8KcI9Tyg_w4")
    vid = choice(vids)
    print(f"""
{Fore.GREEN}{Style.BRIGHT}AltTube-dl allows for users to download videos directly from bitview.net\n\nTo use AltTube-dl, double click alttube-dl.exe or run python alttube-dl.py. You can give the video link in the same command, or start without one.\n
Examples:\nalttube-dl.exe -h (Opens this info prompt)\n
python alttube-dl.py -h (Opens this info prompt)\n
alttube-dl.exe --url  --save test.mp4 (Best usage for this scenario: Add AltTube-dl to PATH variable.)\n
python alttube-dl.py --url {vid} --save bruh.mp4 (Best usage for this scenario: Add AltTube-dl to PATH variable.)\n
alttube-dl.exe --nostalgia 240p (Nostalgia function: Saves video in 144p, 240p, 360p, 480p)\n
python alttube-dl.py --nostalgia 240p (Nostalgia function: Saves video in 144p, 240p, 360p, 480p)\n
alttube-dl.exe --overwrite (This will automatically overwrite any video. You can use this with the --save option to quickly download videos and save them with a certain name."\n
NOTE: Files are downloaded directly from BitView and VidLii, they will always be saved as .mp4.""")
    input()
    sys.exit(0)

if __name__ == "__main__":
    init()
    argParser()
