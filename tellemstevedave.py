#!/usr/bin/python3

import os.path
import re
import time

import requests


API_URL = "https://api-widget.soundcloud.com"
TRACKS_URL = API_URL + "/users/%(USER_ID)s/tracks" \
                       "?client_id=%(CLIENT_ID)s" \
                       "&limit=%(LIMIT)s" \
                       "&linked_partitioning=true" \
                       "&format=json"
LINKED_URL = "%(NEXT_HREF)s&client_id=%(CLIENT_ID)s"
DOWNLOAD_URL = API_URL + "/tracks/%(TRACK_ID)s/download?client_id=%(CLIENT_ID)s"
DOWNLOAD_PATH = "/media/usb/elements/Music/tesd/"
CHUNK_SIZE = 16 * 1024
TESD_USER_ID = "79299245"
CLIENT_ID = "LBCcHmRB8XSStWL6wKH2HPACspQlXg2P"
LIMIT = 10
BACKOFF_SECONDS =  [2, 4, 8, 16]

url = TRACKS_URL % {
    "USER_ID": TESD_USER_ID,
    "CLIENT_ID": CLIENT_ID,
    "LIMIT": LIMIT
}

def request_retry(url, stream=False):
    
    for backoffSeconds in BACKOFF_SECONDS:
        response = requests.get(url, stream=stream)
        
        if response.status_code == 200:
            break
        
        time.sleep(backoffSeconds)
        
    if stream:
        return response
    
    return response.json()
    

while True:
       
    response = request_retry(url)
    tracks = response["collection"]
    nextHref = response["next_href"]

    if not tracks:
        break

    tracks = [(track["id"], track["title"]) for track in tracks]

    for (id, title) in tracks:

        title = str(re.sub('[^A-Za-z0-9]+', '_', title)).strip('_')

        filename = DOWNLOAD_PATH + "%s.mp3" % title
        print ("downloading: %s from %s" % (filename, url))

        if os.path.exists(filename):
            continue

        url = DOWNLOAD_URL % {"TRACK_ID": id, "CLIENT_ID": CLIENT_ID}

        response = request_retry(url)
        url = response['redirectUri']

        response = request_retry(url, stream=True)

        with open(filename + ".tmp", 'wb') as fd:
            chunks = response.iter_content(chunk_size=CHUNK_SIZE)
            for chunk in chunks:
                fd.write(chunk)

        os.rename(filename + ".tmp", filename)

    url = LINKED_URL % {
        "NEXT_HREF": nextHref,
        "CLIENT_ID": CLIENT_ID
    }
