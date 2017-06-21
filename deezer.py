from __future__ import unicode_literals
import requests
import json
# import webbrowser
from bs4 import BeautifulSoup
import youtube_dl
from mutagen.easyid3 import EasyID3
import os
# import sys
import logging
from optparse import OptionParser

logging.basicConfig(filename='deezer.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filemode='w')
logging.info('Deezer.py logs')

parser = OptionParser()
parser.add_option("-c", "--account", dest="account_id",
                  help="deezer account id", metavar="DEEZER_ACCOUNT_ID")
parser.add_option("-o", "--output", dest="output_dir",
                  help="output dir", metavar="OUTPUT_DIR")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
(options, args) = parser.parse_args()

print("account id = " + str(options.account_id))
print("output dir = " + str(options.output_dir))

# user_id = "1"
# (olivier)
user_id = "5912706"
# user_id = "1276017244" (delphine commun)
dir = "download"
if options.account_id is not None:
    user_id = str(options.account_id)
if options.output_dir is not None:
    dir = str(options.output_dir)

base_url = "http://api.deezer.com"
proxy = {"http": "http://p-goodway.rd.francetelecom.fr:3128", "https": "http://p-goodway.rd.francetelecom.fr:3128"}
session = requests.Session()
session.trust_env = False

nb_playlists = 0

print("Deezer user id is " + user_id)
logging.info("Deezer user id is " + user_id)

# new = 2
# webbrowser.open(auth_url, new=new)

### hook and logger for youtube_dl
def YtdlHook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading, now converting ... {}".format(file_tuple[1]))
        logging.info("Done downloading, now converting ... {}".format(file_tuple[1]))

        # pathToMp3File = os.path.abspath(d['filename'])
        # print("Update file metadata : " + pathToMp3File)
        # metatag = EasyID3(pathToMp3File)
        # metatag['title'] = "Song Title"
        # metatag['artist'] = "Song Artist"
        # metatag.RegisterTextKey("track", "TRCK")
        # metatag['track'] = 7
        # metatag.save()

    if d['status'] == 'downloading':
        print(d['filename'], d['_percent_str'], d['_eta_str'])

class YtdlLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        logging.error(msg)

### download mp3 from youtube url
def downloadMp3(yt_url, folder, title, author):
    print("*** download mp3 " + yt_url + " for playlist '" + folder + "'")
    logging.info("*** download mp3 " + yt_url + " for playlist " + folder)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }, {
            'key': 'FFmpegMetadata'
        }],
        'addmetadata': True,
        'metafromtitle': '%(artist)s - %(title)s',
        'embedthumbnail' : True,
        'quiet': True,
        'verbose': False,
        'restrictfilenames': True,
        'prefer_ffmpeg': True,
        'ffmpeg_location': 'C:\\ffmpeg',
        'outtmpl': dir+'\\'+folder+'\\%(title)s.%(ext)s',
        'logger': YtdlLogger(),
        'progress_hooks': [YtdlHook],
        'ignoreerrors': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

### search on youtube
def searchOnYoutube(title, author, folder):
    youtube_url = "https://www.youtube.com/results?search_query="
    print("*** search on youtube " + youtube_url + title + " " + author)
    logging.info("*** search on youtube " + youtube_url + title + " " + author)
    r = session.get(youtube_url + title + " " + author, proxies=proxy)
    # r = session.get(youtube_url + title + " " + author)
    soup = BeautifulSoup(r.text, "html.parser")
    # print("response = " + r.text)
    v = 0
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        if v == 0:
            yt_url = 'https://www.youtube.com' + vid['href']
            downloadMp3(yt_url, folder, title, author)
            # webbrowser.open(yt_url, new=new)
        # print('https://www.youtube.com' + vid['href'])
        v = v + 1

### get playlist songs
def getPlaylistSongs(playlist_id, playlist_name):
    id = str(playlist_id)
    playlist_url = base_url + "/playlist/" + id
    print("*** get songs for playlist " + id)
    logging.info("*** get songs for playlist " + id)
    r = session.get(playlist_url, proxies=proxy)
    # r = session.get(playlist_url)
    # print("response = " + r.text)
    playlist = json.loads(r.text)
    n = len(playlist['tracks']['data'])
    for i in range(0, n):
        # print(playlist['tracks']['data'][i])
        title = playlist['tracks']['data'][i]['title']
        print("------ song " + str(i+1) + "/" + str(n) + " : " + title)
        logging.info("------ song " + str(i+1) + "/" + str(n) + " : " + title)
        author = playlist['tracks']['data'][i]['artist']['name']
        # print(author)
        searchOnYoutube(title, author, playlist_name)
        break;

### ask user playlists (me=5912706)
def askUserPlaylist(user_id):
    global nb_playlists
    user_playlists_url = base_url + "/user/" + user_id + "/playlists/"
    print("*** ask playlist for user " + user_id)
    logging.info("*** ask playlist for user " + user_id)
    r = session.get(user_playlists_url, proxies=proxy)
    # r = session.get(user_playlists_url)
    # print("response = " + r.text)
    playlists = json.loads(r.text)
    print(playlists['data'][0]['id'])
    nb_playlists = len(playlists['data'])
    print("Number of playlists = " + str(nb_playlists))
    logging.info("Number of playlists = " + str(nb_playlists))
    for i in range(0, len(playlists['data'])):
        playlist_id = playlists['data'][i]['id']
        print("+++ playlist : " + str(playlist_id))
        playlist_name = playlists['data'][i]['title']
        print("-------------- Getting songs for playlist '" + playlist_name + "' " + str(i+1) + "/" + str(nb_playlists))
        logging.info("-------------- Getting songs for playlist '" + playlist_name + "' " + str(i+1) + "/" + str(nb_playlists))
        getPlaylistSongs(playlist_id, playlist_name)
        break;

askUserPlaylist(user_id)

