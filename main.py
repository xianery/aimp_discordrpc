import pypresence
import requests as rq
import json
import pyaimp
import time

with open('config.json') as file:
    fileData = json.load(file)
    discordClientID = fileData["discordClientAPI"]
    lastfmAPIkey = fileData["lastfmAPIkey"]
    file.close()

try:
    Discord = pypresence.Presence(discordClientID)
    Discord.connect()
    AIMP = pyaimp.Client()
    
    while True:
        try:

            version = str(AIMP.get_version())
            trackInfo = AIMP.get_current_track_info()

            keysLastfm = {
                "method": "track.getInfo",
                "api_key": lastfmAPIkey,
                "artist": trackInfo['artist'],
                "track": trackInfo['title'],
                "format": "json"
            }

            itunesResponse = rq.get(f"https://itunes.apple.com/search?term={trackInfo['artist'].replace(' ', '+')}+{trackInfo['title'].replace(' ', '+')}&limit=1").json()
            lastfmResponse = rq.get("https://ws.audioscrobbler.com/2.0/", params=keysLastfm ).json()

            try:
                albumArt = itunesResponse['results'][0]["artworkUrl100"]
                if itunesResponse['resultCount'] == 0:
                    albumArt = lastfmResponse['track']['album']['image'][1]['#text']
                    if albumArt == "":
                        albumArt = "aimp_logo_noart" 
            except KeyError as _:
                albumArt = "aimp_logo_noart"
            except IndexError as _:
                albumArt = "aimp_logo_noart"

            try:
                if AIMP.get_playback_state() == pyaimp.PlayBackState.Playing:
                    Discord.update(
                        details = f"{trackInfo['title']} by {trackInfo['artist']}",
                        state = "Playing",
                        large_image = albumArt,
                        large_text = trackInfo['album'],
                        small_image = "aimp_ver",
                        small_text = f"AIMP {version[2:6]}"
                    )
                elif AIMP.get_playback_state() == pyaimp.PlayBackState.Paused:
                    Discord.update(
                        details = f"{trackInfo['title']} by {trackInfo['artist']}",
                        state = "Paused",
                        large_image = albumArt,
                        large_text = trackInfo['album'], 
                        small_image = "aimp_ver",
                        small_text = f"AIMP {version[2:6]}"
                    )
                elif AIMP.get_playback_state() == pyaimp.PlayBackState.Stopped:
                    Discord.update(
                        state = "Nothing played",
                        details = "Stopped",
                        large_image = "aimp_logo", # took for random post in AIMP forum
                        small_image = "aimp_ver",
                        small_text = f"AIMP {version[2:6]}"
                    )
            except pypresence.exceptions.ServerError as _:
                continue
                
        except RuntimeError as _:
            print("AIMP doesn't run yet")
            Discord.close()
        
        time.sleep(3)
    
except pypresence.exceptions.DiscordNotFound as _:
    print("Discord is offline")