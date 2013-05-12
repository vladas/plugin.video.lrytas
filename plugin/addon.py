#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, re, json
import os, cgi
# import traceback
import xml.etree.ElementTree as ET
from xbmcswift2 import Plugin, xbmcgui, xbmcplugin

plugin = Plugin('Lrytas.lt', 'plugin.video.lrytas', __file__)

STRINGS = {
    'live': 30000,
    'tv_shows': 30001,
}

### Routing

@plugin.route('/')
def show_root():
    on_air = get_on_air()
    items = [
        {'label': _('live') + ": " + on_air,
         'path': get_rtmp_url() + ' live=true',
         'is_playable': True},
        {'label': _('tv_shows'),
         'path': plugin.url_for('show_tv_shows')},
    ]
    return plugin.finish(items)
    
@plugin.route('/watch_live')
def watch_live():
    on_air = get_on_air()
    item =  {
        'label': _('live') + ": " + on_air,
        'path': stream_url + ' live=true',
        'is_playable': True,
    }
    return plugin.play_video(item)
    
@plugin.route('/show_tv_shows')
def show_tv_shows():
    log("Show TV Shows start")
    themes_and_clips = load_cached_themes()
    log("themes and clips loaded")
    return __list_themes(themes_and_clips)
    
@plugin.route('/show_theme_videos/<themeId>')
def show_theme_videos(themeId):
    themes_and_clips = load_cached_themes()
    log('show_theme_videos: after load')
    videos = []
    if themes_and_clips.has_key(themeId):
        videos = themes_and_clips[themeId]['clips']
        
    return __list_videos(videos)

@plugin.route('/play_video/<videoId>')
def show_play_video(videoId):
    log('show_play_video')
    play_video(videoId)
    # 
    # video_url, video_title, img_id = fetch_video_info(videoId)
    # log('after fetch video')
    # log(video_url)
    # log(img_id)
    # item =  {
    #     'label': video_title,
    #     'path': video_url,
    #     'thumbnail': get_img_src(img_id),
    #     'is_playable': True,
    # }
    # log('item')
    # # log(item)
    # return plugin.play_video(item)
    
@plugin.route('/play_video_url/<url>')
def show_play_video_url(url):
    items = []
    return plugin.finish(items)
    
    
@plugin.cached(TTL=60)
def fetch_cached_video_info(videoId):
    log('fetch_cached_video_info')
    return fetch_video_info(videoId)

@plugin.cached(TTL=10)
def load_cached_themes():
    log('load_cached_themes')
    return load_themes()

### Helper functions

def get_rtmp_url():
    response = urllib2.urlopen("http://tv.lrytas.lt/live")
    html = response.read()
    rtmp = re.search('href="(rtmp.+live)"', html).group(1)
    log('stream: ' + rtmp)
    return rtmp

def get_on_air():
    response = urllib2.urlopen("http://tv.lrytas.lt/tvvideonews/tv_curr.asp?n=")
    json_str = response.read()
    
    live_info = json.loads(json_str)
    
    try:
        return live_info['s'][0]['PAVADINIMAS']
    except:
        log('Couldn\'t fetch on_air info')
        return ''

def log(msg):
    xbmc.log(u'%s addon: %s' % ('lrytas.lt', msg))

def _(string_id):
    if string_id in STRINGS:
        return plugin.get_string(STRINGS[string_id])
    else:
        plugin.log.warning('String is missing: %s' % string_id)
        return string_id

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
    # TODO load on-air info
    listitem = xbmcgui.ListItem('Live stream')
    playlist.add(stream_url,listitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playlist)
    
def play_video(video_id):
    log("play_video")
    video_url, video_title, img_id = fetch_cached_video_info(video_id)
    img_src = get_img_src(img_id)
    listitem = xbmcgui.ListItem(label="title", iconImage='', thumbnailImage=img_src, path=video_url)

    #log("Playing video: " + video_id + " - " + video_url + " - " + img_src)

    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
    
def __list_videos(videos):
    items = []
        
    for video in videos:
        item = {
            'label': video['title'],
            'path': video['videoSrc'],
            'thumbnail': video['imgSrc'],
            'is_playable': True,
            'info': {
                'date': video['date']
            },
        }
        items.append(item)

    finish_kwargs = {
        'sort_methods': ('DATE', )
    }
    return plugin.finish(items, **finish_kwargs)
        
def __list_themes(themes):
    items = []
    for id in themes:
        item = {
            'label': themes[id]['title'],
            'path': plugin.url_for('show_theme_videos', themeId=id)
        }
        items.append(item)
    
    return plugin.finish(items)

### Lrytas API    

def trim_cdata(str):
    m = re.search('<\!\[CDATA\[(.+)\]\]>', str)
    if m:
        return m.group(1)
    return str

def fetch_videos_xml():
    response = urllib2.urlopen('http://www.lrytas.lt/_ipad/video_list.asp')
    xml = response.read()
    return xml

def parse_themes_xml(xml):
    
    root = ET.fromstring(xml)

    themes = {}
    for clip in root.findall('./clips_by_site_id/new/clip'):
        group = {}
        group['id'] = clip.find("id").text
        group['themeId'] = clip.find("tema").text
        group['title'] = clip.find("pavadinimas").text
        group['imgSrc'] = get_img_src(clip.find("foto_id").text)
        group['themeTitle'] = clip.find("tema_pavadinimas").text
        group['date'] = clip.find("data").text
        group['videoSrc'] = clip.find("video_file").text
    
        if not themes.has_key(group['themeId']):
            themes[group['themeId']] = {}
            themes[group['themeId']]['title'] = group['themeTitle']
            themes[group['themeId']]['clips'] = []
            
        themes[group['themeId']]['clips'].append(group);
        
    return themes

def load_themes():
    xml = fetch_videos_xml()
    themes_and_clips = parse_themes_xml(xml)
    return themes_and_clips

def fetch_video_info(video_id):
    log("fetch_video_info")
    response = urllib2.urlopen("http://tv.lrytas.lt/?id=" + video_id)
    html = response.read()
    video_url = re.search('href="(http.+mp4)"', html).group(1)
    video_title = re.search('<h1[^>]*>([^<]+)</h1>', html).group(1)
    img_id = re.search('rel\="image_src" href\=.+img\.lrytas\.lt/show_foto/\?id=(\d+)', html).group(1)
    return video_url, video_title, img_id
    
def get_img_src(img_id):
    return "http://img.lrytas.lt/show_foto/?id=%s&s=5&f=5" % (img_id)

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, err:
        plugin.notify(msg='Could not load the plugin.')
        log(err)
        # log(traceback.format_exc())
