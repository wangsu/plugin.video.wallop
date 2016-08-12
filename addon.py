import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import httplib
import json
import urllib
import urlparse

def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict

def addDirectoryItem(parameters, li):
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=handle, url=url, 
        listitem=li, isFolder=True)

def show_channels(wallop_server):
    
    # Check if Wallop Server has been defined
    addon = xbmcaddon.Addon('plugin.video.wallop')
    if wallop_server == '':
        addon.openSettings()
        
    # Fetch Channel Lineup
    conn = httplib.HTTPConnection(wallop_server, '8888', timeout=15)
    url = '/channels?type=favorites'
    headers = {"Accept":"application/json"}
    conn.request("GET", url, '', headers)
    response = conn.getresponse()
    conn.close
    
    # Display Channels
    items = json.load(response)
    for item in items['channels']:
        liStyle = xbmcgui.ListItem(item['GuideName'])
        addDirectoryItem({"channel": item['GuideNumber']}, liStyle)    
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def play_channel(channel,wallop_server):
    
    # Fetch resolution and bitrate from settings page
    resolution = xbmcplugin.getSetting(handle,'resolution')
    bitrate = xbmcplugin.getSetting(handle,'bitrate')
    
    # Tune Channel
    conn = httplib.HTTPConnection(wallop_server, 8888, timeout=15)
    url = "/channels/%s/tune?resolution=%s&bitrate=%s" % (channel, resolution, bitrate)
    conn.request("POST", url)
    conn.close

    # Keep Checking status of tuning until it returns ready
    while True:

        conn = httplib.HTTPConnection(wallop_server,'8888', timeout=15)
        url = "/channels/%s/status" % channel
        conn.request("GET", url)
        response = conn.getresponse()
        conn.close
        data = json.load(response)
    
        if data["ready"] != True:
            xbmc.sleep(5000)
        else:
            break

        link = "http://%s:8888/channels/%s.m3u8" % (wallop_server, channel)
        xbmc.Player().play(link)

handle = int(sys.argv[1])
wallop_server = xbmcplugin.getSetting(handle,'wallop')
        
params = parameters_string_to_dict(sys.argv[2])
channel = str(params.get("channel", ""))

if channel == "":
    show_channels(wallop_server)
else:
    play_channel(channel, wallop_server)
