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


import os, re, sys, time, zipfile, threading, requests, random
import urllib, urllib2, base64, fileinput, shutil, socket, httplib, json
import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
import urlparse, time, _strptime, string, datetime, ftplib, hashlib, smtplib, feedparser, imp

from Globals import * 
from FileAccess import *  
from Queue import Queue
from HTMLParser import HTMLParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from xml.dom.minidom import parse, parseString
from urllib import unquote
socket.setdefaulttimeout(30)

# Commoncache plugin import
try:
    import StorageServer
except Exception,e:
    import storageserverdummy as StorageServer

# Globals    
Path = xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'skins', 'Default', '1080i')) #Path to Default PTVL skin, location of mod file.
fle = 'custom_script.pseudotv.live_9506.xml' #mod file, copy to xbmc skin folder
VWPath = xbmc.translatePath(os.path.join(XBMC_SKIN_LOC, fle))
flePath = xbmc.translatePath(os.path.join(Path, fle))
PTVL_SKIN_SELECT_FLE = xbmc.translatePath(os.path.join(PTVL_SKIN_SELECT, 'script.pseudotv.live.EPG.xml'))         
DSPath = xbmc.translatePath(os.path.join(XBMC_SKIN_LOC, 'DialogSeekBar.xml'))

# Videowindow Patch
a = '<!-- PATCH START -->'
b = '<!-- PATCH START --> <!--'
c = '<!-- PATCH END -->'
d = '--> <!-- PATCH END -->'

# Seekbar Patch
v = ' '
w = '<visible>Window.IsActive(fullscreenvideo) + !Window.IsActive(script.pseudotv.TVOverlay.xml) + !Window.IsActive(script.pseudotv.live.TVOverlay.xml)</visible>'
y = '</defaultcontrol>'
z = '</defaultcontrol>\n    <visible>Window.IsActive(fullscreenvideo) + !Window.IsActive(script.pseudotv.TVOverlay.xml) + !Window.IsActive(script.pseudotv.live.TVOverlay.xml)</visible>'

################
# Github Tools #
################
     
def fillGithubItems(url, ext, removeEXT=False):
    log("utils: fillGithubItems Cache")
    if CHKCache() == True:
        try:
            setProperty("PTVL.CHKCache", "false")
            result = parsersGH.cacheFunction(fillGithubItems_NEW, url, ext, removeEXT)
            setProperty("PTVL.CHKCache", "true")
        except:
            result = fillGithubItems_NEW(url, ext, removeEXT)
            pass
    else:
        result = fillGithubItems_NEW(url, ext, removeEXT)
    if not result:
        result = []
    return result  
    
def fillGithubItems_NEW(url, ext, removeEXT=False):
    log("utils: fillGithubItems_NEW")
    Sortlist = []
    try:
        list = []
        response = request_url(url)
        catlink = re.compile('title="(.+?)">').findall(response)
        for i in range(len(catlink)):
            link = catlink[i]
            name = (catlink[i]).lower()
            if ([x.lower for x in ext if name.endswith(x)]):
                if removeEXT == True:
                    link = os.path.splitext(os.path.basename(link))[0]
                list.append(link.replace('&amp;','&'))
        Sortlist = sorted_nicely(list) 
    except Exception,e:
        print str(e)
        pass
    return Sortlist

def VersionCompare():
    log('utils: VersionCompare')
    curver = xbmc.translatePath(os.path.join(ADDON_PATH,'addon.xml'))    
    source = open(curver, mode = 'r')
    link = source.read()
    source.close()
    match = re.compile('" version="(.+?)" name="PseudoTV Live"').findall(link)
    
    for vernum in match:
        log("utils: Current Version = " + str(vernum))
    try:
        link = request_url('https://raw.githubusercontent.com/Lunatixz/XBMC_Addons/master/script.pseudotv.live/addon.xml')  
        link = link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')
        match = re.compile('" version="(.+?)" name="PseudoTV Live"').findall(link)
    except:
        pass   
        
    if len(match) > 0:
        print vernum, str(match)[0]
        if vernum != str(match[0]):
            if not isPlugin('repository.lunatixz'):
                dialog = xbmcgui.Dialog()
                confirm = xbmcgui.Dialog().yesno('[B]PseudoTV Live Update Available![/B]', "Your version is outdated." ,'The current available version is '+str(match[0]),'Would you like to install the PseudoTV Live repository to stay updated?',"Cancel","Install")
                if confirm:
                    UpdateFiles()
            else:
                get_Kodi_JSON('"method":"Addons.SetAddonEnabled","params":{"addonid":"repository.lunatixz","enabled":true}')

def UpdateFiles():
    log('utils: UpdateFiles')
    url='https://github.com/Lunatixz/XBMC_Addons/raw/master/zips/repository.lunatixz/repository.lunatixz-1.0.zip'
    name = 'repository.lunatixz.zip' 
    MSG = 'Lunatixz Repository Installed'    
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    addonpath = xbmc.translatePath(os.path.join('special://','home/addons'))
    lib = os.path.join(path,name)
    log('utils: URL = ' + url)
    
    # Delete old install package
    try: 
        FileAccess.delete(lib)
        log('utils: deleted old package')
    except: 
        pass
        
    try:
        download(url, lib, '')
        log('utils: downloaded new package')
        all(lib,addonpath,'')
        log('utils: extracted new package')
    except: 
        MSG = 'Failed to install Lunatixz Repository, Try Again Later'
        pass
        
    xbmc.executebuiltin("XBMC.UpdateLocalAddons()"); 
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", MSG, 1000, THUMB) )
    return
 
#############
# Art Tools #
#############

# def PreArtService():
    # ADDON_SETTINGS.loadSettings()
    # exclude = ['#EXTM3U', '#EXTINF']
    # i = 0
    # lineLST = []
    # newLST = []
    # ArtLST = []
    
    # for i in range(999):
        # try:
            # try:
                # chtype = int(ADDON_SETTINGS.getSetting('Channel_' + str(i) + '_type'))
                # chname = (self.channels[i - 1].name)
                # fle = xbmc.translatePath(os.path.join(LOCK_LOC, ("channel_" + str(i) + '.m3u')))  
            # except Exception,e:
                # chtype = -1
                # fle = ''
                # pass
            
            # if chtype >= 0 and fle != '':
                # if FileAccess.exists(fle):
                    # f = FileAccess.open(fle, 'r')
                    # lineLST = f.readlines()
                    # lineLST.pop(0) #Remove unwanted first line '#EXTM3U'
                    # for n in range(len(lineLST)):
                        # line = lineLST[n]
                        
                        # if line[0:7] == '#EXTINF':
                            # liveid = line.rsplit('//',1)[1]
                            # type = liveid.split('|')[0]
                            # id = liveid.split('|')[1]
                            # dbid = liveid.split('|')[2]
                            
                        # elif line[0:7] not in exclude:
                            # if id != -1:
                                # if line[0:5] == 'stack':
                                    # smpath = (line.split(' , ')[0]).replace('stack://','').replace('rar://','')
                                    # mpath = (os.path.split(smpath)[0]) + '/'
                                # elif line[0:6] == 'plugin':
                                    # mpath = 'plugin://' + line.split('/')[2] + '/'
                                # elif line[0:4] == 'upnp':
                                    # mpath = 'upnp://' + line.split('/')[2] + '/'
                                # else:
                                    # mpath = (os.path.split(line)[0]) + '/'

                                # if type and mpath:
                                    # newLST = [type, chtype, chname, id, dbid, mpath]
                                    # ArtLST.append(newLST)
        # except:
            # pass
    # # shuffle list to evenly distribute queue
    # random.shuffle(ArtLST)
    # log('utils: PreArtService, ArtLST Count = ' + str(len(ArtLST)))
    # return ArtLST

        
    # def ArtService(self):
        # if getProperty("PTVL.BackgroundLoading_Finished") == "true" and getProperty("ArtService_Running") == "false":
            # setProperty("ArtService_Running","true")
            # start = datetime.datetime.today()
            # ArtLst = self.PreArtService() 
            # Types = []
            # cnt = 0
            # subcnt = 0
            # totcnt = 0
            # lstcnt = int(len(ArtLst))
            
            # if NOTIFY == True:
                # xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Artwork Spooler Started", 4000, THUMB) )
            
            # # Clear Artwork Cache Folders
            # if REAL_SETTINGS.getSetting("ClearLiveArtCache") == "true":
                # artwork.delete("%") 
                # artwork1.delete("%")
                # artwork2.delete("%")
                # artwork3.delete("%")
                # artwork4.delete("%")
                # artwork5.delete("%")
                # artwork6.delete("%")
                # log('utils: ArtService, ArtCache Purged!')
                # REAL_SETTINGS.setSetting('ClearLiveArtCache', "false")
                
                # if NOTIFY == True:
                    # xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Artwork Cache Cleared", 4000, THUMB) )
                # xbmc.sleep(5)
                
            # if getProperty("type1EXT_Overlay") != '':
                # Types.append(getProperty("type1EXT_Overlay"))
            # if getProperty("type2EXT_Overlay") != '':
                # Types.append(getProperty("type1EXT_Overlay"))
            # if getProperty("type3EXT_Overlay") != '':
                # Types.append(getProperty("type3EXT_Overlay"))    
              
            # try:
                # type1EXT_EPG = REAL_SETTINGS.getSetting('type1EXT_EPG')
                # if type1EXT_EPG != '':
                    # Types.append(type1EXT_EPG)
            # except:
                # pass        
            # try:
                # type2EXT_EPG = REAL_SETTINGS.getSetting('type2EXT_EPG')
                # if type2EXT_EPG != '':
                    # Types.append(type2EXT_EPG)
            # except:
                # pass
                
            # Types = remove_duplicates(Types)
            # log('utils: ArtService, Types = ' + str(Types))  
            
            # for i in range(lstcnt): 
                # if getProperty("PseudoTVRunning") == "True":
                    # setDefault = ''
                    # setImage = ''
                    # setBug = ''
                    # lineLST = ArtLst[i]
                    # type = lineLST[0]
                    # chtype = lineLST[1]
                    # chname = lineLST[2]
                    # id = lineLST[3]
                    # dbid = lineLST[4]
                    # mpath = lineLST[5]
                    # cnt += 1
                    
                    # self.Artdownloader.FindLogo(chtype, chname, mpath)
                    
                    # for n in range(len(Types)):
                        # typeEXT = str(Types[n])
                        # if '.' in typeEXT:
                            # self.Artdownloader.FindArtwork(type, chtype, chname, id, dbid, mpath, typeEXT)
                            
                    # if NOTIFY == True:
                        # if lstcnt > 5000:
                            # quartercnt = int(round(lstcnt / 4))
                        # else:
                            # quartercnt = int(round(lstcnt / 2))
                        # if cnt > quartercnt:
                            # totcnt = cnt + totcnt
                            # subcnt = lstcnt - totcnt
                            # percnt = int(round((float(subcnt) / float(lstcnt)) * 100))
                            # cnt = 0
                            # MSSG = ("Artwork Spooler"+' % '+"%d complete" %percnt) 
                            # xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", MSSG, 4000, THUMB) )
                # else:
                    # return
                    
            # stop = datetime.datetime.today()
            # finished = stop - start
            # MSSG = ("Artwork Spooled in %d seconds" %finished.seconds) 
            # log('utils: ArtService, ' + MSSG)  
            # setProperty("ArtService_Running","false")
            # setProperty("PTVL.BackgroundLoading_Finished","true")
            # REAL_SETTINGS.setSetting("ArtService_LastRun",str(stop))
            
            # if NOTIFY == True:
                # xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", MSSG, 4000, THUMB) ) 

##############
# LOGO Tools #
##############
def CleanCHname(text):
    text = text.replace(" (uk)", "")
    text = text.replace(" (UK)", "")
    text = text.replace(" (us)", "")
    text = text.replace(" (US)", "")
    text = text.replace(" (en)", "")
    text = text.replace(" (EN)", "")
    text = text.replace(" hd", "")
    text = text.replace(" HD", "")
    text = text.replace(" PVR", "")
    text = text.replace(" LiveTV", "") 
    text = text.replace(" USTV", "")  
    text = text.replace(" USTVnow", "")  
    text = text.replace(" USTVNOW", "")  
    return text

def FindLogo_Threading(data):
    log("utils: FindLogo_Threading")
    chtype = data[0]
    chname = data[1]
    mpath = getMpath(data[2])
    url = ''
    LogoName = (chname + '.png')
    LogoFolder = os.path.join(LOGO_LOC,LogoName)

    if FileAccess.exists(LogoFolder) and REAL_SETTINGS.getSetting('LogoDB_Override') == "false":
        return
    else:
        if chtype in [0,1,8,9]:
            user_region = REAL_SETTINGS.getSetting('limit_preferred_region')
            user_type = REAL_SETTINGS.getSetting('LogoDB_Type')
            useMix = REAL_SETTINGS.getSetting('LogoDB_Fallback') == "true"
            useAny = REAL_SETTINGS.getSetting('LogoDB_Anymatch') == "true"
            url = findLogodb(chname, user_region, user_type, useMix, useAny)
            if url:
                return GrabLogo(url, chname)
        if chtype in [0,1,2,3,4,5,12,13,14]:
            url = findGithubLogo(chname)
            if url:
                return GrabLogo(url, chname) 
        if mpath and (chtype == 6 or chtype == 7):
            smpath = mpath.rsplit('/',2)[0] #Path Above mpath ie Series folder
            artSeries = xbmc.translatePath(os.path.join(smpath, 'logo.png'))
            artSeason = xbmc.translatePath(os.path.join(mpath, 'logo.png'))
            if FileAccess.exists(artSeries): 
                url = artSeries
            elif FileAccess.exists(artSeason): 
                url = artSeason
            if url:
                return GrabLogo(url, chname) 

            
def FindLogo(chtype, chname, mediapath=None):
    log("utils: FindLogo")
    try:
        try:
            if FindLogoThread.isAlive():
                FindLogoThread.cancel()
                FindLogoThread.join()
        except:
            pass
            
        data = [chtype, chname, mediapath]
        FindLogoThread = threading.Timer(0.5, FindLogo_Threading, [data])
        FindLogoThread.name = "FindLogoThread"
        FindLogoThread.start()
    except Exception,e:
        log('utils: FindLogo, Failed!,' + str(e))
        pass   
         
def findGithubLogo(chname): 
    log("utils: findGithubLogo")
    url = ''
    baseurl='https://github.com/Lunatixz/PseudoTV_Logos/tree/master/%s' % chname[0]
    Studiolst = fillGithubItems(baseurl, '.png', removeEXT=True)
    if not Studiolst:
        miscurl='https://github.com/Lunatixz/PseudoTV_Logos/tree/master/0'
        Misclst = fillGithubItems(miscurl, '.png', removeEXT=True)
        for i in range(len(Misclst)):
            Studio = Misclst[i]
            cchname = CleanCHname(chname)
            if uni((Studio).lower()) == uni(cchname.lower()):
                url = 'https://raw.githubusercontent.com/Lunatixz/PseudoTV_Logos/master/0/'+((Studio+'.png').replace('&','&amp;').replace(' ','%20'))
                log('utils: findGithubLogo, Logo Match: ' + Studio.lower() + ' = ' + (Misclst[i]).lower())
                break
    else:
        for i in range(len(Studiolst)):
            Studio = Studiolst[i]
            cchname = CleanCHname(chname)
            if uni((Studio).lower()) == uni(cchname.lower()):
                url = 'https://raw.githubusercontent.com/Lunatixz/PseudoTV_Logos/master/'+chname[0]+'/'+((Studio+'.png').replace('&','&amp;').replace(' ','%20'))
                log('utils: findGithubLogo, Logo Match: ' + Studio.lower() + ' = ' + (Studiolst[i]).lower())
                break
    return url
           
def findLogodb(chname, user_region, user_type, useMix=True, useAny=True):
    log("utils: findLogodb Cache")   
    if CHKCache() == True:
        try:
            setProperty("PTVL.CHKCache", "false")
            result = daily.cacheFunction(findLogodb_NEW, chname, user_region, user_type, useMix, useAny)
            setProperty("PTVL.CHKCache", "true")
        except:
            result = findLogodb_NEW(chname, user_region, user_type, useMix, useAny)
            pass
    else:
        result = findLogodb_NEW(chname, user_region, user_type, useMix, useAny)
    if not result:
        result = ''
    return result  
     
def findLogodb_NEW(chname, user_region, user_type, useMix=True, useAny=True):
    try:
        clean_chname = (CleanCHname(chname))
        urlbase = 'http://www.thelogodb.com/api/json/v1/%s/tvchannel.php?s=' % LOGODB_API_KEY
        chanurl = (urlbase+clean_chname).replace(' ','%20')
        log("utils: findLogodb_NEW, chname = " + chname + ', clean_chname = ' + clean_chname + ', url = ' + chanurl)
        typelst =['strLogoSquare','strLogoSquareBW','strLogoWide','strLogoWideBW','strFanart1']
        user_type = typelst[int(user_type)]   
        response = request_url(chanurl)
        detail = re.compile("{(.*?)}", re.DOTALL ).findall(response)
        MatchLst = []
        mixRegionMatch = []
        mixTypeMatch = []
        image = ''
        
        for f in detail:
            try:
                regions = re.search('"strCountry" *: *"(.*?)"', f)
                channels = re.search('"strChannel" *: *"(.*?)"', f)
                if regions:
                    region = regions.group(1)
                if channels:
                    channel = channels.group(1)
                    for i in range(len(typelst)):
                        types = re.search('"'+typelst[i]+'" *: *"(.*?)"', f)
                        if types:
                            type = types.group(1)
                            if channel.lower() == clean_chname.lower():
                                if typelst[i] == user_type:
                                    if region.lower() == user_region.lower():
                                        MatchLst.append(type.replace('\/','/'))
                                    else:
                                        mixRegionMatch.append(type.replace('\/','/'))
                                else:
                                    mixTypeMatch.append(type.replace('\/','/'))
            except:
                pass
                
        if len(MatchLst) == 0:
            if useMix == True and len(mixRegionMatch) > 0:
                random.shuffle(mixRegionMatch)
                image = mixRegionMatch[0]
                log('utils: findLogodb_NEW, Logo NOMATCH useMix: ' + str(image))
            if not image and useAny == True and len(mixTypeMatch) > 0:
                random.shuffle(mixTypeMatch)
                image = mixTypeMatch[0]
                log('utils: findLogodb_NEW, Logo NOMATCH useAny: ' + str(image))
        else:
            random.shuffle(MatchLst)
            image = MatchLst[0]
            log('utils: findLogodb_NEW, Logo Match: ' + str(image))
        return image
        
    except Exception,e:
        log("utils: findLogodb_NEW, Failed! " + str(e))

def GrabLogo(url, Chname):
    log("utils: GrabLogo")
    print url
    if REAL_SETTINGS.getSetting('ChannelLogoFolder') != '':                 
        try:
            LogoFile = os.path.join(LOGO_LOC, Chname + '.png')
            url = url.replace('.png/','.png').replace('.jpg/','.jpg')
            
            if REAL_SETTINGS.getSetting('LogoDB_Override') == "true":
                try:
                    FileAccess.delete(LogoFile)
                except:
                    pass

            if not FileAccess.exists(LogoFile):
                if url.startswith('image'):
                    url = (unquote(url)).replace("image://",'')
                    if url.startswith('http'):
                        download_silent(url, LogoFile)
                    else:
                        FileAccess.copy(url, LogoFile) 
                elif url.startswith('http'):
                    download_silent(url, LogoFile)
                else:
                    FileAccess.copy(xbmc.translatePath(url), LogoFile) 
        except Exception,e:
            log("utils: GrabLogo, Failed! " + str(e))
     
#######################
# Communication Tools #
#######################

def GA_Request():
    log("GA_Request")
    """
    Simple proof of concept code to push data to Google Analytics.
    Related blog posts:
     * http://www.canb.net/2012/01/push-data-to-google-analytics-with.html
     * https://medium.com/python-programming-language/80eb9691d61f
    """
    try:
        PROPERTY_ID = os.environ.get("GA_PROPERTY_ID", "UA-45979766-1")

        if not REAL_SETTINGS.getSetting('Visitor_GA'):
            REAL_SETTINGS.setSetting('Visitor_GA', str(random.randint(0, 0x7fffffff)))
        VISITOR = str(REAL_SETTINGS.getSetting("Visitor_GA"))
        OPTIONS = ['PTVL',str(ADDON_VERSION),str(VISITOR)]
        
        if getProperty("Donor") == "true":
            USER,PASS = (REAL_SETTINGS.getSetting('Donor_UP')).split(':')
            OPTIONS = OPTIONS + ['Donor:'+USER]
        else:
            OPTIONS = OPTIONS+ ['FreeUser']
        
        if REAL_SETTINGS.getSetting('Hub') == 'true':  
            OPTIONS = OPTIONS + ['Hub:True']
        else:
            OPTIONS = OPTIONS + ['Hub:False']
        
        if getProperty("PTVL.COM_APP") == "true":
            USER = REAL_SETTINGS.getSetting('Gmail_User')
            OPTIONS = OPTIONS + ['Com:'+USER]
            
        OPTIONLST = "/".join(OPTIONS)
        DATA = {"utmwv": "5.2.2d",
        "utmn": str(random.randint(1, 9999999999)),
        "utmp": OPTIONLST,
        "utmac": PROPERTY_ID,
        "utmcc": "__utma=%s;" % ".".join(["1", VISITOR, "1", "1", "1", "1"])}
 
        URL = urlparse.urlunparse(("http",
        "www.google-analytics.com",
        "/__utm.gif",
        "",
        urllib.urlencode(DATA),
        ""))
        print urllib2.urlopen(URL).info()
    except Exception,e:  
        log("GA_Request Failed" + str(e), xbmc.LOGERROR)
        
def UpdateRSS():
    now  = datetime.datetime.today()
    try:
        UpdateRSS_LastRun = getProperty("UpdateRSS_NextRun")
        if not UpdateRSS_LastRun:
            raise
    except:
        UpdateRSS_LastRun = "1970-01-01 23:59:00.000000"
        setProperty("UpdateRSS_NextRun",UpdateRSS_LastRun)
    try:
        SyncUpdateRSS = datetime.datetime.strptime(UpdateRSS_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    except:
        UpdateRSS_LastRun = "1970-01-01 23:59:00.000000"
        SyncUpdateRSS = datetime.datetime.strptime(UpdateRSS_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    # log('utils: UpdateRSS, Now = ' + str(now) + ', UpdateRSS_NextRun = ' + str(UpdateRSS_LastRun))
    
    if now > SyncUpdateRSS:
        ##Push MSG
        pushlist = ''
        try:
            pushrss = 'https://raw.githubusercontent.com/Lunatixz/XBMC_Addons/master/push_msg.xml'
            file = request_url('https://raw.githubusercontent.com/Lunatixz/XBMC_Addons/master/push_msg.xml')
            pushlist = file.read()
            file.close()
        except:
            pass
        ##Github RSS
        gitlist = ''
        try:
            gitrss = 'https://github.com/Lunatixz.atom'
            d = feedparser.parse(gitrss)
            header = (d['feed']['title']).replace(' ',' Github ')
            post = d['entries'][0]['title']
            for post in d.entries:
                if post.title.startswith('Lunatixz pushed') and 'Lunatixz/XBMC_Addons' in post.title:
                    date = time.strftime("%m.%d.%Y @ %I:%M %p", post.date_parsed)
                    title = (post.title).replace('Lunatixz pushed to master at ','').replace('Lunatixz/XBMC_Addons','Updated repository plugins on')
                    gitlist += (header + ' - ' + title + ": " + date + "   ").replace('&amp;','&')
                    break
        except:
            pass
        ##Twitter RSS
        twitlist = ''
        try:
            twitrss ='http://feedtwit.com/f/pseudotv_live'
            e = feedparser.parse(twitrss)
            header = ((e['feed']['title']) + ' - ')
            twitlist = header
            for tost in e.entries:
                if '#PTVLnews' in tost.title:
                    date = time.strftime("%m.%d.%Y @ %I:%M %p", tost.published_parsed)
                    twitlist += (date + ": " + tost.title + "   ").replace('&amp;','&')
        except:
            pass
            
        UpdateRSS_NextRun = ((now + datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S.%f"))
        log('utils: UpdateRSS, Now = ' + str(now) + ', UpdateRSS_NextRun = ' + str(UpdateRSS_NextRun))
        setProperty("UpdateRSS_NextRun",str(UpdateRSS_NextRun))
        setProperty("twitter.1.label", pushlist)
        setProperty("twitter.2.label", gitlist)
        setProperty("twitter.3.label", twitlist)   
        
def sendGmail(subject, body, attach):
    GAuser = REAL_SETTINGS.getSetting('Visitor_GA')
    recipient = 'pseudotvsubmit@gmail.com'
    sender = REAL_SETTINGS.getSetting('Gmail_User')
    password = REAL_SETTINGS.getSetting('Gmail_Pass')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    if attach:
        log("utils: sendGmail w/Attachment")
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject + ", From:" + GAuser
        msg.attach(MIMEText(body))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
               'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)
        mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(sender, password)
        mailServer.sendmail(sender, recipient, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
    else:
        log("utils: sendGmail")
        body = "" + body + ""
        subject = subject + ", From:" + GAuser
        headers = ["From: " + sender,
                   "Subject: " + subject,
                   "To: " + recipient,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)        
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(sender, password)
        session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
        session.quit()
     
##################
# Download Tools #
##################

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
    try: 
        percent = min(numblocks * blocksize * 100 / filesize, 100) 
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
        kbps_speed = numblocks * blocksize / (time.time() - start_time) 
        if kbps_speed > 0: 
            eta = (filesize - numblocks * blocksize) / kbps_speed 
        else: 
            eta = 0 
        kbps_speed = kbps_speed / 1024 
        total = float(filesize) / (1024 * 1024) 
        mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
        e = 'Speed: %.02f Kb/s ' % kbps_speed 
        e += 'ETA: %02d:%02d' % divmod(eta, 60) 
        dp.update(percent, mbs, e)
    except: 
        percent = 100 
        dp.update(percent) 
    if dp.iscanceled(): 
        dp.close() 
  
  
def download(url, dest, dp = None):
    log('download')
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("PseudoTV Live","Downloading & Installing Files", ' ', ' ')
    dp.update(0)
    start_time=time.time()
    try:
        urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))
    except Exception,e:
        print str(e)
        pass
     
     
def download_silent_threading(data):
    log('download_silent_threading')
    try:
        urllib.urlretrieve(data[0], data[1])
    except Exception,e:
        print str(e)
        pass
     
     
def download_silent(url, dest):
    log('download_silent')
    try:
        try:
            if download_silentThread.isAlive():
                download_silentThread.cancel()
                download_silentThread.join()
        except:
            pass
            
        data = [url, dest]
        download_silentThread = threading.Timer(0.5, download_silent_threading, [data])
        download_silentThread.name = "download_silentThread"
        download_silentThread.start()
        # Sleep between Download, keeps cpu usage down and reduces the number of simultaneous threads.
        xbmc.sleep(1000)
    except Exception,e:
        log('utils: download_silent, Failed!,' + str(e))
        pass   

def open_url(url):        
    try:
        f = urllib2.urlopen(url)
        return f
    except urllib2.URLError as e:
        pass
    
def open_url_up(url, userpass):
    log("utils: open_url_up")
    try:
        userpass = userpass.split(':')
        username = userpass[0]
        password = userpass[1]
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = open_url(request)
        return result
    except:
        pass
        
def readline_url_cached(url, userpass=False): 
    if CHKCache() == True:
        try:
            setProperty("PTVL.CHKCache", "false")
            result = daily.cacheFunction(readline_url, url, userpass)
            setProperty("PTVL.CHKCache", "true")
        except:
            result = readline_url(url, userpass)
            pass
    else:
        result = readline_url(url, userpass)
    if not result:
        result = []
    return result 
           
def readline_url(url, userpass=False):        
    try:
        if userpass != False:
            f = open_url_up(url, userpass)
        else:
            f = open_url(url)
        return f.readlines()
    except urllib2.URLError as e:
        pass   
     
def request_url_cached(url):
    log('request_url_cached')
    if CHKCache() == True:
        try:
            setProperty("PTVL.CHKCache", "false")
            result = daily.cacheFunction(request_url, url)
            setProperty("PTVL.CHKCache", "true")
        except:
            result = request_url(url)
            pass
    else:
        result = request_url(url)
    if not result:
        result = []
    return result     
           
def request_url(url):
    try:
        req=urllib2.Request(url)
        req.add_header('User-Agent','Magic Browser')
        response=urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        pass   

def requestDownload(url, fle):
    log('utils: requestDownload')
    # requests = requests.Session()
    response = requests.get(url, stream=True)
    with open(fle, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    
def force_url(url):
    Con = True
    Count = 0
    while Con:
        if Count > 3:
            Con = False
        try:
            req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            return urllib2.urlopen(req)
            Con = False
        except URLError, e:
            print "Oops, timed out?"
            Con = True
        except socket.timeout:
            print "Timed out!"
            Con = True
            pass 
        Count += 1
     
def retrieve_url_up(url, userpass, dest):
    log("utils: retrieve_url_up")
    try:
        username, password = userpass.split(':')
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        resource = open_url(request)
        output = FileAccess.open(dest, 'w')
        output.write(resource.read())  
        output.close()
        return True
    except:
        pass

def download_url(_in, _out): 
    Finished = False    
    
    if FileAccess.exists(_out):
        try:
            os.remove(_out)
        except:
            pass
    try:
        resource = urllib.urlopen(_in)
        output = FileAccess.open(_out, 'w')
        output.write(resource.read())
        Finished = True    
        output.close()
    except:
        pass
    return Finished  

def anonFTPDownload(filename, DL_LOC):
    log('utils: anonFTPDownload, ' + filename + ' - ' + DL_LOC)
    try:
        ftp = ftplib.FTP("ftp.pseudotvlive.com", "PTVLuser@pseudotvlive.com", "PTVLuser")
        ftp.cwd("/")
        file = FileAccess.open(DL_LOC, 'w')
        ftp.retrbinary('RETR %s' % filename, file.write)
        file.close()
        ftp.quit()
        return True
    except Exception, e:
        log('utils: anonFTPDownload, Failed!! ' + str(e))
        return False
##################
# Zip Tools #
##################

def all(_in, _out, dp=None):
    if dp:
        return allWithProgress(_in, _out, dp)
    return allNoProgress(_in, _out)

def allNoProgress(_in, _out):
    try:
        zin = zipfile.ZipFile(_in, 'r')
        zin.extractall(_out)
    except Exception, e:
        return False
    return True

def allWithProgress(_in, _out, dp):
    zin = zipfile.ZipFile(_in,  'r')
    nFiles = float(len(zin.infolist()))
    count  = 0

    try:
        for item in zin.infolist():
            count += 1
            update = count / nFiles * 100
            dp.update(int(update))
            zin.extract(item, _out)
    except Exception, e:
        return False
    return True 
     
##################
# GUI Tools #
##################

def Comingsoon():
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Coming Soon", 1000, THUMB) )

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        time.sleep(.1)
        
def Error(header, line1= '', line2= '', line3= ''):
    dlg = xbmcgui.Dialog()
    dlg.ok(header, line1, line2, line3)
    del dlg
    
def showText(heading, text):
    log("utils: showText")
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def infoDialog(str, header=ADDON_NAME, time=4000):
    try: xbmcgui.Dialog().notification(header, str, THUMB, time, sound=False)
    except: xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (header, str, time, THUMB))

def Notify(header=ADDON_NAME, message="", icon=THUMB, time=5000, sound=False):
    xbmcgui.Dialog().notification(heading=header, message=message, icon=icon, time=time, sound=sound)

def okDialog(str1, str2='', header=ADDON_NAME):
    xbmcgui.Dialog().ok(header, str1, str2)

def selectDialog(list, header=ADDON_NAME, autoclose=0):
    if len(list) > 0:
        select = xbmcgui.Dialog().select(header, list, autoclose)
        return select

def yesnoDialog(str1, str2='', header=ADDON_NAME, str3='', str4=''):
    answer = xbmcgui.Dialog().yesno(header, str1, str2, '', str4, str3)
    return answer
     
##################
# Property Tools #
##################

def getProperty(str):
    return xbmcgui.Window(10000).getProperty(str)

def setProperty(str1, str2):
    xbmcgui.Window(10000).setProperty(str1, str2)

def clearProperty(str):
    xbmcgui.Window(10000).clearProperty(str)
     
##############
# XBMC Tools #
##############
 
def verifyPlayMedia(cmd):
    return True

def verifyPlugin(cmd):
    try:
        plugin = re.compile('plugin://(.+?)/').search(cmd).group(1)
        return xbmc.getCondVisibility('System.HasAddon(%s)' % plugin) == 1
    except:
        pass

    return True

def verifyScript(cmd):
    try:
        script = cmd.split('(', 1)[1].split(',', 1)[0].replace(')', '').replace('"', '')
        script = script.split('/', 1)[0]
        return xbmc.getCondVisibility('System.HasAddon(%s)' % script) == 1

    except:
        pass
    return True

def isATV():
    return xbmc.getCondVisibility('System.Platform.ATV2') == 1

def get_Kodi_JSON(params):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", %s, "id": 1}' % params)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    return simplejson.loads(json_query)
    
def isPlugin(plugin):
    if plugin[0:9] == 'plugin://':
        plugin = plugin.replace("plugin://","")
        # addon = os.path.split(plugin)[0]
        # addon = (plugin.split('/?')[0]).replace("plugin://","")
        addon = splitall(plugin)[0]
        log("utils: plugin id = " + addon)
    else:
        addon = plugin
    return xbmc.getCondVisibility('System.HasAddon(%s)' % addon) == 1

def videoIsPlaying():
    return xbmc.getCondVisibility('Player.HasVideo')

def getXBMCVersion():
    log("utils: getXBMCVersion")
    return int((xbmc.getInfoLabel('System.BuildVersion').split('.'))[0])
 
def getPlatform():
    log("utils: getPlatform")
    if xbmc.getCondVisibility('system.platform.osx'):
        return "OSX"
    elif xbmc.getCondVisibility('system.platform.atv2'):
        REAL_SETTINGS.setSetting('os', "4")
        return "ATV2"
    elif xbmc.getCondVisibility('system.platform.ios'):
        REAL_SETTINGS.setSetting('os', "5")
        return "iOS"
    elif xbmc.getCondVisibility('system.platform.windows'):
        REAL_SETTINGS.setSetting('os', "11")
        return "Windows"
    elif xbmc.getCondVisibility('system.platform.darwin'):
        return "Darwin"
    elif xbmc.getCondVisibility('system.platform.linux'):
        return "Linux"
    elif xbmc.getCondVisibility('system.platform.linux.raspberryPi'): 
        REAL_SETTINGS.setSetting('os', "10")
        return "rPi"
    elif xbmc.getCondVisibility('system.platform.android'): 
        return "Android"
    elif REAL_SETTINGS.getSetting("os") in ['0','1']: 
        return "Android"
    elif REAL_SETTINGS.getSetting("os") in ['2','3','4']: 
        return "ATV2"
    elif REAL_SETTINGS.getSetting("os") == "5": 
        return "iOS"
    elif REAL_SETTINGS.getSetting("os") in ['6','7']: 
        return "Linux"
    elif REAL_SETTINGS.getSetting("os") in ['8','9']: 
        return "OSX"
    elif REAL_SETTINGS.getSetting("os") == "10": 
        return "rPi"
    elif REAL_SETTINGS.getSetting("os") == "11": 
        return "Windows"
    return "Unknown"
     
#####################
# String/File Tools #
#####################
             
def trim(content, limit, suffix):
    if len(content) <= limit:
        return content
    else:
        return content[:limit].rsplit(' ', 1)[0]+suffix
        
def closest(list, Number):
    aux = []
    for valor in list:
        aux.append(abs(Number-int(valor)))
    return aux.index(min(aux))   
    
def removeStringElem(lst,string=''):
    return ([x for x in lst if x != string])
           
def sorted_nicely(lst): 
    log('utils: sorted_nicely')
    list = set(lst)
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(list, key = alphanum_key)
       
def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]
    
def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()
    
def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output
        
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)
    
def getSize(file):
    if FileAccess.exists(file):
        fileobject = FileAccess.open(file, "r")
        fileobject.seek(0,2) # move the cursor to the end of the file
        size = fileobject.tell()
        fileobject.close()
        return size
        
def replaceAll(file,searchExp,replaceExp):
    log('utils: script.pseudotv.liveutils: replaceAll')
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

def splitall(path):
    log("utils: splitall")
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
    
def replaceXmlEntities(link):
    log('utils: replaceXmlEntities')   
    entities = (
        ("%3A",":"),("%2F","/"),("%3D","="),("%3F","?"),("%26","&"),("%22","\""),("%7B","{"),("%7D",")"),("%2C",","),("%24","$"),("%23","#"),("%40","@"),("&#039;s","'s")
      );
    for entity in entities:
       link = link.replace(entity[0],entity[1]);
    return link;

def convert(s):
    log('utils: convert')       
    try:
        return s.group(0).encode('latin1').decode('utf8')
    except:
        return s.group(0)
        
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

##############
# PTVL Tools #
##############
     
def writeCache(thelist, thepath, thefile):
    log("writeCache")  
    now = datetime.datetime.today()

    if not FileAccess.exists(os.path.join(thepath)):
        FileAccess.makedirs(os.path.join(thepath))
    
    thefile = uni(thepath + thefile)        
    try:
        fle = FileAccess.open(thefile, "w")
        fle.write("%s\n" % now)
        for item in thelist:
            fle.write("%s\n" % item)
        fle.close()
    except Exception,e:
        pass
    
def readCache(thepath, thefile):
    log("readCache") 
    thelist = []  
    thefile = (thepath + thefile)
    
    if FileAccess.exists(thefile):
        try:
            fle = FileAccess.open(thefile, "r")
            thelist = fle.readlines()
            LastItem = len(thelist) - 1
            thelist.pop(LastItem)#remove last line (empty line)
            thelist.pop(0)#remove first line (datetime)
            fle.close()
        except Exception,e:
            pass
            
        log("readCache, thelist.count = " + str(len(thelist)))
        return thelist

def Cache_ok(thepath, thefile):
    log("Cache_ok")   
    CacheExpired = False
    thefile = (thepath + thefile)
    now = datetime.datetime.today()
    log("Cache_ok, now = " + str(now))
    
    if FileAccess.exists(thefile):
        try:
            fle = FileAccess.open(thefile, "r")
            cacheline = fle.readlines()
            cacheDate = str(cacheline[0])
            cacheDate = cacheDate.split('.')[0]
            cacheDate = datetime.datetime.strptime(cacheDate, '%Y-%m-%d %H:%M:%S')
            log("Cache_ok, cacheDate = " + str(cacheDate))
            cacheDateEXP = (cacheDate + datetime.timedelta(days=30))
            log("Cache_ok, cacheDateEXP = " + str(cacheDateEXP))
            fle.close()  
            
            if now >= cacheDateEXP or len(cacheline) == 2:
                CacheExpired = True         
        except Exception,e:
            log("Cache_ok, exception")
    else:
        CacheExpired = True    
        
    log("Cache_ok, CacheExpired = " + str(CacheExpired))
    return CacheExpired
      
def splitDBID(dbid):
    log('utils: splitDBID')
    try:
        epid = dbid.split(':')[1]
        dbid = dbid.split(':')[0]
    except:
        epid = '0'
    return dbid, epid
    
def getMpath(mediapath):
    log('utils: getMpath')
    try:
        if mediapath[0:5] == 'stack':
            smpath = (mediapath.split(' , ')[0]).replace('stack://','').replace('rar://','')
            mpath = (os.path.split(smpath)[0]) + '/'
        elif mediapath[0:6] == 'plugin':
            mpath = 'plugin://' + mediapath.split('/')[2] + '/'
        elif mediapath[0:4] == 'upnp':
            mpath = 'upnp://' + mediapath.split('/')[2] + '/'
        else:
            mpath = (os.path.split(mediapath)[0]) + '/'
        return mpath
    except:
        pass
                
def ChkSettings2():   
    log('utils: ChkSettings2')
    #Back/Restore Settings2
    settingFileAccess = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'settings2.xml'))
    nsettingFileAccess = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'settings2.bak.xml'))
    atsettingFileAccess = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'settings2.pretune.xml'))
    bksettingFileAccess = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'backups', 'settings2.' + str(datetime.datetime.now()).split('.')[0] + '.xml'))
    
    try:
        Normal_Shutdown = REAL_SETTINGS.getSetting('Normal_Shutdown') == "true"
    except:
        REAL_SETTINGS.setSetting('Normal_Shutdown', "true")
        Normal_Shutdown = REAL_SETTINGS.getSetting('Normal_Shutdown') == "true"
            
    if REAL_SETTINGS.getSetting("ATRestore") == "true" and REAL_SETTINGS.getSetting("Warning2") == "true":
        log('utils: ChkSettings2, Setting2 ATRestore')
        if getSize(atsettingFileAccess) > 100:
            REAL_SETTINGS.setSetting("ATRestore","false")
            REAL_SETTINGS.setSetting("Warning2","false")
            REAL_SETTINGS.setSetting('ForceChannelReset', 'true')
            Restore(atsettingFileAccess, settingFileAccess) 
    elif Normal_Shutdown == False:
        log('utils: ChkSettings2, Setting2 Restore') 
        if getSize(settingFileAccess) < 100 and getSize(nsettingFileAccess) > 100:
            Restore(nsettingFileAccess, settingFileAccess)
    else:
        log('utils: ChkSettings2, Setting2 Backup') 
        if getSize(settingFileAccess) > 100:
            Backup(settingFileAccess, nsettingFileAccess)
            Backup(settingFileAccess, bksettingFileAccess)

def ClearCache(type):
    log('utils: ClearCache ' + type)  
    if type == 'Filelist':
        quarterly.delete("%") 
        bidaily.delete("%") 
        daily.delete("%") 
        weekly.delete("%")
        monthly.delete("%")
        liveTV.delete("%")
        RSSTV.delete("%")
        pluginTV.delete("%")
        upnpTV.delete("%")
        lastfm.delete("%")
        REAL_SETTINGS.setSetting('ClearCache', "false")
    elif type == 'BCT':
        bumpers.delete("%")
        ratings.delete("%")
        commercials.delete("%")
        trailers.delete("%")
        REAL_SETTINGS.setSetting('ClearBCT', "false")
    elif type == 'Art':
        try:    
            shutil.rmtree(ART_LOC)
            log('utils: Removed ART_LOC')  
            REAL_SETTINGS.setSetting('ClearLiveArtCache', "true") 
            xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Artwork Folder Cleared", 1000, THUMB) )
        except:
            pass
        REAL_SETTINGS.setSetting('ClearLiveArt', "false")
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", type + " Cache Cleared", 1000, THUMB) )

def makeSTRM(mediapath):
    log('utils: makeSTRM')            
    if not FileAccess.exists(STRM_CACHE_LOC):
        FileAccess.makedirs(STRM_CACHE_LOC)
    path = (mediapath.encode('base64'))[:16] + '.strm'
    filepath = os.path.join(STRM_CACHE_LOC,path)
    if FileAccess.exists(filepath):
        return filepath
    else:
        fle = FileAccess.open(filepath, "w")
        fle.write("%s" % mediapath)
        fle.close()
        return filepath

def EXTtype(arttype): 
    JPG = ['banner', 'fanart', 'folder', 'landscape', 'poster']
    PNG = ['character', 'clearart', 'logo', 'disc']
    
    if arttype in JPG:
        arttypeEXT = (arttype + '.jpg')
    else:
        arttypeEXT = (arttype + '.png')
    log('utils: EXTtype = ' + str(arttypeEXT))
    return arttypeEXT

def Backup(org, bak):
    log('utils: Backup ' + str(org) + ' - ' + str(bak))
    if FileAccess.exists(org):
        if FileAccess.exists(bak):
            try:
                FileAccess.delete(bak)
            except:
                pass
        FileAccess.copy(org, bak)
    
    if NOTIFY == 'true':
        xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Backup Complete", 1000, THUMB) )
       
def Restore(bak, org):
    log('utils: Restore ' + str(bak) + ' - ' + str(org))
    if FileAccess.exists(bak):
        if FileAccess.exists(org):
            try:
                FileAccess.delete(org)
            except:
                pass
        xbmcvfs.rename(bak, org)
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Restore Complete, Restarting...", 1000, THUMB) )

def ClearPlaylists():
    log('utils: ClearPlaylists')
    for i in range(999):
        try:
            FileAccess.delete(CHANNELS_LOC + 'channel_' + str(i) + '.m3u')
        except:
            pass
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", 'Channel Playlists Cleared', 1000, THUMB) )
    return   

def CHKAutoplay():
    log('utils: CHKAutoplay')
    fle = xbmc.translatePath("special://profile/guisettings.xml")
    try:
        xml = FileAccess.open(fle, "r")
        dom = parse(xml)
        autoplaynextitem = dom.getElementsByTagName('autoplaynextitem')
        Videoautoplaynextitem  = (autoplaynextitem[0].childNodes[0].nodeValue.lower() == 'true')
        Musicautoplaynextitem  = (autoplaynextitem[1].childNodes[0].nodeValue.lower() == 'true')
        xml.close()
        log('utils: CHKAutoplay, Videoautoplaynextitem is ' + str(Videoautoplaynextitem)) 
        log('utils: CHKAutoplay, Musicautoplaynextitem is ' + str(Musicautoplaynextitem)) 
        totcnt = Videoautoplaynextitem + Musicautoplaynextitem
        if totcnt > 0:
            okDialog("Its recommended you disable Kodi's"+' "Play the next video/song automatically" ' + "feature found under Kodi's video/playback and music/playback settings.")
        else:
            raise
    except:
        pass
  
def VideoWindow():
    log("utils: VideoWindow, VWPath = " + str(VWPath))
    #Copy VideoWindow Patch file
    try:
        if getProperty("PseudoTVRunning") != "True":
            if not FileAccess.exists(VWPath):
                log("utils: VideoWindow, VWPath not found")
                xbmcvfs.copy(flePath, VWPath)
                if FileAccess.exists(VWPath):
                    log('utils: custom_script.pseudotv.live_9506.xml Copied')
                    VideoWindowPatch()   
                    xbmc.executebuiltin("ReloadSkin()")
                else:
                    raise
            else:
                log("utils: VideoWindow, VWPath found")
                VideoWindowPatch()
    except Exception:
        VideoWindowUninstall()
        VideoWindowUnpatch()
        Error = True
        pass
    
def VideoWindowPatch():
    log("utils: VideoWindowPatch")
    #Patch Videowindow/Seekbar
    try:
        f = open(PTVL_SKIN_SELECT_FLE, "r")
        linesLST = f.readlines()  
        f.close()
        
        for i in range(len(linesLST)):
            lines = linesLST[i]
            if b in lines:
                replaceAll(PTVL_SKIN_SELECT_FLE,b,a)        
                log('utils: script.pseudotv.live.EPG.xml Patched b,a')
            elif d in lines:
                replaceAll(PTVL_SKIN_SELECT_FLE,d,c)           
                log('utils: script.pseudotv.live.EPG.xml Patched d,c') 

        f = open(DSPath, "r")
        lineLST = f.readlines()            
        f.close()
        
        Ypatch = True
        for i in range(len(lineLST)):
            line = lineLST[i]
            if z in line:
                Ypatch = False
                break
            
        if Ypatch:
            for i in range(len(lineLST)):
                line = lineLST[i]
                if y in line:
                    replaceAll(DSPath,y,z)
                log('utils: dialogseekbar.xml Patched y,z')
    except Exception:
        VideoWindowUninstall()
        pass
   
def VideoWindowUnpatch():
    log("utils: VideoWindowUnpatch")
    #unpatch videowindow
    try:
        f = open(PTVL_SKIN_SELECT_FLE, "r")
        linesLST = f.readlines()    
        f.close()
        for i in range(len(linesLST)):
            lines = linesLST[i]
            if a in lines:
                replaceAll(PTVL_SKIN_SELECT_FLE,a,b)
                log('utils: script.pseudotv.live.EPG.xml UnPatched a,b')
            elif c in lines:
                replaceAll(PTVL_SKIN_SELECT_FLE,c,d)          
                log('utils: script.pseudotv.live.EPG.xml UnPatched c,d')
                
        #unpatch seekbar
        f = open(DSPath, "r")
        lineLST = f.readlines()            
        f.close()
        for i in range(len(lineLST)):
            line = lineLST[i]
            if w in line:
                replaceAll(DSPath,w,v)
                log('utils: dialogseekbar.xml UnPatched w,v')
    except Exception:
        Error = True
        pass

def VideoWindowUninstall():
    log('utils: VideoWindowUninstall')
    try:
        FileAccess.delete(VWPath)
        if not FileAccess.exists(VWPath):
            log('utils: custom_script.pseudotv.live_9506.xml Removed')
    except Exception:
        Error = True
        pass

def SyncXMLTV(force=False):
    log('utils: SyncXMLTV')
    if REAL_SETTINGS.getSetting("SyncXMLTV_Enabled") != "true":
        return
    now  = datetime.datetime.today()  
    try:
        if isDon() == True:
            try:
                SyncPTV_LastRun = REAL_SETTINGS.getSetting('SyncPTV_NextRun')
                if not SyncPTV_LastRun or FileAccess.exists(PTVLXML) == False or force == True:
                    raise
            except:
                SyncPTV_LastRun = "1970-01-01 23:59:00.000000"
                REAL_SETTINGS.setSetting("SyncPTV_NextRun",SyncPTV_LastRun)

            try:
                SyncPTV = datetime.datetime.strptime(SyncPTV_LastRun, "%Y-%m-%d %H:%M:%S.%f")
            except:
                SyncPTV_LastRun = "1970-01-01 23:59:00.000000"
                SyncPTV = datetime.datetime.strptime(SyncPTV_LastRun, "%Y-%m-%d %H:%M:%S.%f")
            if now > SyncPTV:         
                #Remove old file before download
                if FileAccess.exists(PTVLXML):
                    try:
                        FileAccess.delete(PTVLXML)
                        log('utils: SyncPTVL, Removed old PTVLXML')
                    except:
                        log('utils: SyncPTVL, Removing old PTVLXML Failed!')
                        
                #Download new file from ftp, then http backup.
                if retrieve_url_up((BASEURL + 'ptvlguide.zip'), UPASS, (xbmc.translatePath(PTVLXMLZIP))):
                    if FileAccess.exists(PTVLXMLZIP):
                        all(PTVLXMLZIP,XMLTV_CACHE_LOC,'')
                        try:
                            FileAccess.delete(PTVLXMLZIP)
                            log('utils: SyncPTVL, Removed PTVLXMLZIP')
                        except:
                            log('utils: SyncPTVL, Removing PTVLXMLZIP Failed!')
                    
                    if FileAccess.exists(os.path.join(XMLTV_CACHE_LOC,'ptvlguide.xml')):
                        log('utils: SyncPTVL, ptvlguide.xml download successful!')  
                        xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live","Guidedata Update Complete", 1000, THUMB) )  
                        SyncPTV_NextRun = ((now + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S.%f"))
                        log('utils: SyncPTVL, Now = ' + str(now) + ', SyncPTV_NextRun = ' + str(SyncPTV_NextRun))
                        REAL_SETTINGS.setSetting("SyncPTV_NextRun",str(SyncPTV_NextRun))   
                else:
                    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("Guidedata Update Failed!", "", 1000, THUMB) )  
    except:
        xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("Guidedata Update Failed!", "", 1000, THUMB) ) 
        pass
    
def CHKCache():
    # Secondary Cache Control - Threaded cache functions can collide with filelist cache.
    if getProperty("PTVL.BackgroundLoading_Finished") == "true":
        log('utils: CHKCache = ' + getProperty("PTVL.CHKCache"))
        return getProperty("PTVL.CHKCache") == "true"
    
def tidy(cmd):
    cmd = cmd.replace('&quot;', '')
    cmd = cmd.replace('&amp;', '&')

    if cmd.startswith('RunScript'):
        cmd = cmd.replace('?content_type=', '&content_type=')
        cmd = re.sub('/&content_type=(.+?)"\)', '")', cmd)

    if cmd.endswith('/")'):
        cmd = cmd.replace('/")', '")')

    if cmd.endswith(')")'):
        cmd = cmd.replace(')")', ')')

    return cmd

def help(chtype):
    log('utils: help, ' + chtype)
    HelpBaseURL = 'http://raw.github.com/Lunatixz/XBMC_Addons/master/script.pseudotv.live/resources/help/help_'
    type = (chtype).replace('None','General')
    URL = HelpBaseURL + (type.lower()).replace(' ','%20')
    log("utils: help URL = " + URL)
    title = type + ' Configuration Help'
    f = open_url(URL)
    text = f.read()
    showText(title, text)
    
def DonorDel(all=False):
    log('utils: DonorDel')
    FileAccess.delete(xbmc.translatePath(DL_DonorPath))   
    if all == True:
        FileAccess.delete(xbmc.translatePath(DonorPath))
        REAL_SETTINGS.setSetting("AT_Donor", "false")
        REAL_SETTINGS.setSetting("COM_Donor", "false")
        REAL_SETTINGS.setSetting("TRL_Donor", "false")
        REAL_SETTINGS.setSetting("Verified_Donor", "false")
        REAL_SETTINGS.setSetting("Donor_Verified", "0")
    return True
        
def isDon():
    val = REAL_SETTINGS.getSetting("Verified_Donor") == "true"
    setProperty("Verified_Donor", str(val))
    log('utils: isDon = ' + str(val))
    return val
    
def isCom():
    val = REAL_SETTINGS.getSetting("Verified_Community") == "true"
    setProperty("Verified_Community", str(val))
    log('utils: isCom = ' + str(val))
    return val
    
def isHub():
    val = REAL_SETTINGS.getSetting("Verified_Hub") == "true"
    setProperty("Verified_Hub", str(val))
    log('utils: isHub = ' + str(val))
    return val
        
def DonCHK():
    if REAL_SETTINGS.getSetting("Donor_Enabled") == "true" and REAL_SETTINGS.getSetting("Donor_UP") != '' and REAL_SETTINGS.getSetting("Donor_UP") != 'Username:Password': 
        if REAL_SETTINGS.getSetting("Verified_Donor") != "true": 
            xbmc.executebuiltin("RunScript("+ADDON_PATH+"/utilities.py,-DDautopatch)")
    else:
        if REAL_SETTINGS.getSetting("Verified_Donor") != "false":      
            DonorDel(True)
            
def ComCHK():
    if REAL_SETTINGS.getSetting("Community_Enabled") == "true" and REAL_SETTINGS.getSetting("Gmail_User") != '' and REAL_SETTINGS.getSetting("Gmail_User") != 'User@gmail.com':
        if REAL_SETTINGS.getSetting("Verified_Community") != "true": 
            REAL_SETTINGS.setSetting("AT_Community","true")
            REAL_SETTINGS.setSetting("Verified_Community", "true")
            REAL_SETTINGS.setSetting("Community_Verified", "1")
            xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live","Community List Activated", 1000, THUMB) )
    else:
        if REAL_SETTINGS.getSetting("Verified_Community") != "false": 
            REAL_SETTINGS.setSetting("AT_Community","false")
            REAL_SETTINGS.setSetting("Verified_Community", "false")
            REAL_SETTINGS.setSetting("Community_Verified", "0")

def HubCHK():
    if xbmc.getCondVisibility('System.HasAddon(plugin.program.addoninstaller)') == 1:
        if REAL_SETTINGS.getSetting("Verified_Hub") != "true": 
            REAL_SETTINGS.setSetting("AT_Hub","true")
            REAL_SETTINGS.setSetting("Verified_Hub","true") 
    else:
        if REAL_SETTINGS.getSetting("Verified_Hub") != "false": 
            REAL_SETTINGS.setSetting("AT_Hub","false") 
            REAL_SETTINGS.setSetting("Verified_Hub","false")
           
def listXMLTV():
    log("utils: listXMLTV")
    xmltvLst = []   
    EXxmltvLst = ['pvr','scheduledirect (Coming Soon)','zap2it (Coming Soon)']
    dirs,files = xbmcvfs.listdir(XMLTV_CACHE_LOC)
    dir,file = xbmcvfs.listdir(XMLTV_LOC)
    xmltvcacheLst = [s.replace('.xml','') for s in files if s.endswith('.xml')] + EXxmltvLst
    xmltvLst = sorted_nicely([s.replace('.xml','') for s in file if s.endswith('.xml')] + xmltvcacheLst)
    select = selectDialog(xmltvLst, 'Select xmltv file')

    if select != -1:
        return xmltvLst[select]        
        
def xmltvFile(setting3):
    log("utils: xmltvFile")                
    if setting3[0:4] == 'http' or setting3.lower() == 'pvr' or setting3.lower() == 'scheduledirect' or setting3.lower() == 'zap2it':
        xmltvFle = setting3
    elif setting3.lower() == 'ptvlguide':
        xmltvFle = PTVLXML
    else:
        xmltvFle = xbmc.translatePath(os.path.join(REAL_SETTINGS.getSetting('xmltvLOC'), str(setting3) +'.xml'))
    return xmltvFle
   
def getOSPpath(OSplat):
    log("utils: getOSPpath") 
    if OSplat == '0':
        return 'androidarm/rtmpdump'
    elif OSplat == '1':
        return 'android86/rtmpdump'
    elif OSplat == '2':
        return 'atv1linux/rtmpdump'
    elif OSplat == '3':
        return 'atv1stock/rtmpdump'
    elif OSplat == '4':
        return 'atv2/rtmpdump'
    elif OSplat == '5':
        return 'ios/rtmpdump'
    elif OSplat == '6':
        return 'linux32/rtmpdump'
    elif OSplat == '7':
        return 'linux64/rtmpdump'
    elif OSplat == '8':
        return 'mac32/rtmpdump'
    elif OSplat == '9':
        return 'mac64/rtmpdump'
    elif OSplat == '10':
        return 'pi/rtmpdump'
    elif OSplat == '11':
        return 'win/rtmpdump.exe'
    elif OSplat == '12':
        return '/usr/bin/rtmpdump'
        
def chkSources():
    log("utils: chkSources") 
    hasPVR = False
    hasUPNP = False
    try:
        fle = xbmc.translatePath('special://userdata/sources.xml')
        xml = FileAccess.open(fle, "r")
        dom = parse(xml)
        path = dom.getElementsByTagName('path')
        xml.close()
        for i in range(len(path)):
            line = path[i].childNodes[0].nodeValue.lower()
            if line in ['pvr://']:
                hasPVR = True
            elif line in ['upnp://']:
                hasUPNP = True
        if hasPVR + hasUPNP == 2:
            return
    except:
        pass
        
def chkLowPower(): 
    setProperty("PTVL.LOWPOWER","false") 
    if getPlatform() in ['ATV2','iOS','rPi','Android']:
        setProperty("PTVL.LOWPOWER","true") 
        REAL_SETTINGS.setSetting('SFX_Enabled', "false")
        REAL_SETTINGS.setSetting('Idle_Screensaver', "false")
        REAL_SETTINGS.setSetting('EnhancedGuideData', "false")
        if MEDIA_LIMIT > 250:
            REAL_SETTINGS.setSetting('MEDIA_LIMIT', "3")
    log("utils: chkLowPower = " + getProperty("PTVL.LOWPOWER"))
            
def chkChanges():
    CURR_ENHANCED_DATA = REAL_SETTINGS.getSetting('EnhancedGuideData')
    try:
        LAST_ENHANCED_DATA = REAL_SETTINGS.getSetting('Last_EnhancedGuideData')
    except:
        REAL_SETTINGS.setSetting('Last_EnhancedGuideData', CURR_ENHANCED_DATA)
        LAST_ENHANCED_DATA = REAL_SETTINGS.getSetting('Last_EnhancedGuideData')
    
    if CURR_ENHANCED_DATA != LAST_ENHANCED_DATA:
        REAL_SETTINGS.setSetting('ForceChannelReset', "true")
        REAL_SETTINGS.setSetting('Last_EnhancedGuideData', CURR_ENHANCED_DATA)
        
def getRSSFeed(genre):
    log("utils: getRSSFeed, genre = " + genre)
    feed = ''
    if genre.lower() == 'news':
        feed = 'http://feeds.bbci.co.uk/news/rss.xml'
    # todo parse git list pair rss by genre
    parseFeed(feed)
    
def parseFeed(link):
    log("utils: parseFeed")
    # RSSlst = ''
    # try:
        # feed = feedparser.parse(link)
        # header = (feed['feed']['title'])
        # title = feed['entries'][1].title
        # description =  feed['entries'][1].summary,
        # RSSlst = '[B]'+ header + "[/B]: "
        # for i in range(0,len(feed['entries'])):
            # RSSlst += ('[B]'+replaceXmlEntities(feed['entries'][i].title) + "[/B] - " + replaceXmlEntities((feed['entries'][i].summary).split('<')[0]))
        # setProperty("RSS.FEED", utf(RSSlst))
    # except Exception,e:
        # log("getRSSFeed Failed!" + str(e))
        # pass