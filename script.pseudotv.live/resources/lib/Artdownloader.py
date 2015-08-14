#   Copyright (C) 2015 Kevin S. Graer
#
#
# This file is part of PseudoTV Live.
#
# PseudoTV is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PseudoTV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PseudoTV.  If not, see <http://www.gnu.org/licenses/>.

import xbmc, xbmcgui, xbmcaddon
import subprocess, os
import time, datetime, random
import threading
import sys, re
import random, traceback
import urllib, urllib2, urlparse
import socket

from apis.fanarttv import *
from ChannelList import *
from Globals import *
from FileAccess import FileAccess
from xml.etree import ElementTree as ET
from apis import tvdb
from apis import tmdb
from urllib import unquote, quote
from utils import *
from HTMLParser import HTMLParser

try:
    from metahandler import metahandlers
except:  
    pass

try:
    import buggalo
    buggalo.SUBMIT_URL = 'http://pseudotvlive.com/buggalo-web/submit.php'
except:
    pass
    
# Commoncache plugin import
try:
    import StorageServer
except Exception,e:
    import storageserverdummy as StorageServer
    
try:
    from PIL import Image
    from PIL import ImageEnhance
except:
    pass
    
socket.setdefaulttimeout(30)

class Artdownloader:

    def __init__(self):
        self.chanlist = ChannelList()
        self.fanarttv = fanarttv()
        self.tvdbAPI = tvdb.TVDB(TVDB_API_KEY)
        self.tmdbAPI = tmdb.TMDB(TMDB_API_KEY)  
        
        
    def log(self, msg, level = xbmc.LOGDEBUG):
        log('Artdownloader: ' + msg, level)

    
    def logDebug(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == 'true':
            log('Artdownloader: ' + msg, level)
    

    def getFallback_Arttype(self, arttype):
        arttype = arttype.lower()
        arttype = arttype.replace('landscape','fanart')
        arttype = arttype.replace('folder','poster')
        arttype = arttype.replace('clearart','logo')
        arttype = arttype.replace('character','logo')
        self.log("getFallback_Arttype = " + arttype)
        return arttype

        
    def searchDetails(self, file_detail, arttype):
        self.log("searchDetails")
        for f in file_detail:
            try:
                arttypes = re.search(('"%s" *: *"(.*?)"' % arttype), f)
                arttypes_fallback = re.search(('"%s" *: *"(.*?)"' % self.getFallback_Arttype(arttype)), f)
                if arttypes != None and len(arttypes.group(1)) > 0:
                    return (unquote(xbmc.translatePath((arttypes.group(1).split(','))[0]))).replace('image://','').replace('.jpg/','.jpg').replace('.png/','.png') 
                elif arttypes_fallback != None and len(arttypes_fallback.group(1)) > 0:
                    if (arttypes_fallback.group(1)).lower() ==  (self.getFallback_Arttype(arttype)).lower():
                        return (unquote(xbmc.translatePath((arttypes_fallback.group(1).split(','))[0]))).replace('image://','').replace('.jpg/','.jpg').replace('.png/','.png')
            except:
                pass
                
    
    def dbidArt(self, type, chname, mpath, dbid, arttypeEXT):
        self.log("dbidArt")
        file_detail = []
        try:
            if type == 'tvshow':
                json_query = ('{"jsonrpc":"2.0","method":"VideoLibrary.GetTVShowDetails","params":{"tvshowid":%s,"properties":["art","thumbnail","fanart"]},"id":1}' % dbid)
            elif type == 'movie':
                json_query = ('{"jsonrpc":"2.0","method":"VideoLibrary.GetMovieDetails","params":{"movieid":%s,"properties":["art","thumbnail","fanart"]},"id":1}' % dbid)
            arttype = (arttypeEXT.split(".")[0])
            json_folder_detail = self.chanlist.sendJSON(json_query)
            file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)
            return self.searchDetails(file_detail, arttype)
        except Exception,e:  
            self.log("dbidArt, Failed" + str(e), xbmc.LOGERROR)
        
        
    def JsonArt(self, type, chname, mpath, arttypeEXT):
        self.log("JsonArt")
        file_detail = []
        try:
            json_query = ('{"jsonrpc":"2.0","method":"Files.GetDirectory","params":{"directory":"%s","media":"video","properties":["art","fanart","thumbnail"]}, "id": 1}' % (mpath))
            arttype = (arttypeEXT.split(".")[0])
            json_folder_detail = self.chanlist.sendJSON(json_query)
            file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)
            return self.searchDetails(file_detail, arttype)
        except Exception,e:  
            self.log("JsonArt, Failed" + str(e), xbmc.LOGERROR)

            
    def FindArtwork(self, type, chtype, chname, id, dbid, mpath, arttypeEXT):
        if Primary_Cache_Enabled == True:
            self.log("FindArtwork Cache") 
            try: #stagger artwork cache by chtype
                if chtype <= 3:
                    result = artwork1.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
                elif chtype > 3 and chtype <= 6:
                    result = artwork2.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
                elif chtype > 6 and chtype <= 9:
                    result = artwork3.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
                elif chtype > 9 and chtype <= 12:
                    result = artwork4.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
                elif chtype > 9 and chtype <= 15:
                    result = artwork5.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
                else:
                    result = artwork6.cacheFunction(self.FindArtwork_NEW, type, chtype, chname, id, dbid, mpath, arttypeEXT)
            except:
                self.log("FindArtwork Cache Failed Forwarding to FindArtwork_NEW") 
                result = self.FindArtwork_NEW(type, chtype, chname, id, dbid, mpath, arttypeEXT)
        else:
            self.log("FindArtwork Cache Disabled")
            result = self.FindArtwork_NEW(type, chtype, chname, id, dbid, mpath, arttypeEXT)
        if not result:
            result = self.SetDefaultArt_NEW(chname, mpath, arttypeEXT)
        return result

               
    def FindArtwork_NEW(self, type, chtype, chname, id, dbid, mpath, arttypeEXT):
        self.logDebug("FindArtwork_NEW, type = " + type + ', chtype = ' + str(chtype) + ', chname = ' + chname + ', id = ' + str(id) + ', dbid = ' + str(dbid) + ', arttypeEXT = ' + arttypeEXT)
        try:
            setImage = ''
            CacheArt = False
            DefaultArt = False
            arttypeEXT = EXTtype(arttypeEXT)
            arttype = arttypeEXT.split(".")[0]
            fle = id + '-' + arttypeEXT
            ext = arttypeEXT.split('.')[1]
            cachedthumb = xbmc.getCacheThumbName(os.path.join(mpath, fle))
            cachefile = xbmc.translatePath(os.path.join(ART_LOC, cachedthumb[0], cachedthumb[:-4] + "." + ext)).replace("\\", "/")
                    
            if FileAccess.exists(cachefile):
                self.logDebug('FindArtwork_NEW, Artwork Cache')
                return cachefile   
                
            elif chtype <= 7:
                self.logDebug('FindArtwork_NEW, chtype <= 7 - FOLDER')
                smpath = mpath.rsplit('/',2)[0]
                artSeries = xbmc.translatePath(os.path.join(smpath, arttypeEXT))
                artSeason = xbmc.translatePath(os.path.join(mpath, arttypeEXT))
                artSeries_fallback = xbmc.translatePath(os.path.join(smpath, self.getFallback_Arttype(arttypeEXT)))
                artSeason_fallback = xbmc.translatePath(os.path.join(mpath, self.getFallback_Arttype(arttypeEXT)))

                if type == 'tvshow': 
                    if FileAccess.exists(artSeries):
                        return artSeries
                    elif FileAccess.exists(artSeason):
                        return artSeason
                    elif FileAccess.exists(artSeries_fallback): 
                        return artSeries_fallback
                    elif FileAccess.exists(artSeason_fallback):
                        return artSeason_fallback    
                else:
                    if FileAccess.exists(artSeason):
                        return artSeason
                    elif FileAccess.exists(artSeason_fallback):
                        return artSeason_fallback    
            
                if getProperty("PTVL.LOWPOWER") != "true":
                    self.logDebug('FindArtwork_NEW, chtype <= 7 - JSON/DBID')
                    SetImage = self.JsonArt(type, chname, mpath, arttypeEXT)
                    if not SetImage and dbid != '0':
                        SetImage = self.dbidArt(type, chname, mpath, dbid, arttypeEXT)
                    if FileAccess.exists(SetImage):
                        return SetImage
                    if ENHANCED_DATA == True: 
                        self.logDebug('FindArtwork_NEW, Artwork Download')
                        self.DownloadArt(type, id, arttype, cachefile, chname, mpath, arttypeEXT)
            else:
                if id == '0':
                    if chtype == 8 and dbid != '0':
                        self.logDebug('FindArtwork_NEW, XMLTV')
                        return dbid.decode('base64')
                    elif type == 'youtube':
                        self.logDebug('FindArtwork_NEW, YOUTUBE')
                        return "http://i.ytimg.com/vi/"+dbid+"/mqdefault.jpg"
                    elif type == 'rss' and dbid != '0':
                        self.logDebug('FindArtwork_NEW, RSS')
                        return dbid.decode('base64')
                else:
                    if ENHANCED_DATA == True: 
                        self.logDebug('FindArtwork_NEW, Artwork Download')
                        self.DownloadArt(type, id, arttype, cachefile, chname, mpath, arttypeEXT)
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: FindArtwork_NEW Failed" + str(e), xbmc.LOGERROR)
            buggalo.onExceptionRaised()     
                
                
    def SetDefaultArt(self, chname, mpath, arttypeEXT):
        self.logDebug("SetDefaultArt Cache")
        if Primary_Cache_Enabled == True:
            try:
                result = artwork.cacheFunction(self.SetDefaultArt_NEW, chname, mpath, arttypeEXT)
            except:
                self.log("SetDefaultArt Cache Failed Forwarding to SetDefaultArt_NEW") 
                result = self.SetDefaultArt_NEW(chname, mpath, arttypeEXT)
                pass
        else:
            result = self.SetDefaultArt_NEW(chname, mpath, arttypeEXT)
        if not result:
            result = THUMB
        return result  

        
    def SetDefaultArt_NEW(self, chname, mpath, arttypeEXT):
        self.logDebug('SetDefaultArt_NEW, chname = ' + chname + ', arttypeEXT = ' + arttypeEXT)
        try:
            setImage = ''
            arttype = arttypeEXT.split(".")[0]
            MediaImage = os.path.join(MEDIA_LOC, (arttype + '.png'))
            StockImage = os.path.join(IMAGES_LOC, (arttype + '.png'))
            ChannelLogo = os.path.join(LOGO_LOC,chname[0:18] + '.png')
            
            if FileAccess.exists(ChannelLogo):
                self.logDebug('SetDefaultArt, Channel Logo')
                return ChannelLogo
            elif mpath[0:6] == 'plugin':
                self.logDebug('SetDefaultArt, Plugin Icon')
                icon = 'special://home/addons/'+(mpath.replace('plugin://',''))+ '/icon.png'
                return icon
            elif FileAccess.exists(MediaImage):
                self.logDebug('SetDefaultArt, Media Image')
                return MediaImage
            elif FileAccess.exists(StockImage):
                self.logDebug('SetDefaultArt, Stock Image')
                return StockImage
            else:
                self.logDebug('SetDefaultArt, THUMB')
                return THUMB
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: SetDefaultArt_NEW Failed" + str(e), xbmc.LOGERROR)
            buggalo.onExceptionRaised()
              
              
    def DownloadArt(self, type, id, arttype, cachefile, chname, mpath, arttypeEXT):
        self.log('DownloadArt')
        try:
            self.DownloadArtTimer = threading.Timer(0.1, self.DownloadArt_Thread, [type, id, arttype, cachefile, chname, mpath, arttypeEXT])
            self.DownloadArtTimer.name = "DownloadArtTimer"
            if self.DownloadArtTimer.isAlive():
                self.DownloadArtTimer.cancel()
                self.DownloadArtTimer.join()
            self.DownloadArtTimer.start()
        except Exception,e:  
            self.log("DownloadArt, Failed" + str(e), xbmc.LOGERROR)
            
                       
    def DownloadArt_Thread(self, type, id, arttype, cachefile, chname, mpath, arttypeEXT):
        self.log('DownloadArt_Thread')
        try:
            drive, Dpath = os.path.splitdrive(cachefile)
            path, filename = os.path.split(Dpath)

            if not FileAccess.exists(os.path.join(drive,path)):
                FileAccess.makedirs(os.path.join(drive,path))   
                    
            if type == 'tvshow':
                self.logDebug('DownloadArt_Thread, tvshow')
                tvdb_Types = ['banner', 'fanart', 'folder', 'poster']
                    
                if arttype in tvdb_Types:
                    self.logDebug('DownloadArt_Thread, TVDB')
                    arttype = arttype.replace('banner', 'graphical').replace('folder', 'poster')
                    tvdb = str(self.tvdbAPI.getBannerByID(id, arttype))
                    tvdbPath = tvdb.split(', ')[0].replace("[('", "").replace("'", "") 
                    if tvdbPath.startswith('http'):
                        self.logDebug('DownloadArt_Thread, return TV TVDB')
                        return download_silent(tvdbPath,cachefile)
                
                self.logDebug('DownloadArt_Thread, Fanart.TV')
                arttype = arttype.replace('graphical', 'banner').replace('folder', 'poster').replace('fanart', 'landscape')
                fan = str(self.fanarttv.get_image_list_TV(id))
                file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(fan)
                pref_language = self.fanarttv.get_abbrev(REAL_SETTINGS.getSetting('limit_preferred_language'))
                
                for f in file_detail:
                    try:
                        languages = re.search("'language' *: *(.*?),", f)
                        art_types = re.search("'art_type' *: *(.*?),", f)
                        fanPaths = re.search("'url' *: *(.*?),", f)       
                        if languages and len(languages.group(1)) > 0:
                            language = (languages.group(1)).replace("u'",'').replace("'",'')
                            if language.lower() == pref_language.lower():
                                if art_types and len(art_types.group(1)) > 0:
                                    art_type = art_types.group(1).replace("u'",'').replace("'",'').replace("[",'').replace("]",'')
                                    if art_type.lower() == arttype.lower():
                                        if fanPaths and len(fanPaths.group(1)) > 0:
                                            fanPath = fanPaths.group(1).replace("u'",'').replace("'",'')
                                            if fanPath.startswith('http'):
                                                self.logDebug('DownloadArt_Thread, return TV Fanart.tv')
                                                return download_silent(fanPath,cachefile)
                    except:
                        pass

            elif type == 'movie':
                self.logDebug('DownloadArt_Thread, movie')
                tmdb_Types = ['fanart', 'folder', 'poster']

                if arttype in tmdb_Types:
                    self.logDebug('DownloadArt_Thread, TMDB')
                    arttype = arttype.replace('folder', 'poster')
                    tmdb = self.tmdbAPI.get_image_list(id)
                    data = str(tmdb).replace("[", "").replace("]", "").replace("'", "")
                    data = data.split('}, {')
                    tmdbPath = str([s for s in data if arttype in s]).split("', 'width: ")[0]
                    match = re.search('url *: *(.*?),', tmdbPath)
                    if match:
                        tmdbPath = match.group().replace(",", "").replace("url: u", "").replace("url: ", "")
                        if tmdbPath.startswith('http'):
                            FanMovieDownload = False 
                            self.logDebug('DownloadArt_Thread, return Movie TMDB')
                            return download_silent(tmdbPath,cachefile)

                self.logDebug('DownloadArt_Thread, Fanart.TV')
                arttype = arttype.replace('graphical', 'banner').replace('folder', 'poster').replace('fanart', 'landscape')
                fan = str(self.fanarttv.get_image_list_Movie(id))
                file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(fan)
                # print file_detail
                pref_language = self.fanarttv.get_abbrev(REAL_SETTINGS.getSetting('limit_preferred_language'))
                
                for f in file_detail:
                    try:
                        languages = re.search("'language' *: *(.*?),", f)
                        art_types = re.search("'art_type' *: *(.*?),", f)
                        fanPaths = re.search("'url' *: *(.*?),", f)    
                        if languages and len(languages.group(1)) > 0:
                            language = (languages.group(1)).replace("u'",'').replace("'",'')
                            if language.lower() == pref_language.lower():
                                if art_types and len(art_types.group(1)) > 0:
                                    art_type = art_types.group(1).replace("u'",'').replace("'",'').replace("[",'').replace("]",'')
                                    if art_type.lower() == arttype.lower():
                                        if fanPaths and len(fanPaths.group(1)) > 0:
                                            fanPath = fanPaths.group(1).replace("u'",'').replace("'",'')
                                            if fanPath.startswith('http'):
                                                self.logDebug('DownloadArt_Thread, return Movie Fanart.tv')
                                                return download_silent(fanPath,cachefile)
                    except:
                        pass
            self.logDebug('DownloadArt_Thread, Trying Fallback Download')
            self.DownloadArt(type, id, self.getFallback_Arttype(arttype), cachefile, chname, mpath, self.getFallback_Arttype(arttype))                
        except Exception,e:  
            self.log("DownloadArt_Thread, Failed" + str(e), xbmc.LOGERROR)
            
            
    def DownloadMetaArt(self, type, fle, id, typeEXT, ART_LOC):
        self.log('DownloadMetaArt')
        ArtPath = os.path.join(ART_LOC, fle)
        setImage = ''
        
        if type == 'tvshow':
            Tid = id
            Mid = ''
        else:
            Mid = id
            Tid = ''
            
        typeEXT = typeEXT.split('.')[0]
        typeEXT = typeEXT.replace('landscape','backdrop_url').replace('fanart','backdrop_url').replace('logo','backdrop_url').replace('clearart','backdrop_url').replace('poster','cover_url').replace('banner','banner_url')
        try:
            self.log('DownloadMetaArt, metahander')
            self.metaget = metahandlers.MetaData(preparezip=False)
            ImageURL = str(self.metaget.get_meta(type, '', imdb_id=str(Mid), tmdb_id=str(Tid)))[typeEXT]
            resource = urllib.urlopen(ImageURL)
            output = FileAccess.open(ArtPath, 'w')
            output.write(resource.read())
            output.close()
            setImage = ArtPath
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: DownloadMetaArt Failed" + str(e), xbmc.LOGERROR)
            buggalo.onExceptionRaised()      
        return setImage
        

    def Fanart_Download(self, type, arttype, id, FilePath):
        try:
            if type == 'tvshow':
                arttype = arttype.replace('graphical', 'banner').replace('folder', 'poster').replace('fanart', 'landscape')
                fan = str(self.fanarttv.get_image_list_TV(id))
                file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(fan)
                pref_language = self.fanarttv.get_abbrev(REAL_SETTINGS.getSetting('limit_preferred_language'))
                
                for f in file_detail:
                    languages = re.search("'language' *: *(.*?),", f)
                    art_types = re.search("'art_type' *: *(.*?),", f)
                    fanPaths = re.search("'url' *: *(.*?),", f)       
                    if languages and len(languages.group(1)) > 0:
                        language = (languages.group(1)).replace("u'",'').replace("'",'')
                        if language == pref_language:
                            if art_types and len(art_types.group(1)) > 0:
                                art_type = art_types.group(1).replace("u'",'').replace("'",'').replace("[",'').replace("]",'')
                                if art_type.lower() == arttype.lower():
                                    if fanPaths and len(fanPaths.group(1)) > 0:
                                        fanPath = fanPaths.group(1).replace("u'",'').replace("'",'')
                                        if fanPath.startswith('http'):
                                            download_silent(fanPath,FilePath)
                                            break 
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: Fanart_Download Failed" + str(e), xbmc.LOGERROR)
            buggalo.onExceptionRaised()      

            
    def AlphaLogo(self, org, mod):
        self.log("AlphaLogo")
        try:
            img = Image.open(org)
            img = img.convert("RGBA")
            datas = img.getdata()
            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            img.save(mod, "PNG")
        except:
            pass

            
    def ConvertBug(self, org, mod):
        self.log("ConvertBug")
        try:
            drive, path = os.path.splitdrive(mod)
            path, filename = os.path.split(path)
            if not FileAccess.exists(path):
                FileAccess.makedirs(path)
                
            org =  xbmc.translatePath(org)
            original = Image.open(org)                  
            converted_img = original.convert('LA')  
            img_bright = ImageEnhance.Brightness(converted_img)
            converted_img = img_bright.enhance(1.0)     
            converted_img.save(mod)
            return mod
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: ConvertBug Failed" + str(e), xbmc.LOGERROR)
            return 'NA.png'
            

    def FindBug(self, chtype, chname):
        self.logDebug("FindBug Cache")
        if Primary_Cache_Enabled == True:
            try:
                result = artwork.cacheFunction(self.FindBug_NEW, chtype, chname)
            except:
                result = self.FindBug_NEW(chtype, chname)
        else:
            result = self.FindBug_NEW(chtype, chname)
        if not result:
            result = THUMB
        return result  
        
        
    def FindBug_NEW(self, chtype, chname):
        self.logDebug("FindBug_NEW, chname = " + chname)
        try:
            setImage = ''
            BugName = (chname[0:18] + '.png')
            BugFLE = xbmc.translatePath(os.path.join(LOGO_LOC,BugName))
            cachedthumb = xbmc.getCacheThumbName(BugFLE)
            cachefile = xbmc.translatePath(os.path.join(ART_LOC, cachedthumb[0], cachedthumb[:-4] + ".png")).replace("\\", "/")
            
            if REAL_SETTINGS.getSetting('UNAlter_ChanBug') == 'true':
                if chname == 'OnDemand':
                    DefaultBug = os.path.join(IMAGES_LOC,'ondemand.png')
                else:
                    DefaultBug = os.path.join(IMAGES_LOC,'logo.png')
            else:
                if chname == 'OnDemand':
                    DefaultBug = os.path.join(IMAGES_LOC,'Default_ondemand.png')
                else:
                    DefaultBug = os.path.join(IMAGES_LOC,'Default.png')
            
            if chtype == 8:
                return 'NA.png'
            else:
                if REAL_SETTINGS.getSetting('UNAlter_ChanBug') == 'true':
                    if not FileAccess.exists(BugFLE):
                        BugFLE = DefaultBug
                    return BugFLE
                else:
                    if FileAccess.exists(cachefile):
                        return cachefile
                    else:
                        if not FileAccess.exists(BugFLE):
                            return DefaultBug
                        else:
                            return self.ConvertBug(BugFLE, cachefile)
        except Exception,e:  
            self.log("script.pseudotv.live-Artdownloader: FindBug_NEW Failed" + str(e), xbmc.LOGERROR)
            buggalo.onExceptionRaised()