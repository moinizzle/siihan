#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from string import punctuation
import sys
import signal
import genius
import artists
import tweepy
import random
import os
import time
import datetime
import re


KEY = ''
SECRET = ''
TOKEN = ''
SECRET_TOKEN = ''
GENIUS_TOKEN = ''


def signal_handler(signum, frame):
    raise(SystemExit)


def time_handler(secs):
    time = datetime.datetime.fromtimestamp(secs)
    formatted = time.strftime(
        '%Mm %Ss'
        ) if secs > float(
            60.00) else str(float(format(secs, '.2f'))) + 's'
    return str(formatted)


def execute():
    signal.signal(signal.SIGINT, signal_handler)
    siihan = Siihan(KEY, SECRET, TOKEN, SECRET_TOKEN)
    account = siihan.validate()

    while(1):

        # fetches all necesary information
        try:
            artist, lyrics = siihan.API_fetch()

        except Exception as e:
            print(e)
            continue

        # find a perfect lyric line to tweet
        # (under 280 characters among other things)
        counter = 0
        random_lyric = random.choice(lyrics)

        if ((len(random_lyric) > 280) or (
            len(random_lyric) == 0)) and (
                counter < 10) or (
                    len(
                        random_lyric.split(" ")
                        ) < 3 or not(
                            re.search(
                                '[a-zA-Z]', random_lyric
                                )
                                ) or '[' and ']' in random_lyric):
            print("[ERROR] " + random_lyric)
            print("changing lyric...")
            continue

        artist = artist.replace("$", "S")
        translator = str.maketrans('', '', punctuation)
        filtered_artist_name = artist.translate(translator)
        filtered_artist_name = filtered_artist_name.replace(" ", "")
        tweet = random_lyric + " #" + filtered_artist_name
        print("[tweeting] " + tweet)

        try:
            siihan.tweet_status(account, tweet)

        except tweepy.TweepError as error:

            if error.api_code == 187:
                print("[DUPLICATE ERROR] " + error.reason)
                print("changing lyric...")
                continue

            else:
                print("[ERROR] " + error.reason)
                raise(SystemExit)

        sleep_time = random.uniform(1, 5)
        time.sleep(sleep_time)


class Siihan():

    def __init__(self, KEY, SECRET, TOKEN, SECRET_TOKEN):
        self._key = KEY
        self._secret = SECRET
        self._token = TOKEN
        self._secret_token = SECRET_TOKEN

    def validate(self):
        validate = tweepy.OAuthHandler(KEY, SECRET)
        validate.set_access_token(TOKEN, SECRET_TOKEN)
        return tweepy.API(validate)

    def delete_file(self, file):
        if os.path.isfile(file):
            os.remove(file)
        else:
            pass

    # function for writing lyrics on after fetching, using Genius API

    def lyrics_writer(self, artist, song):

        song_list = [song]
        filename = "Lyrics_" + artist.name.replace(" ", "") + ".txt"

        with open(filename, 'w') as lyrics_file:
            [lyrics_file.write(s.lyrics + 5*'\n') for s in song_list]

        if not os.path.isfile(filename):
            print("{} does not exist ".format(filename))
            return

        with open(filename) as filehandle:
            lines = filehandle.readlines()

        with open(filename, 'w') as filehandle:
            lines = filter(lambda x: x.strip(), lines)
            filehandle.writelines(lines)

    def tweet_status(self, account, status='test'):
        account.update_status(status)

    def API_fetch(self):
        random_artist = random.choice(tuple(artists.ARTISTS))
        g = genius.Genius(GENIUS_TOKEN)
        artist, artist_id = g.search(random_artist)
        all_songs, all_songs_data = g.get_all_songs(
            artist, artist_id, return_data=True)
        target = random.choice(all_songs_data)
        lyrics = g.get_song_lyrics(target)

        # rare case of internal error (API call returns None)

        if artist and lyrics:
            lyrics = self.parse_lyrics(lyrics)

        else:
            try:
                artist, lyrics = self.API_fetch()
                lyrics = self.parse_lyrics(lyrics)
            except Exception as e:
                print(e)

        return artist, lyrics

    def parse_lyrics(self, lyrics):
        lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
        return lyrics.split("\n")

if __name__ == "__main__":
    begin = time.time()
    try:
        execute()
    except (KeyboardInterrupt, SystemExit):
        finish = time.time() - begin
        print('\ntime elapsed: ' + time_handler(finish))
        print('exiting program...')
        sys.exit(0)
