# py.deezer
## Installation (only for Windows at this step)
- your playlists must be public on deezer
- install Python 3 from https://www.python.org/downloads/windows/ (check the box "add to windows path")
- download FFMPEG (https://ffmpeg.zeranoe.com/builds/) and put ./bin content in C:\\ffmpeg
- execute 'python deezer.py -o download -c [your deezer id] (your id is 123456 in http://www.deezer.com/profile/123456 when you click on your Deezer profile)
- it will search music clip on Youtube and get mp3 file from it in 'download' directory

## Code
Needs Python modules : requests, BeatutifulSoup from bs4, json and youtude_dl
