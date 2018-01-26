#!/usr/bin/env python3
#
# částečně inspirováno ctsream od petr_p

__author__ = "Jakub Lužný"
__desc__ = "ČT (iVysílání)"
__url__ = r"https?://www\.ceskatelevize\.cz/(porady|ivysilani)/.+"

import re,os.path, urllib.request, urllib.parse, json, http.cookiejar, logging
from collections import OrderedDict
import json
from urllib.parse import urlparse, unquote

log = logging.getLogger()

urlopen = urllib.request.urlopen

def flatten(obj, prefix = ''):
    out = []
#  print(prefix)
    if type(obj) == dict:
        for key in obj:
            out+= flatten(obj[key], prefix+"[{}]".format(key) )

    elif type(obj) == list:
        for i in range(0, len(obj)):
            out+= flatten(obj[i], prefix+'[{}]'.format(i) )

    else:
        out.append( (prefix, obj) )

    return out
    
def srt_time(time):
    time = int(time)
    sec = time / 1000
    msec = time % 1000
    hour = sec / 3600
    sec = sec % 3600
    min = sec / 60
    sec = sec % 60
    return "{:02}:{:02}:{:02},{:03}".format(int(hour), int(min), int(sec), msec)
    
def txt_to_srt(txt):
    subs = re.findall('\s*(\d+); (\d+) (\d+)\n(.+?)\n\n', txt, re.DOTALL)
    srt = ''
    for s in subs:
        srt += "{}\n{} --> {}\n{}\n\n".format(s[0], srt_time(s[1]), srt_time(s[2]), s[3] )
    
    return srt

class CtEngine:

    def __init__(self, url):
        url = url.replace('/porady/', '/ivysilani/').replace('/video/', '')
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener.addheaders = [
            ('User-agent', 'Mozilla/5.0'),
            ('x-addr', '127.0.0.1'),
            ('Referer', url)
        ]
        urllib.request.install_opener(self.opener)
        
        self.b_page = urlopen(url).read()  # .decode('utf-8')

        #get playlist URL first
        data = re.findall(b"getPlaylistUrl\((.+?]), request", self.b_page)[0]
        data = data.decode('utf-8')
        data = json.loads(data)
        data = data[0]        
        data = {
            'playlist[0][type]' : data['type'],
            'playlist[0][id]' : data['id'],
            'requestUrl' : urlparse(url).path,
            'requestSource' : 'iVysilani'
        }
        data = urllib.parse.urlencode( data, 'utf-8')
        header = { 
            "Content-type": "application/x-www-form-urlencoded"        
        }
        req = urllib.request.Request('http://www.ceskatelevize.cz/ivysilani/ajax/get-client-playlist', bytes(data, 'utf-8'), header )
        data = json.loads(urlopen(req).read().decode('utf-8'))
        url = urllib.parse.unquote(data['url'])
                
        self.getPlaylist(url)
        self.getMovie()
        self.getStreams()

        if len(self.streams) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')
        
    def getPlaylist(self, playlistUrl):
        rawData = urlopen(playlistUrl).read().decode('utf-8')
        self.playlist = json.loads(rawData, 'utf-8')

    def getMovie(self):
        self.movie = self.playlist['playlist'][0]
        
        self.subtitles = None # TODO

    def getStreams(self):
        rawStreams = urlopen(self.movie['streamUrls']['main']).read().decode('utf-8')
        lines = rawStreams.rstrip().split('\n')

        bandwidthsRaw = list(filter(lambda s: str.startswith(s, '#') and s.find('BANDWIDTH=') != -1, lines[1:]))
        streams = list(filter(lambda s: not str.startswith(s, '#'), lines))

        bandwidths = [re.sub(r'^.*BANDWIDTH=([0-9]+)[^0-9]?.*$', '\\1', b) for b in bandwidthsRaw]
        qualityMap = {'500000': '288p', '1032000': '404p', '2048000': '576p', '3584000': '720p', '628000': '288p', '1160000': '404p', '2176000': '576p', '3712000': '720p'}
        qualities = [qualityMap[b] for b in bandwidths]

        self.streams = OrderedDict(zip(qualities, streams))

    def qualities(self):
        return list(zip(self.streams.keys(), self.streams.keys())) + ([('srt', 'Titulky')] if self.subtitles is not None else [])
      
    def movies(self):        
        return [ ('0', self.movie['title']) ]

    def get_video(self, quality):
        if not quality in self.streams:
            raise ValueError('Není k dispozici zadaná kvalita videa.')
    
        log.info('Vybraná kvalita: {}'.format(quality))
        return self.streams[quality]
                
    def download(self, quality, movie):
        if quality == 'srt':
            return self.download_srt()
        if quality:
            video = self.get_video(quality)
        else:
            bestQuality = list(self.streams.keys())[-1]
            video = self.streams[bestQuality]
            log.info('Automaticky vybraná kvalita: {}.'.format(bestQuality))

        filename =  self.movie['title'] + '.mp4'
        urlParts = self.getVideoParts(video)
        return ('http', filename, {'url': urlParts})
        
    def getVideoParts(self, video):
        return list(filter(lambda s: not str.startswith(s, '#'), urlopen(video).read().decode('utf-8').rstrip().split('\n')))

    def download_srt(self): #TODO
        if self.subtitles is None:
            raise ValueError('Titulky nejsou k dispozici.')
        
        txt = urllib.request.urlopen(self.subtitles).read().decode('utf8')
        srt = txt_to_srt(txt)
        return ('text', 'subtitles.srt', srt.encode('cp1250') )
        
