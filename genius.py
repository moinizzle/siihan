#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import json
import requests
import time
from bs4 import BeautifulSoup as bs
import os
import artists

API_URL = 'https://api.genius.com/'
WEB_URL = "https://genius.com/api/"
SLEEP = 3


class Genius():

    def __init__(self, GENIUS_TOKEN):
        self._sleep = SLEEP
        self._api = API_URL
        self._web = WEB_URL
        self._access_token = GENIUS_TOKEN
        self._session = requests.Session()
        self._session.headers = {
            'Authorization': 'Bearer ' + self._access_token}

    def search(self, artist_name, page=1, per_page=5):
        artists = list()
        artists_data = list()
        payload = {'per_page': per_page, 'page': page, 'q': artist_name}
        url = WEB_URL + 'search/multi?'
        api_response = requests.get(url, params=payload, timeout=SLEEP)
        json_data = api_response.json(
            ) if api_response and api_response.status_code == 200 else None

        if json_data is not None:
            for n in json_data['response']['sections']:
                for hit in n['hits']:
                    if hit['result']['_type'] == 'artist':
                        artists_data.append(hit['result'])
                        artists.append(hit['result']['name'])
            artist, artist_id = artists_data[0]['name'], artists_data[0]['id']
            return artist, artist_id
        else:
            return api_response.status_code

    def search_song(self, artist_name, artist_id, page=1, per_page=20):

        '''returns top 20 songs stored in the genius databse, given artist name
        '''
        songs = list()
        songs_data = list()
        url = API_URL + 'search?'
        payload = {
            'q': artist_name,
            'sort': 'popularity',
            'per_page': per_page,
            'page': page}
        api_response = self._session.request(
            'GET', url, params=payload, timeout=SLEEP)
        json_data = api_response.json(
            ) if api_response and api_response.status_code == 200 else None

        if json_data is not None:
            for hits in json_data['response']['hits']:
                if hits['type'] == 'song':
                    song_name = hits['result']['title']
                    primary_artist_id = hits['result']['primary_artist']['id']
                    if (
                        any(
                            x in song_name.lower(
                                ) for x in artists.SKIP
                                ) is False
                                ) and (artist_id == primary_artist_id):
                        songs_data.append(hits['result'])
                        songs.append(song_name)
            return songs, songs_data
        else:
            return api_response.status_code

    def get_all_songs(self, artist_name, artist_id, return_data=False):
        '''returns approximately 100 songs from Genius database (or less)
        '''

        all_songs = list()
        all_songs_data = list()

        for i in range(1, 6):
            songs, song_data = self.search_song(artist_name, artist_id, page=i)
            all_songs += songs
            all_songs_data += song_data

        if return_data:
            return all_songs, all_songs_data

        else:
            return all_songs

    def get_song_lyrics(self, song_data):

        url = song_data['url']
        lyrics_page = requests.get(url)
        lyrics_page_html = bs(
            lyrics_page.content, 'html.parser'
            ) if lyrics_page.status_code == 200 else None

        if lyrics_page_html:
            lyrics = lyrics_page_html.find("div", {"class": "lyrics"})
            return lyrics.get_text()
