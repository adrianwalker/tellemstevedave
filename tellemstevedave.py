#!/usr/bin/python

import os.path
import re
import time

import requests


API_URL = "http://api.soundcloud.com"
TRACKS_URL = API_URL + "/users/%(USER_ID)s/tracks" \
                       "?client_id=%(CLIENT_ID)s" \
                       "&limit=%(LIMIT)s" \
                       "&linked_partitioning=true" \
                       "&format=json"
LINKED_URL = "%(NEXT_HREF)s&client_id=%(CLIENT_ID)s"
DOWNLOAD_URL = "https://api.soundcloud.com/tracks/%(TRACK_ID)s/download?client_id=%(CLIENT_ID)s"
DOWNLOAD_PATH = "/media/usb/elements/Music/tesd/"
CHUNK_SIZE = 16 * 1024
TESD_USER_ID = "79299245"
CLIENT_ID = "3b6b877942303cb49ff687b6facb0270"
LIMIT = 10

url = TRACKS_URL % {
    "USER_ID": TESD_USER_ID,
    "CLIENT_ID": CLIENT_ID,
    "LIMIT": LIMIT
}

while True:

    response = requests.get(url).json()

    if response.get("code") == 401:
        time.sleep(3)
        continue

    tracks = response["collection"]

    if not tracks:
        break

    tracks = [(track["id"], track["title"]) for track in tracks]

    for (id, title) in tracks:

        title = str(re.sub('[^A-Za-z0-9]+', '_', title)).strip('_')

        url = DOWNLOAD_URL % {"TRACK_ID": id, "CLIENT_ID": CLIENT_ID}

        filename = DOWNLOAD_PATH + "%s.mp3" % title
        print "downloading: %s from %s" % (filename, url)

        if os.path.exists(filename):
            continue

        request = requests.get(url, stream=True)

        with open(filename + ".tmp", 'wb') as fd:
            chunks = request.iter_content(chunk_size=CHUNK_SIZE)
            for chunk in chunks:
                fd.write(chunk)

        os.rename(filename + ".tmp", filename)

    url = LINKED_URL % {
        "NEXT_HREF": response["next_href"],
        "CLIENT_ID": CLIENT_ID
    }
