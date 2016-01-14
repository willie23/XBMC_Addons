#   Copyright (C) 2015 Kevin S. Graer
#
#
# This file is part of PseudoCompanion.
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

# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib, requests
import time, datetime, operator
import os, sys, re, traceback
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

# Plugin Info
ADDON_ID = 'plugin.video.pseudo.companion'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')
PTVL_ICON = os.path.join(ADDON_PATH,'resources','images','icon.png')
PTVL_ICON_GRAY = os.path.join(ADDON_PATH,'resources','images','icon_gray.png')
DEBUG = True # DEBUG = REAL_SETTINGS.getSetting('enable_Debug') == "true"

def log(msg, level = xbmc.LOGDEBUG):
    if DEBUG != True and level == xbmc.LOGDEBUG:
        return
    xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + uni(msg), level)

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))
    
def utf(string, encoding = 'utf-8'):
    if isinstance(string, basestring):
        if not isinstance(string, unicode):
            string = unicode(string, encoding, 'ignore')
    return string
  
def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string
    
def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
    return string

def cleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&', '&amp;')
    newstr = newstr.replace('>', '&gt;')
    newstr = newstr.replace('<', '&lt;')
    return uni(newstr)

def uncleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&amp;', '&')
    newstr = newstr.replace('&gt;', '>')
    newstr = newstr.replace('&lt;', '<')
    return uni(newstr)
    
def cleanLabels(text, format=''):
    text = uni(text)
    text = re.sub('\[COLOR (.+?)\]', '', text)
    text = re.sub('\[/COLOR\]', '', text)
    text = re.sub('\[COLOR=(.+?)\]', '', text)
    text = re.sub('\[color (.+?)\]', '', text)
    text = re.sub('\[/color\]', '', text)
    text = re.sub('\[Color=(.+?)\]', '', text)
    text = re.sub('\[/Color\]', '', text)
    text = text.replace("[]",'')
    text = text.replace("[UPPERCASE]",'')
    text = text.replace("[/UPPERCASE]",'')
    text = text.replace("[LOWERCASE]",'')
    text = text.replace("[/LOWERCASE]",'')
    text = text.replace("[B]",'')
    text = text.replace("[/B]",'')
    text = text.replace("[I]",'')
    text = text.replace("[/I]",'')
    text = text.replace('[D]','')
    text = text.replace('[F]','')
    text = text.replace("[CR]",'')
    text = text.replace("[HD]",'')
    text = text.replace("()",'')
    text = text.replace("[CC]",'')
    text = text.replace("[Cc]",'')
    text = text.replace("[Favorite]", "")
    text = text.replace("[DRM]", "")
    text = text.replace('(cc).','')
    text = text.replace('(n)','')
    text = text.replace("(SUB)",'')
    text = text.replace("(DUB)",'')
    text = text.replace('(repeat)','')
    text = text.replace("(English Subtitled)", "")    
    text = text.replace("*", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = text.replace("/",'')
    text = text.replace("\ ",'')
    text = text.replace("/ ",'')
    text = text.replace("/",'')
    text = text.replace("\\",'/')
    text = text.replace("//",'/')
    text = text.replace('plugin.video.','')
    text = text.replace('plugin.audio.','')

    if format == 'title':
        text = text.title().replace("'S","'s")
    elif format == 'upper':
        text = text.upper()
    elif format == 'lower':
        text = text.lower()
    else:
        text = text
        
    text = uncleanString(text.strip())
    return text  
    
def addDir(name,description,url,previous,mode,thumb=ICON,icon=ICON,fanart=FANART,infoList=False,infoArt=False,content_type='video',showcontext=False):
    log('addDir')
    liz = xbmcgui.ListItem(name)
    liz.setIconImage(icon)
    if content_type in ['video','movie','tvshow']:
        liz.setThumbnailImage(thumb)
    else:
        liz.setThumbnailImage(fanart)
    liz.setProperty("Fanart_Image", fanart)
    liz.setProperty('IsPlayable', 'false')
    
    if showcontext == True:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
        liz.addContextMenuItems(contextMenu)
                 
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&previous="+urllib.quote_plus(previous)
        
    if infoList == False:
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "mediatype": content_type})
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
        
    if infoArt != False:
        liz.setArt(infoArt) 
        
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
      
def addLink(name,description,url,previous,mode,thumb=ICON,icon=ICON,fanart=FANART,infoList=False,infoArt=False,showcontext=False,total=0):
    log('addLink') 
    liz = xbmcgui.ListItem(name)
    liz.setIconImage(icon)
    liz.setThumbnailImage(thumb)
    liz.setProperty("Fanart_Image", fanart)
    liz.setProperty('IsPlayable', 'true')
    
    if showcontext == True:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
        liz.addContextMenuItems(contextMenu)
                
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&previous="+urllib.quote_plus(previous)
                
    if infoList == False:
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description})
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
    
    if infoArt != False:
        liz.setArt(infoArt) 
        
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,totalItems=total)

def getProperty(str):
    return xbmcgui.Window(10000).getProperty(str)

def setProperty(str1, str2):
    xbmcgui.Window(10000).setProperty(str1, str2)

def clearProperty(str):
    xbmcgui.Window(10000).clearProperty(str)

def sendJSON(command):
    log('sendJSON')
    data = ''
    try:
        data = xbmc.executeJSONRPC(uni(command))
    except UnicodeEncodeError:
        data = xbmc.executeJSONRPC(ascii(command))
    return uni(data)
           
def requestItem(file, fletype='video'):
    log("requestItem") 
    json_query = ('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":1,"properties":["thumbnail","fanart","title","year","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}')
    json_folder_detail = sendJSON(json_query)
    return re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)
          
def requestList(path, fletype='video'):
    log("requestList, path = " + path) 
    json_query = ('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "%s", "properties":["thumbnail","fanart","title","year","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}'%(path,fletype))
    json_folder_detail = sendJSON(json_query)
    return re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)      
   
def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other'):
    log('fillPluginItems')
    if not file_type:
        detail = uni(requestList(url, media_type))
    else:
        detail = uni(requestItem(url, media_type))
    for f in detail:
        files = re.search('"file" *: *"(.*?)",', f)
        filetypes = re.search('"filetype" *: *"(.*?)",', f)
        labels = re.search('"label" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        
        if filetypes and labels and files:
            filetype = filetypes.group(1)
            label = cleanLabels(labels.group(1))
            file = (files.group(1).replace("\\\\", "\\"))
            
            if not descriptions:
                description = ''
            else:
                description = cleanLabels(descriptions.group(1))
                
            thumbnail = removeNonAscii(thumbnails.group(1))
            fan = removeNonAscii(fanarts.group(1))
            
            if REAL_SETTINGS.getSetting('Link_Type') == '0':
                link = sys.argv[0]+"?url="+urllib.quote_plus(file)+"&mode="+str(10)+"&name="+urllib.quote_plus(label)
            else:
                link = file
            
            if strm_type in ['TV','Episodes']:
                path = os.path.join('TV',strm_name)
                filename = strm_name + ' - ' + label
                print path, filename
                
            if filetype == 'file':
                if strm:
                    writeSTRM(cleanStrms(path), cleanStrms(filename) ,link)
                else:
                    addLink(label,description,file,'',5001,thumb=thumbnail,fanart=fan,total=len(detail))
            else:
                if strm:
                    fillPluginItems(file, media_type, file_type, strm, label, strm_type)
                else:
                    addDir(label,description,file,'',6002,thumb=thumbnail,fanart=fan)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
def fillPlugins(type='video'):
    log('fillPlugins, type = ' + type)
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary"]}, "id": 1 }'%type)
    json_detail = sendJSON(json_query)
    detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_detail)
    for f in detail:
        names = re.search('"name" *: *"(.*?)",', f)
        paths = re.search('"addonid" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        if not descriptions:
            descriptions = re.search('"summary" *: *"(.*?)",', f)
        if descriptions:
            description = cleanLabels(descriptions.group(1))
        else:
            description = ''
        if names and paths:
            name = cleanLabels(names.group(1))
            path = paths.group(1)
            if type == 'video' and path.startswith('plugin.video') and not path.startswith('plugin.video.pseudo.companion'):
                thumbnail = removeNonAscii(thumbnails.group(1))
                fan = removeNonAscii(fanarts.group(1))
                addDir(name,description,'plugin://'+path,'',6002,thumb=thumbnail,fanart=fan)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def getSources():
    log('getSources')
    STATE = getProperty('PseudoCompanion.STATE') == 'true'
    STATUS = getProperty('PseudoCompanion.STATUS')
    if STATE == True:
        addDir('PseudoTV Live: '+STATUS,'','','getSources',9000,PTVL_ICON,PTVL_ICON)
    else:
        addDir('PseudoTV Live: '+STATUS,'','','getSources','',PTVL_ICON_GRAY,PTVL_ICON_GRAY)
    addDir('Channel Tools','','','',9001)

def getOnline():
    log('getOnline')
    # NowWatching()
    addDir('On Now','What On Now!','','',1,PTVL_ICON,PTVL_ICON)
    # addDir('On Next','What On Next!','','',2,PTVL_ICON,PTVL_ICON)
    addDir('Channel Guide','Channel Listing','','',3,PTVL_ICON,PTVL_ICON)
    addDir('Scheduled Reminders','Coming Soon','','',4,PTVL_ICON,PTVL_ICON)
    addDir('Scheduled Recordings','Coming Soon','','',5,PTVL_ICON,PTVL_ICON)
    addDir('Recorded TV','Coming Soon','','',6,PTVL_ICON,PTVL_ICON)
    addDir('Sidebar','Sidebar Controls','','',7,PTVL_ICON,PTVL_ICON)
    addDir('Misc.','','','',8,PTVL_ICON,PTVL_ICON)
    
def getMisc():
    getDEBUG()
    getStatus()
    
    
def getStatus():
    title = getProperty('PTVL.NOTIFY_LOG')
    debug_icon = os.path.join(ADDON_PATH,'resources','images','debug.png')
    label = 'STATUS:'
    content_type = 'movie'
    infoList = {}
    infoList['mediatype']     = content_type
    infoList['TVShowTitle']   = label
    infoList['Genre']         = title
    infoList['Title']         = label
    infoList['Studio']        = label
    infoList['Year']          = '0'
    addDir(label, title,'','getMisc','',debug_icon,debug_icon,'',infoList)
    
def getDEBUG(): 
    title = getProperty('PTVL.DEBUG_LOG')
    debug_icon = os.path.join(ADDON_PATH,'resources','images','debug.png')
    label = 'DEBUG:'
    content_type = 'movie'
    infoList = {}
    infoList['mediatype']     = content_type
    infoList['TVShowTitle']   = label
    infoList['Genre']         = title
    infoList['Title']         = label
    infoList['Studio']        = label
    infoList['Year']          = '0'
    addDir(label, title,'','getMisc','',debug_icon,debug_icon,'',infoList)
                
def getTools():
    addDir('Media Sources','','','',8000)
    addDir('Channel Manager','','','',8001)
    
def getMedia():
    log('getMedia')
    addDir('BCT Sources','','','',7000)
    addDir('BringThePopcorn','','','',7001)
    addDir('PseudoCinema','','','',7002)
    addDir('Local Media','','','',7003)
    
def getLocal():
    log('getLocal') 
    addDir('Browse Local Video','','video','',6000)
    addDir('Browse Local Music','','music','',6000)
    addDir('Browse Plugin Video ','','video','',6001)
    addDir('Browse Plugin Music','','music','',6001)
    addDir('Browse PVR Backend','','pvr://','',6002)
    addDir('Browse UPNP Servers','','upnp://','',6002)
        
def getSideBar():
    NowWatching()
    addDir('OnNow','What On Now!','','',1,PTVL_ICON,PTVL_ICON)
    addDir('Browse','','','',4000)
    addDir('Search','','','',4001)
    addDir('Last Channel','','','',9999)
    addDir('Favorites','','','',9999)
    addDir('Favorites Flip','','','',9999)
    addDir('EPGType','','','',9999)
    addDir('Mute','','','',9999)
    addDir('Subtitle','','','',9999)
    addDir('Player Settings','','','',9999)
    addDir('Sleep','','','',9999)
    addDir('Exit','','','',9999)
    
def getReminders():
    log('getReminders')
    try:
        ReminderLst = eval(getProperty("PTVL.ReminderLst"))
        if ReminderLst and len(ReminderLst) > 0:
            for n in range(len(ReminderLst)):
                lineLST = ReminderLst[n]
                record  =  lineLST['Record'] == 'True'
                chtype  =  lineLST['Chtype']
                tmpDate =  lineLST['TimeStamp']
                title   =  lineLST['Title']
                SEtitle =  lineLST['SEtitle']
                chnum   =  lineLST['Chnum']
                chname  =  lineLST['Chname']
                poster  =  lineLST['poster']
                fanart  =  lineLST['fanart']
                chlogo  =  lineLST['LOGOART']
                Notify_Time, epochBeginDate = cleanReminderTime(tmpDate)          
                now = time.time()
                if epochBeginDate > now:
                    label = ('[B]%s[/B] on channel [B]%s[/B] at [B]%s[/B]'%(title, chnum, str(Notify_Time)))
                    content_type = 'tvshow'
                    infoList = {}
                    infoList['mediatype']     = content_type
                    infoList['TVShowTitle']   = str(Notify_Time)
                    infoList['Genre']         = str(Notify_Time)
                    infoList['Title']         = title
                    infoList['Studio']        = 'chname'
                    infoList['Year']          = int(chnum or '0')
                    
                    infoArt = {}
                    infoArt['thumb']        = poster
                    infoArt['poster']       = poster
                    infoArt['fanart']       = fanart
                    infoArt['landscape']    = fanart
                    infoList['icon']        = chlogo
                    addDir(label, Notify_Time, str(chnum),'getReminders',10000,poster,chlogo,fanart,infoList,infoArt,content_type)
        else:
            raise Exception()
    except Exception,e:
        addDir('No Reminders Set','','','','',PTVL_ICON,PTVL_ICON)
            
def cleanReminderTime(tmpDate):
    try:#sloppy fix, for threading issue with strptime.
        t = time.strptime(tmpDate, '%Y-%m-%d %H:%M:%S')
    except:
        t = time.strptime(tmpDate, '%Y-%m-%d %H:%M:%S')
    Notify_Time = time.strftime('%I:%M%p, %A', t)
    epochBeginDate = time.mktime(t)
    return Notify_Time, epochBeginDate    
        
def ChannelGuide():
    log('ChannelGuide') 
    try:
        GuideLst = eval(getProperty("OVERLAY.ChannelGuide"))
        GuideLst.sort(key=lambda x:x['Chnum'])
        
        for i in range(len(GuideLst)):
            GuideLstItem = GuideLst[i]
            content_type = 'episode'
            chnum  = GuideLstItem['Chnum']
            chname = GuideLstItem['Chname']
            chtype = GuideLstItem['Chtype']
            chlogo = GuideLstItem['LOGOART']
            label  = ('%d| %s' %(chnum, chname))
            
            infoList = {}
            infoList['mediatype']     = content_type
            infoList['title']         = chname
            infoList['tvshowtitle']   = getChanTypeLabel(chtype)
            infoList['season']        = 0
            infoList['episode']       = chnum
            addDir(label,'',str(chnum),'ChannelGuide',10000,chlogo,chlogo,chlogo,infoList,False,content_type)
    except:
        addDir('Try Again Later','','','',PTVL_ICON,PTVL_ICON)
            
def getChanTypeLabel(chantype):
    if chantype == 0:
        return "Custom Playlist"
    elif chantype == 1:
        return "TV Network"
    elif chantype == 2:
        return "Movie Studio"
    elif chantype == 3:
        return "TV Genre"
    elif chantype == 4:
        return "Movie Genre"
    elif chantype == 5:
        return "Mixed Genre"
    elif chantype == 6:
        return "TV Show"
    elif chantype == 7:
        return "Directory"
    elif chantype == 8:
        return "LiveTV"
    elif chantype == 9:
        return "InternetTV"
    elif chantype == 10:
        return "Youtube"
    elif chantype == 11:
        return "RSS"
    elif chantype == 12:
        return "Music (Coming Soon)"
    elif chantype == 13:
        return "Music Videos (Coming Soon)"
    elif chantype == 14:
        return "Exclusive (Coming Soon)"
    elif chantype == 15:
        return "Plugin"
    elif chantype == 16:
        return "UPNP"
    elif chantype == 9999:
        return "None"
    return ''
        
def OnNow(next=False):
    log('OnNow')
    try:
        if next == True:
            previous = 'OnNext'
            OnNowLst = eval(getProperty("OVERLAY.OnNextLst"))
            OnNextLst = []
        else:
            previous = 'OnNow'
            OnNowLst = eval(getProperty("OVERLAY.OnNowLst"))
            OnNextLst = eval(getProperty("OVERLAY.OnNextLst"))
       
        OnNowLst.sort(key=lambda x:x['Chnum'])
        OnNextLst.sort(key=lambda x:x['Chnum'])
        
        for i in range(len(OnNowLst)):
            OnNowLine = OnNowLst[i]
            OnNextLine = OnNextLst[i]
            
            content_type = 'tvshow'
            type         = OnNowLine['content_type']
            title        = OnNowLine['Title']
            rating       = OnNowLine['Rating']
            nextTitle    = OnNextLine['Title']
            SEtitle      = OnNowLine['SEtitle']
            nextSEtitle  = OnNextLine['SEtitle']
            tagline      = OnNowLine['Tagline']
            nexttagline  = OnNextLine['Tagline']
            chname       = OnNowLine['Chname']
            chnum        = OnNowLine['Chnum']
            chtype       = OnNowLine['Chtype']
            season       = OnNowLine['Season']
            episode      = OnNowLine['Episode'] 
            playcount    = OnNowLine['Playcount']
            description  = OnNowLine['Description']
            poster       = OnNowLine['poster']
            fanart       = OnNowLine['fanart']
            chlogo       = OnNowLine['LOGOART']
            label        = ('%d| %s' %(chnum, title))
            
            # if type in ['tvshow','episode']:
                # title = ('%s - %s' % (title,SEtitle))
                
            # setup infoList
            infoList = {}
            infoList['mediatype']     = content_type
            infoList['MPAA']          = rating
            infoList['TVShowTitle']   = 'Next: ' + nextTitle
            infoList['Genre']         = 'Next: ' + nextTitle
            infoList['Title']         = title
            infoList['Studio']        = chname
            infoList['Year']          = int(chnum or '0')
            infoList['Season']        = int(season or '0')
            infoList['Episode']       = int(episode or '0')
            infoList['playcount']     = int(playcount or '0')
            # setup infoArt
            infoArt = {}
            infoArt['thumb']        = poster
            infoArt['poster']       = poster
            infoArt['fanart']       = fanart
            infoArt['landscape']    = fanart
            infoList['icon']        = chlogo
            url = str({'content_type': content_type, 'Rating': rating, 'Description': description, 'Title': title, 'Chname': chname, 'Chname': chname, 'Chnum': chnum, 'Season': season, 'Episode': episode, 'playcount': playcount, 'poster': poster, 'fanart': fanart, 'chlogo': chlogo})
            addDir(label,OnNowLine['Description'],str(chnum),previous,10000,poster,chlogo,fanart,infoList,infoArt,content_type)
    except:
        addDir('Try Again Later','','','',PTVL_ICON,PTVL_ICON)
     
def PreviewChannel(name, url, previous):
    log('PreviewChannel')
    PreviewLine = eval(url)
    content_type = 'tvshow' 
    infoList = {}
    infoList['mediatype']     = PreviewLine['content_type']
    infoList['MPAA']          = PreviewLine['Rating']
    infoList['TVShowTitle']   = PreviewLine['Description']
    infoList['Genre']         = PreviewLine['Description']
    infoList['Title']         = PreviewLine['Title']
    infoList['Studio']        = PreviewLine['Chname']
    infoList['Year']          = int(PreviewLine['Chnum'] or '0')
    infoList['Season']        = int(PreviewLine['Season'] or '0')
    infoList['Episode']       = int(PreviewLine['Episode'] or '0')
    infoList['playcount']     = int(PreviewLine['playcount'] or '0')
    
    infoArt = {}
    infoArt['thumb']        = PreviewLine['poster']
    infoArt['poster']       = PreviewLine['poster']
    infoArt['fanart']       = PreviewLine['fanart']
    infoArt['landscape']    = PreviewLine['fanart']
    infoList['icon']        = PreviewLine['chlogo']
    
    addDir(name,PreviewLine['Description'],str(PreviewLine['Chnum']),previous,10000,PreviewLine['poster'],PreviewLine['chlogo'],PreviewLine['fanart'],infoList,infoArt,content_type)
        
def InputChannel(channel, previous):
    log('InputChannel = ' + str(channel))
    for n in range(len(str(channel))):  
        json_query = ('{"jsonrpc":"2.0","method":"Input.ExecuteAction","params":{"action":"number%s"},"id":2}') % (str(channel)[n])
        sendJSON(json_query)
    back(previous)
    
def NowWatching():
    log('NowWatching')
    content_type = 'tvshow' 
    infoList = {}
    infoList['mediatype']     = content_type
    infoList['MPAA']          = getProperty("OVERLAY.Rating")
    infoList['TVShowTitle']   = 'Next: ' + getProperty("OVERLAY.NEXT.Title")
    infoList['Genre']         = 'Next: ' + getProperty("OVERLAY.NEXT.Title")
    infoList['Title']         = 'Now: ' + getProperty("OVERLAY.Title")
    infoList['Studio']        = getProperty("OVERLAY.Chname")
    infoList['Year']          = int(getProperty("OVERLAY.Chnum") or '0')
    infoList['Season']        = int(getProperty("OVERLAY.Season") or '0')
    infoList['Episode']       = int(getProperty("OVERLAY.Episode") or '0')
    infoList['playcount']     = int(getProperty("OVERLAY.Playcount") or '0')
    
    infoArt = {}
    infoArt['thumb']        = getProperty("OVERLAY.poster")
    infoArt['poster']       = getProperty("OVERLAY.poster")
    infoArt['banner']       = getProperty("OVERLAY.banner")
    infoArt['fanart']       = getProperty("OVERLAY.fanart")
    infoArt['clearart']     = getProperty("OVERLAY.clearart")
    infoArt['clearlogo']    = getProperty("OVERLAY.clearlogo")
    infoArt['landscape']    = getProperty("OVERLAY.landscape")
    
    addDir('1',getProperty("OVERLAY.Description"),getProperty("OVERLAY.Chnum"),'getOnline',10000,getProperty("OVERLAY.poster"),getProperty("OVERLAY.LOGOART"),getProperty("OVERLAY.landscape"),infoList,infoArt,content_type)
        
def getLocalVideo():
    comingsoon()
    
def comingsoon():
    addDir('ComingSoon','','','','')
        
def getPTVLManager():
    log('getPTVLManager')
    comingsoon()
    
def getControls():
    log('getControls')
    comingsoon()
    
def getPTVLGuide():
    log('getPTVLGuide')
    comingsoon()
    
def getRecordings():
    log('getRecordings')
    comingsoon()
    
def getRecorded():
    log('getRecorded')
    comingsoon()
    
def getBCTs():
    log('getBCTs')
    comingsoon()
    
def getPopcorn():
    log('getPopcorn')
    comingsoon()
    
def getCinema():
    log('getCinema')
    comingsoon()

def back(parent):
    log('back')
    if parent == 'Main':
        addDir('-Back to Main Menu','','','',None)
    elif parent == 'Online':
        addDir('-Back to PTVL Menu','','','',9000,PTVL_ICON,PTVL_ICON)
    elif parent == 'Tools':
        addDir('-Back to PTVL Menu','','','',8000,PTVL_ICON,PTVL_ICON)
    elif parent == 'Local':
        addDir('-Back to PTVL Menu','','','',7003,PTVL_ICON,PTVL_ICON)
    elif parent == 'ChannelGuide':
        ChannelGuide()
    elif parent == 'OnNow':
        OnNow()
    elif parent == 'OnNext':
        OnNow(next=True)
    elif parent == 'getReminders':
        getReminders()
        
def playURL(url):
    log('playURL')
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def getURL(par):
    log('getURL')
    try:
        url = par.split('?url=')[1]
        url = url.split('&mode=')[0]
    except:
        url = None
    return url
    
def get_params():
    log('get_params')
    param=[]
    paramstring=sys.argv[2]
    log('paramstring = ' + paramstring)
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
    log('param = ' + str(param))
    return param

params=get_params()

try:
    url=urllib.unquote_plus(params["url"]).decode('utf-8')
except:
    url=getURL(sys.argv[2])
try:
    name=urllib.unquote_plus(params["name"])
except:
    name=''
try:
    previous=urllib.unquote_plus(params["previous"])
except:
    previous = None
try:
    mode=int(params["mode"])
    log("Mode: "+str(mode))
except:
    mode=None
    
if not url is None:
    log("URL: "+str(url.encode('utf-8')))
log("Name: "+str(name))

if mode == None: getSources()

elif mode == -1: print 'null'

#getOnline
elif mode == 0: NowWatching()
elif mode == 1: OnNow()
elif mode == 2: OnNow(next=True)
elif mode == 3: ChannelGuide()
elif mode == 4: getReminders()
elif mode == 5: getRecordings()
elif mode == 6: getRecorded()
elif mode == 7: getSideBar()
elif mode == 8: getMisc()

#sidebar
elif mode == 4000: getLocal()
elif mode == 4001: comingsoon()
elif mode == 4002: comingsoon()
elif mode == 4003: comingsoon()
elif mode == 4004: comingsoon()
elif mode == 4005: comingsoon()

#misc
elif mode == 5000: getPTVLGuide()
elif mode == 5001: playURL(url)

#getLocal
elif mode == 6000: getLocalVideo()
elif mode == 6001: fillPlugins(url)
elif mode == 6002: fillPluginItems(url)

#getMedia
elif mode == 7000: getBCTs()
elif mode == 7001: getPopcorn()
elif mode == 7002: getCinema()
elif mode == 7003: getLocal()

#getTools
elif mode == 8000: getMedia()
elif mode == 8001: getPTVLManager()

#getSources
elif mode == 9000: getOnline()
elif mode == 9001: getTools()

#PTVL Json Input
elif mode == 9999: sendJSON(url)

#PTVL Channel Input
elif mode == 10000: InputChannel(int(url),previous)

#PTVL Pre-Channel Input
elif mode == 10001: PreviewChannel(name,url,previous)

# if mode in [0,1,2,3,4,5,6]: back('Online')                      # Return to Online Menu
# elif mode in [9995,9999]: back('Main')                        # Return to Main Menu

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False) # End List
