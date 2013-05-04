import urllib2
import re
import os
from xbmcswift import Plugin, xbmcgui

plugin = Plugin('Lrytas.lt', 'plugin.video.lrytas', __file__)
                              
def get_rtmp_url():
    response = urllib2.urlopen("http://tv.lrytas.lt/live")
    html = response.read()
    rtmp = re.search('href="(rtmp.+live)"', html).group(1)
    # rtmp = 'rtmp://live.lrtc.lt:80/X8a7MmK/live'
    log('stream: ' + rtmp)
    return rtmp

def log(msg):
    xbmc.log('%s addon: %s' % ('lrytas.lt', msg))
    
def play_live_stream():
    stream_url = get_rtmp_url()
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem('Live stream')
    playlist.add(stream_url,listitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

if __name__ == '__main__':
    play_live_stream()
