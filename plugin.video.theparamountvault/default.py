#   Copyright (C) 2016 Lunatixz
#
#
# This file is part of The Paramount Vault.
#
# The Paramount Vault is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Paramount Vault is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with The Paramount Vault.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
import os, re, sys, time, zipfile, requests, random, traceback
import urllib, urllib2,cookielib, base64, fileinput, shutil, socket, httplib, urlparse, HTMLParser
import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
import time, _strptime, string, datetime, ftplib, hashlib, smtplib, feedparser, imp, operator

from pyfscache import *
from xml.etree import ElementTree as ET
from xml.dom.minidom import parse, parseString
from datetime import timedelta
      
if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json

# Plugin Info
ADDON_ID = 'plugin.video.theparamountvault'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
REQUESTS_LOC = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'requests',''))
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')
DEBUG = REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'
KODI_MONITOR = xbmc.Monitor()
YOUTUBE_PLAYER = 'plugin://plugin.video.youtube/play/?video_id='
YT_API_KEY = REAL_SETTINGS.getSetting('YT_API_KEY')
TMDB_API_KEY = REAL_SETTINGS.getSetting('TMDB_API_KEY')

# pyfscache globals
from pyfscache import *
cache_daily = FSCache(REQUESTS_LOC, days=1, hours=0, minutes=0)

try:
    from metahandler import metahandlers
    METAGET = metahandlers.MetaData(preparezip=False, tmdb_api_key=TMDB_API_KEY)
    ENHANCED_DATA = REAL_SETTINGS.getSetting('Enable_Metahandler') == 'true'               
except Exception,e:  
    ENHANCED_DATA = False 
    xbmc.log("plugin.video.bringthepopcorn: metahandler Import failed! " + str(e))   

def log(msg, level = xbmc.LOGDEBUG):
    if DEBUG == True:
        xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + msg, level)
        
def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
    return string

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        xbmc.sleep(100)
        
def getTitleYear(showtitle, showyear=0):  
    # extract year from showtitle, merge then return
    try:
        labelshowtitle = re.compile('(.+?) [(](\d{4})[)]$').findall(showtitle)
        title = labelshowtitle[0][0]
        year = int(labelshowtitle[0][1])
    except Exception,e:
        year = showyear
        title = showtitle
    log("getTitleYear, return " + str(year) +', '+ title +', '+ showtitle) 
    return year, title, showtitle
   
def __total_seconds__(delta):
    try:
        return delta.total_seconds()
    except AttributeError:
        return int((delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10 ** 6)) / 10 ** 6

def parseYoutubeDuration(duration):
    try:
        dur = 0
        """ Parse and prettify duration from youtube duration format """
        DURATION_REGEX = r'P(?P<days>[0-9]+D)?T(?P<hours>[0-9]+H)?(?P<minutes>[0-9]+M)?(?P<seconds>[0-9]+S)?'
        NON_DECIMAL = re.compile(r'[^\d]+')
        duration_dict = re.search(DURATION_REGEX, duration).groupdict()
        converted_dict = {}
        # convert all values to ints, remove nones
        for a, x in duration_dict.iteritems():
            if x is not None:
                converted_dict[a] = int(NON_DECIMAL.sub('', x))
        x = time.strptime(str(timedelta(**converted_dict)).split(',')[0],'%H:%M:%S')
        dur = int(__total_seconds__(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec)))
        log('parseYoutubeDuration, dur = ' + str(dur))
    except Exception,e:
        pass
    return dur

def getYoutubeDetails(YTID):
    log('getYoutubeDetails')
    try:
        YT_URL_Video = ('https://www.googleapis.com/youtube/v3/videos?key=%s&id=%s&part=id,snippet,contentDetails,statistics' % (YT_API_KEY, YTID))
        details = re.compile("},(.*?)}", re.DOTALL ).findall(read_url_cached(YT_URL_Video))
    except:
        details = ''
    return details

def getYoutubeMeta(id):
    log('getYoutubeMeta ' + id)
    stars =  ''
    year =  ''
    duration =  ''
    description =  ''
    title =  ''
    SEtitle =  ''
    genre =  ''
    rating = '' 
    playcount = '' 
    hd = '' 
    cc = ''
    detail = getYoutubeDetails(id)
    for f in detail:
        cats = {0 : 'NR',
                1 : 'Film & Animation',
                2 : 'Autos & Vehicles',
                10 : 'Music',
                15 : 'Pets & Animals',
                17 : 'Sports',
                18 : 'Short Movies',
                19 : 'Travel & Events',
                20 : 'Gaming',
                21 : 'Videoblogging',
                22 : 'People & Blogs',
                23 : 'Comedy',
                24 : 'Entertainment',
                25 : 'News & Politics',
                26 : 'Howto & Style',
                27 : 'Education',
                28 : 'Science & Technology',
                29 : 'Nonprofits & Activism',
                30 : 'Movies',
                31 : 'Anime/Animation',
                32 : 'Action/Adventure',
                33 : 'Classics',
                34 : 'Comedy',
                35 : 'Documentary',
                36 : 'Drama',
                37 : 'Family',
                38 : 'Foreign',
                39 : 'Horror',
                40 : 'Sci-Fi/Fantasy',
                41 : 'Thriller',
                42 : 'Shorts',
                43 : 'Shows',
                44 : 'Trailers'}
        try:
            contentDetail = re.search('"contentDetails" *:', f)
            if contentDetail:
                durations = re.search('"duration" *: *"(.*?)",', f)
                definitions = re.search('"definition" *: *"(.*?)",', f)
                captions = re.search('"caption" *: *"(.*?)",', f)
                duration = parseYoutubeDuration((durations.group(1) or duration))
                
                if definitions and len(definitions.group(1)) > 0:
                    hd = (definitions.group(1)) == 'hd'
                    
                if captions and len(captions.group(1)) > 0:
                    cc = (captions.group(1)) == 'true'

            categoryIds = re.search('"categoryId" *: *"(.*?)",', f)
            if categoryIds and len(categoryIds.group(1)) > 0:
                genre = cats[int(categoryIds.group(1))]
                    
            chname = ''
            channelTitles = re.search('"channelTitle" *: *"(.*?)",', f)
            if channelTitles and len(channelTitles.group(1)) > 0:
                chname = channelTitles.group(1)

            items = re.search('"items" *:', f)
            if items:
                titles = re.search('"title" *: *"(.*?)",', f)
                descriptions = re.search('"description" *: *"(.*?)",', f)
                publisheds = re.search('"publishedAt" *: *"(.*?)",', f)

                if titles and len(titles.group(1)) > 0:
                    title = (titles.group(1) or title)
                if descriptions and len(descriptions.group(1)) > 0:
                    description = ((descriptions.group(1) or description).split('http')[0]).replace('\\n',' ')
                if publisheds and len(publisheds.group(1)) > 0:
                    published = (publisheds.group(1) or '')
                    
                    if year == 0:
                        year = int(published[0:4])

                if not description:
                    description = title

            statistics = re.search('"statistics" *:', f)
            if statistics:
                if stars == 0.0:
                    try:
                        viewCounts = re.search('"viewCount" *: *"(.*?)",', f)
                        likeCounts = re.search('"likeCount" *: *"(.*?)",', f)
                        dislikeCounts = re.search('"dislikeCount" *: *"(.*?)",', f)
                        likeCount = int(likeCounts.group(1) or '0')
                        dislikeCount = int(dislikeCounts.group(1) or '0')
                        V = likeCount + dislikeCount
                        R = likeCount - dislikeCount
                        stars = float((((V * R)) / (V))/100)/5
                    except:
                        stars = 0.0
        except Exception,e:
            log('getYoutubeMeta, failed! ' + str(e))

    log("getYoutubeMeta, return")
    return stars, year, duration, description, title, chname, id, genre, rating, playcount, hd, cc
        
def getYoutubeUserID( YTid):
    log("getYoutubeUserID, IN = " + YTid)
    YT_ID = 'UC'
    try:
        region = 'US' #todo
        lang = xbmc.getLanguage(xbmc.ISO_639_1)
        youtubeApiUrl = 'https://www.googleapis.com/youtube/v3/'
        youtubeChannelsApiUrl = (youtubeApiUrl + 'channels?key=%s&chart=mostPopular&regionCode=%s&hl=%s&' % (YT_API_KEY, region, lang))
        requestParametersChannelId = (youtubeChannelsApiUrl + 'forUsername=%s&part=id' % (YTid))
        f = read_url_cached(requestParametersChannelId)
        YT_IDS = re.search('"id" *: *"(.*?)"', f)
        if YT_IDS:
            YT_ID = YT_IDS.group(1)
        log("getYoutubeUserID, OUT = " + YT_ID)
    except Exception,e:
        log('getYoutubeUserID, failed! ' + str(e), xbmc.LOGERROR)
    return YT_ID
       
def open_url(url, userpass=None):
    log("open_url")
    page = ''
    try:
        request = urllib2.Request(url)
        if userpass:
            user, password = userpass.split(':')
            base64string = base64.encodestring('%s:%s' % (user, password))
            request.add_header("Authorization", "Basic %s" % base64string) 
        else:
            request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        page = urllib2.urlopen(request)
        page.close
        return page
    except urllib2.HTTPError, e:
        return page
        
@cache_daily        
def read_url_cached(url, userpass=False, return_type='read'):
    log("read_url_cached")
    try:
        if return_type == 'readlines':
            response = open_url(url, userpass).readlines()
        else:
            response = open_url(url, userpass).read()
        return response
    except Exception,e:
        pass
     
def getParamount():
    addDir('New Releases','PLd0LhgZxFkVKh_JNXcdHoPYo832Wu9fub',3012)
    addDir('Tough Guy Tuesday #tgt','PLd0LhgZxFkVJbKX_LyERYB6TRk9pbNO5O',3012)
    addDir('Action Movies','PLd0LhgZxFkVII3x-u6Ogh90iEepCLjKcW',3012)
    addDir('Classics Movies','PLd0LhgZxFkVI7ds18u2o-qVluJfREYsIf',3012)
    addDir('Comedy Movies','PLd0LhgZxFkVINkUJWrXd3AdGkrPGfpByw',3012)
    addDir('Drama Movies','PLd0LhgZxFkVLtg4IZ-1jgGPmwZyhR-66o',3012)
    addDir('Horror Movies','PLd0LhgZxFkVKnyj6NIMTwGfL-KqBtGyFZ',3012)
    addDir('Sci-Fi Movies','PLd0LhgZxFkVJFsvRos55jeIKHKBmfN2uA',3012)
    addDir('Thriller Movies','PLd0LhgZxFkVJ4iI_mkUiHjwhW3c98GoLC',3012)
    addDir('Western Movies','PLd0LhgZxFkVLB8Zs8bQP5B-bnLimzY0FC',3012)

def getParamountItems(url):
    getYoutubeVideos(2, url, '', 200)

def getYoutubeVideos(YT_Type, YT_ID, YT_NextPG, limit):
    log("getYoutubeVideos, YT_Type = " + str(YT_Type) + ', YT_ID = ' + YT_ID) 
    cnt = 0
    region = 'US' #todo
    lang = xbmc.getLanguage(xbmc.ISO_639_1)
    Last_YT_NextPG = YT_NextPG      
    youtubeApiUrl = 'https://www.googleapis.com/youtube/v3/'
    youtubeChannelsApiUrl = (youtubeApiUrl + 'channels?key=%s&chart=mostPopular&regionCode=%s&hl=%s&' % (YT_API_KEY, region, lang))
    youtubeSearchApiUrl = (youtubeApiUrl + 'search?key=%s&chart=mostPopular&regionCode=%s&hl=%s&' % (YT_API_KEY, region, lang))
    youtubePlaylistApiUrl = (youtubeApiUrl + 'playlistItems?key=%s&chart=mostPopular&regionCode=%s&hl=%s&' % (YT_API_KEY, region, lang))
    requestChannelVideosInfo = (youtubeSearchApiUrl + 'channelId=%s&part=id&order=date&pageToken=%s&maxResults=50' % (YT_ID, YT_NextPG))
    requestPlaylistInfo = (youtubePlaylistApiUrl+ 'part=snippet&maxResults=50&playlistId=%s&pageToken=%s' % (YT_ID, YT_NextPG))
    show_busy_dialog()
    if YT_Type == 1:
        if YT_ID[0:2] != 'UC':
            YT_ID = getYoutubeUserID(YT_ID)
            return getYoutubeVideos(YT_Type, YT_ID, YT_NextPG, limit)  
        else:
            YT_URL_Search = requestChannelVideosInfo
            log("getYoutubeVideos, requestChannelVideosInfo = " + YT_URL_Search) 
    elif YT_Type == 2:
        YT_URL_Search = requestPlaylistInfo
        log("getYoutubeVideos, requestPlaylistInfo = " + YT_URL_Search) 

    try:
        detail = re.compile( "{(.*?)}", re.DOTALL ).findall(read_url_cached(YT_URL_Search))
        for f in detail:
            if cnt >= limit:
                break
                
            VidIDS = re.search('"videoId" *: *"(.*?)"', f)
            YT_NextPGS = re.search('"nextPageToken" *: *"(.*?)"', f)
            if YT_NextPGS:
                YT_NextPG = YT_NextPGS.group(1)
                
            if VidIDS:
                VidID = VidIDS.group(1)
                log("getYoutubeVideos, VidID = " + VidID) 
                stars, year, duration, description, showtitle, chname, id, genre, rating, playcount, hd, cc = getYoutubeMeta(VidID)
                year, title, showtitle = getTitleYear(showtitle, year)
                
                thumburl = "http://i.ytimg.com/vi/"+VidID+"/mqdefault.jpg"
                xbmclink = YOUTUBE_PLAYER + VidID
                meta = {'genre':'','plot':'','tagline':'','imdb_id':'','mpaa':'','rating':'','cover_url':'','backdrop_url':''}
                if ENHANCED_DATA == True:
                    meta = METAGET.get_meta('movie', title, str(year))
                    
                # setup infoList
                infoList = {}
                infoList['mediatype']     = 'movies'
                infoList['Duration']      = int(duration)
                infoList['Title']         = uni(showtitle)
                infoList['Year']          = int(year or '0')
                infoList['Genre']         = uni(meta['genre'] or genre or 'Unknown')
                infoList['Plot']          = uni(meta['plot'] or description)
                infoList['tagline']       = uni(meta['tagline'])
                infoList['imdbnumber']    = uni(meta['imdb_id'])
                infoList['mpaa']          = uni(meta['mpaa'] or 'NR')
                infoList['ratings']       = float(meta['rating'] or '0.0')
                        
                # setup infoArt
                infoArt = {}
                infoArt['thumb']        = (meta['cover_url'] or thumburl)
                infoArt['poster']       = (meta['cover_url'] or thumburl)
                infoArt['fanart']       = (meta['backdrop_url'] or thumburl)   
                infoArt['landscape']    = (meta['backdrop_url'] or thumburl)
                cnt += 1
                print infoList, infoArt
                addLink(showtitle,xbmclink,infoList,infoArt)
    except Exception,e:
        log('getYoutubeVideos, Failed!, ' + str(e))
    hide_busy_dialog() 
              
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]             
        return param
            
def addLink(name,url,infoList=False,infoArt=False):
    log('addLink')
    liz=xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'true')
    if infoList == False:
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
    if infoArt == False:
        liz.setArt({'thumb': ICON, 'fanart': FANART})
    else:
        liz.setArt(infoArt)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        
def addDir(name,url,mode,infoList=False,infoArt=False):
    log('addDir')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'false')
    if infoList == False:
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
    if infoArt == False:
        liz.setArt({'thumb': ICON, 'fanart': FANART})
    else:
        liz.setArt(infoArt)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
        pass
try:
    name=urllib.unquote_plus(params["name"])
except:
        pass
try:
    mode=int(params["mode"])
except:
        pass
        
log("Mode: "+str(mode))
log("URL:  "+str(url))
log("Name: "+str(name))

if mode==None: getParamount()
elif mode == 3011: getParamount()
elif mode == 3012: getParamountItems(url)

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True) # End List