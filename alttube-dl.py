from colorama import init, Fore, Style
import requests
import os
import getopt
import sys
from random import choice
from tqdm import tqdm
import ffmpeg
    

class Video:
    def __init__(self, URL, src, location=0):

        self.URL = URL
        self.saveLocation = 0
        self.src = src
        
        if location != 0:
            self.saveLocation = os.path.abspath(location)
            self.name = os.path.basename(self.saveLocation)
            self.saveFolder = os.path.dirname(self.saveLocation)

        siteTuple = ("<title>", "</title>", 'src: "', 'hdsrc: "', '.mp4",')
        restrictedChar = r'/\:*?"<>|'

        srcLink, srcLinkEnd = siteTuple[2], siteTuple[4]
        hdsrcLink, hdsrcLinkEnd = siteTuple[3], siteTuple[4]
        titleStart, titleEnd = siteTuple[0], siteTuple[1]

        ## Downloads webpage using requests library, immediately pulls text attribute. Handles exceptions.
        print("Retrieving webpage...")
        try:
            page = requests.get(URL, allow_redirects=True).text
        except Exception as e:
            print(e, "\n\nAn exception has occurred. Ensure you are pasting a full, valid BitView or VidLii URL, including 'https://www'")
        
        ## Uses string methods to retrieve direct video URL from the page source.
        print("Retrieving direct video URL...")
        try:
            if self.src == "sd":
                raise Exception("notSelected")
            self.sourceURL = self.substringParse(page, hdsrcLink, hdsrcLinkEnd, hdsrc=1)
            check = requests.head(self.sourceURL).status_code

            if check == 404:
                raise Exception("404Error")
        except Exception as e:
            if str(e) == "404Error":
                self.src == "sd"
                print("\nA high quality version of this video does not exist on the server. Fetching standard quality...\n")
            elif str(e) == "notSelected":
                print("HD not selected. Fetching standard quality...")
            else:
                print(e)
            self.sourceURL = self.substringParse(page, srcLink, srcLinkEnd)

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
                    askforOverwrite = input(f"\nWould you like to overwrite this existing file:\n{self.saveLocation}\nType Y or N; or type start to play the existing file. Y/N/start ")
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
        hdMsg = f"\n\n{Fore.GREEN}{Style.BRIGHT}To speed up downloads, try starting Command Prompt, navigating to alttube-dl.py, and typing this:\npython alttube-dl.py --standard\n\
{Fore.YELLOW}The above method increases download speeds, but greatly reduces quality, and is only recommended for long, high quality videos.{Style.RESET_ALL}\n" if self.src == "hd" else ""
        
        print("\nDownloading video...\nVideos may take a few moments to download." + hdMsg)
        
        DLrequest = requests.get(self.sourceURL, stream=True)
        size = int(DLrequest.headers.get("content-length", 0))
        bar = tqdm(total=size, unit="iB", unit_scale=True)
        
        ## Saves video to full path
        with open(self.saveLocation, "wb") as f:
            for chunk in DLrequest.iter_content(1024):
                bar.update(len(chunk))
                f.write(chunk)
        

        ## Uses any non-zero value as variable silent to control when saveFolder is shown. In this case, the quality selection value is used to stop the folder from opening.
        ## The folder will later be opened in ffmpegEdit().
        if not silent:
            os.system(f'{self.folderCommand} "{self.saveFolder}"')

    def substringParse(self, string, start, end, title = 0, hdsrc=0):

        """The substringParse function takes 3 strings, the initial, start, and end,
        then returns the substring that is in between the start and end.

        For example, substringParse("test message stuff", "test", "stuff") will return
        "message".

        The optional title argument changes how the string is trimmed, allowing for the title of a video
        to be pulled from the webpages source code.
        
        The optional hdsrc argument is used while grabbing the HD video link through the page's source code.
        The rfind() method has to be used due to the fact that there are 2 instances of the ".mp4" substring.

        This function is in place to reduce clutter in the __init__ function."""

        start = string.find(start)+len(start)
        
        if not title:
            if not hdsrc:
                end = string.find(end)+len(end)-2
            else:
                end = string.rfind(end)+len(end)-2
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
            print(f"\n{Fore.RED}{Style.BRIGHT}Unable to change quality of video to {quality}p. Make sure ffmpeg.exe is in the same folder as AltTube-dl, or that ffmpeg is in the PATH environment variable.\n\nPress enter to continue.{Style.RESET_ALL}")
            input()
            os.system(f"{self.folderCommand} {self.saveFolder}")
def argParser():

    quality = 0
    location = 0
    overwrite = 0
    silent = 0
    src = "hd"
    sdMsg = ""
    nostalMsg = f"{Fore.GREEN}{Style.BRIGHT}If you want to emulate old YouTube by reducing the video quality, open Command Prompt and type this:\nalttube-dl --nostalgia 240\nYou can select between 144p, 240p, or 360p video qualities and lower bitrates!\nYou can also use --nos instead!\n{Style.RESET_ALL}\n{Fore.GREEN}{Style.BRIGHT}\
Please note that the --nostalgia option will not speed up your video download, try using --standard to switch to standard quality before downloading.\n\nFor more information, type alttube-dl -h or check out the AltTube-dl GitHub{Style.RESET_ALL}"
    options = ["-h", "url=", "save=", "nostalgia=", "overwrite", "standard"]

    arguments, values = getopt.getopt(sys.argv[1:], "hu:s:nos:oh", options)
    if len(sys.argv) > 1:
        for current_arg, current_val in arguments:
            if current_arg in ("-h"):
                info()
            elif current_arg in ("--u", "--url"):
                url = current_val
            elif current_arg == "--save":
                location = current_val
            elif current_arg in ("--nos", "--nostalgia"):
                if any(current_val == i for i in ("144", "240", "360")):
                    quality = current_val
                    nostalMsg = f"Nostalgia video quality activated!\n\nThis video will be saved as {quality}p"
                else:
                    quality = 0
                    nostalMsg = f"{Fore.RED}Invalid nostalgia video quality selected. Only 144p, 240p, and 360p can be selected.\n\nThis video will be saved using default settings.\n"
            elif current_arg == "--overwrite":
                overwrite = 1
            elif current_arg == "--standard":
                src = "sd"
                sdMsg = "\n--standard activated, the video will be downloaded in standard quality."

    print(f"\nAltTube-dl by Dare Developer, v3.1\n\n{Fore.GREEN}{Style.BRIGHT}{nostalMsg}{sdMsg}\n{Style.RESET_ALL}")

    if "url" not in locals():
        url = input("Type a BitView/VidLii link: ")

    inputVid = Video(url, src=src, location=location)
    inputVid.downloadVid(overwrite=overwrite, silent=1 if quality else 0)
    if quality:
        inputVid.ffmpegEdit(quality)

def info():
    vids = ("https://www.bitview.net/watch.php?v=nWqfqRjy4g6", "https://www.vidlii.com/watch?v=8KcI9Tyg_w4")
    vid = choice(vids)
    print(f"""
{Fore.GREEN}{Style.BRIGHT}AltTube-dl allows you to download videos directly from BitView.net and VidLii.com\n
Available, optional startup flags:\n
-h: Opens this help prompt\n
--nostalgia, --nos: Use ffmpeg to reduce the quality of the video after downloading to emulate old YouTube. Takes 144, 240, 360 as valid options.\n
--standard: Speed up downloads of long, high quality videos, automatically tries to download standard-quality version of the video, but the quality of the video will be significantly reduced compared to the high quality version.\n
--url, --u: Specify the URL before the script starts\n
--save: Specify the location to save the file, and the file's name\n
--overwrite: Automatically overwrites files instead of asking\n""")
    input()
    sys.exit(0)

if __name__ == "__main__":
    init()
    argParser()
