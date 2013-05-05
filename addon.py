import urllib2
import re
import os
import cgi
from xbmcswift import Plugin, xbmcgui, xbmcplugin

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

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q
    
def play_live_stream():
    stream_url = get_rtmp_url()
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem('Live stream')
    playlist.add(stream_url,listitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)

def fetch_video_info(video_id):
    log("fetch_video_info")
    response = urllib2.urlopen("http://tv.lrytas.lt/?id=" + video_id)
    html = response.read()
    video_url = re.search('href="(http.+mp4)"', html).group(1)
    log(video_url)
    video_title = re.search('<h1[^>]*>([^<]+)</h1>', html).group(1)
    log(video_title)
    return video_url, video_title
    
def play_video(video_id):
    video_url, video_title = fetch_video_info(video_id)
    listitem = xbmcgui.ListItem(label=video_title, iconImage='', thumbnailImage='', path=video_url)

    log("Playing video: " + video_title + " - " + video_id + " - " + video_url)

    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

if __name__ == '__main__':
    plugin_query = plugin_queries = parse_query(sys.argv[2][1:])
    if plugin_query['mode'] == 'play_video':
        play_video(plugin_query['videoid'])
    else:
        play_live_stream()