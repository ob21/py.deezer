from __future__ import unicode_literals
import requests
import json
import webbrowser
from bs4 import BeautifulSoup
import youtube_dl
import os
import sys

session = requests.Session()
session.trust_env = False

user_id="5912706"

base_url = "http://api.deezer.com"

proxy = {"http": "http://p-goodway.rd.francetelecom.fr:3128", "https": "http://p-goodway.rd.francetelecom.fr:3128"}

new = 2
# webbrowser.open(auth_url, new=new)

### download mp3 from youtube url
def downloadMp3(yt_url, folder):
    print("*** download mp3 " + yt_url)
    # sys.path.append("C:\\ffmpeg")
    # print(os.getenv('PATH'))
    # print(sys.path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'verbose': False,
        'restrictfilenames': True,
        'prefer_ffmpeg': True,
        'ffmpeg_location': 'C:\\ffmpeg',
        'outtmpl': folder+'\\%(title)s.%(ext)s'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

### search on youtube
def searchOnYoutube(title, author, folder):
    youtube_url = "https://www.youtube.com/results?search_query="
    print("*** get on youtube " + youtube_url + title + " " + author)
    r = session.get(youtube_url + title + " " + author, proxies=proxy)
    # r = session.get(youtube_url + title + " " + author)
    soup = BeautifulSoup(r.text, "html.parser")
    # print("response = " + r.text)
    v = 0
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        if v == 0:
            yt_url = 'https://www.youtube.com' + vid['href']
            downloadMp3(yt_url, folder)
            # webbrowser.open(yt_url, new=new)
        # print('https://www.youtube.com' + vid['href'])
        v = v + 1

### get playlist songs
def getPlaylistSongs(playlist_id, playlist_name):
    id = str(playlist_id)
    playlist_url = base_url + "/playlist/" + id
    print("*** get songs for playlist " + id + " playlist : " + playlist_url)
    r = session.get(playlist_url, proxies=proxy)
    # r = session.get(playlist_url)
    print("response = " + r.text)
    playlist = json.loads(r.text)
    i = 1
    for i in range(0, len(playlist['tracks']['data'])):
        # print(playlist['tracks']['data'][i])
        title = playlist['tracks']['data'][i]['title']
        print("--- song : " + title)
        author = playlist['tracks']['data'][i]['artist']['name']
        # print(author)
        searchOnYoutube(title, author, playlist_name)

### ask user playlists (me=5912706)
def askUserPlaylist(user_id):
    user_playlists_url = base_url + "/user/" + user_id + "/playlists/"
    print("*** get playlist for user " + user_id + " playlists : "+user_playlists_url)
    r = session.get(user_playlists_url, proxies=proxy)
    # r = session.get(user_playlists_url)
    print("response = " + r.text)
    playlists = json.loads(r.text)
    # print(playlists['data'][0]['id'])
    for i in range(0, len(playlists['data'])):
        playlist_id = playlists['data'][i]['id']
        print("+++ playlist : " + str(playlist_id))
        getPlaylistSongs(playlist_id, playlists['data'][i]['title'])

askUserPlaylist(user_id)

