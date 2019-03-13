import os.path
import re
import requests

API_URL = "http://api.soundcloud.com"
TRACKS_URL = API_URL + "/users/%(USER_ID)s/tracks" \
                       "?client_id=%(CLIENT_ID)s" \
                       "&offset=%(OFFSET)s" \
                       "&limit=%(LIMIT)s" \
                       "&format=json"
DOWNLOAD_URL = "https://api.soundcloud.com/tracks/%(TRACK_ID)s/download?client_id=%(CLIENT_ID)s"
CHUNK_SIZE = 16 * 1024
TESD_USER_ID = "79299245"
CLIENT_ID = "3b6b877942303cb49ff687b6facb0270"
LIMIT = 10
offset = 0

while True:

    url = TRACKS_URL % {
        "USER_ID": TESD_USER_ID,
        "CLIENT_ID": CLIENT_ID,
        "LIMIT": LIMIT,
        "OFFSET": offset
    }

    tracks = requests.get(url).json()

    if not tracks:
        break

    tracks = [(track["id"], track["title"]) for track in tracks]

    for (id, title) in tracks:

        title = str(re.sub('[^A-Za-z0-9]+', '_', title)).strip('_')
        
        url = DOWNLOAD_URL % {"TRACK_ID": id, "CLIENT_ID": CLIENT_ID}

        filename = "%s.mp3" % title
        print "downloading: %s from %s" % (filename, url)

        if os.path.exists(filename):
            continue;

        request = requests.get(url, stream=True)

        with open(filename + ".tmp", 'wb') as fd:
            chunks = request.iter_content(chunk_size=CHUNK_SIZE)
            for chunk in chunks:
                fd.write(chunk)
                
        os.rename(filename + ".tmp", filename)

    offset = offset + LIMIT
