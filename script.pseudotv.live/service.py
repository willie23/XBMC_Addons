#   Copyright (C) 2015 Kevin S. Graer
#
#
# This file is part of PseudoTV Live.
#
# PseudoTV Live is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PseudoTV Live is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PseudoTV Live.  If not, see <http://www.gnu.org/licenses/>.

import xbmc, xbmcgui, xbmcaddon, xbmcvfs, hashlib, base64
import os, feedparser, datetime, time, _strptime, urllib2, threading

from time import sleep
from random import randint

# Plugin Info
ADDON_ID = 'script.pseudotv.live'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
THUMB = (xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'images')) + '/' + 'icon.png')

def UID():
    # GAID
    if not REAL_SETTINGS.getSetting('Visitor_GA'):
        REAL_SETTINGS.setSetting('Visitor_GA', str(randint(0, 0x7fffffff)))
        
    # UID
    try:
        UID_LOC = xbmc.translatePath(os.path.join(SETTINGS_LOC,'UID'))
        if not os.path.exists(UID_LOC):
            fle = open(UID_LOC, "w")
            fle.write("%s" % str(randint(0, 0x7fffffff)))
            fle.close()
            
        if not xbmcgui.Window(10000).getProperty("PTVL.UID"):
            fle = open(UID_LOC, 'r')
            xbmcgui.Window(10000).setProperty("PTVL.UID",str((fle.readlines())[0]))
            fle.close()
    except Exception,e:
        print str(e)
        
    # UPID
    try:
        UPID_LOC = xbmc.translatePath(os.path.join(SETTINGS_LOC,'UPID'))
        if REAL_SETTINGS.getSetting('Donor_UP') != 'Username:Password':     
            if not os.path.exists(UPID_LOC):
                fle = open(UPID_LOC, "w")
                HASH = str(randint(0, 0x7fffffff))
                REAL_SETTINGS.setSetting("Donor_UP",str(encode(HASH, REAL_SETTINGS.getSetting('Donor_UP'))))
                fle.write("%s" % HASH)
                fle.close()
            
            if not xbmcgui.Window(10000).getProperty("PTVL.UPID"):
                fle = open(UPID_LOC, 'r')
                HASH = str((fle.readlines())[0])
                fle.close()
                xbmcgui.Window(10000).setProperty("PTVL.UPID",HASH)
    except Exception,e:
        print str(e)

    # GID
    try:
        GID_LOC = xbmc.translatePath(os.path.join(SETTINGS_LOC,'GID'))
        if REAL_SETTINGS.getSetting('Community_Enabled') == 'true' and REAL_SETTINGS.getSetting('Gmail_Pass') != 'Password':     
            if not os.path.exists(GID_LOC):
                fle = open(GID_LOC, "w")
                HASH = str(randint(0, 0x7fffffff))
                REAL_SETTINGS.setSetting("Gmail_Pass",str(encode(HASH, REAL_SETTINGS.getSetting('Gmail_Pass'))))
                fle.write("%s" % HASH)
                fle.close()
            
            if not xbmcgui.Window(10000).getProperty("PTVL.GID"):
                fle = open(GID_LOC, 'r')
                HASH = str((fle.readlines())[0])
                fle.close()
                xbmcgui.Window(10000).setProperty("PTVL.GID",HASH)
    except Exception,e:
        print str(e)
        
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
    
def SettopUpdate():
    if xbmcgui.Window(10000).getProperty("PseudoTVRunning") == "True" and REAL_SETTINGS.getSetting("SettopUpdate") == "true" :
        # from resources.lib.Overlay import TVOverlay
        # overlay = TVOverlay()
        if REAL_SETTINGS.getSetting("EnableSettop") == "true" and xbmc.getCondVisibility("Library.IsScanningVideo"):
            xbmc.log('script.pseudotv.live-Service: SettopUpdate')
            while (xbmc.getCondVisibility("Library.IsScanningVideo")) : xbmc.sleep(10)
            # xbmc.executebuiltin("RunScript("+__cwd__+"/utilities.py,-showChangelog)")
            # try:
                # if overlay.channelThread_Timer.isAlive():
                    # overlay.channelThread_Timer.cancel()
            # except:
                # pass
            # overlay.channelThread_Timer = threading.Timer((5.0), overlay.Settop)
            # overlay.channelThread_Timer.start() 
            
def ArtService():
    now  = datetime.datetime.today()
    try:
        UpdateArt_LastRun = xbmcgui.Window(10000).getProperty("UpdateArt_NextRun")
        if not UpdateArt_LastRun:
            raise
    except:
        UpdateArt_LastRun = "1970-01-01 23:59:00.000000"
        xbmcgui.Window(10000).setProperty("UpdateArt_NextRun",UpdateArt_LastRun)
    try:
        SyncUpdateArt = datetime.datetime.strptime(UpdateArt_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    except:
        UpdateArt_LastRun = "1970-01-01 23:59:00.000000"
        SyncUpdateArt = datetime.datetime.strptime(UpdateArt_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    xbmc.log('script.pseudotv.live-Service: UpdateArt, Now = ' + str(now) + ', UpdateArt_LastRun = ' + str(UpdateArt_LastRun))
    
    if now > SyncUpdateArt:
        xbmc.executebuiltin('RunScript("' + ADDON_PATH + '/utilities.py,-ArtService)')
        
def UpdateRSS():
    now  = datetime.datetime.today()
    try:
        UpdateRSS_LastRun = xbmcgui.Window(10000).getProperty("UpdateRSS_NextRun")
        if not UpdateRSS_LastRun:
            raise
    except:
        UpdateRSS_LastRun = "1970-01-01 23:59:00.000000"
        xbmcgui.Window(10000).setProperty("UpdateRSS_NextRun",UpdateRSS_LastRun)
    try:
        SyncUpdateRSS = datetime.datetime.strptime(UpdateRSS_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    except:
        UpdateRSS_LastRun = "1970-01-01 23:59:00.000000"
        SyncUpdateRSS = datetime.datetime.strptime(UpdateRSS_LastRun, "%Y-%m-%d %H:%M:%S.%f")
    xbmc.log('script.pseudotv.live-Service: UpdateRSS, Now = ' + str(now) + ', UpdateRSS_LastRun = ' + str(UpdateRSS_LastRun))
    
    if now > SyncUpdateRSS:
        ##Push MSG
        pushlist = ''
        try:
            pushrss = 'https://raw.githubusercontent.com/Lunatixz/XBMC_Addons/master/push_msg.xml'
            file = urllib2.urlopen('https://raw.githubusercontent.com/Lunatixz/XBMC_Addons/master/push_msg.xml')
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
        xbmc.log('script.pseudotv.live-Service: UpdateRSS, Now = ' + str(now) + ', UpdateRSS_NextRun = ' + str(UpdateRSS_NextRun))
        xbmcgui.Window(10000).setProperty("UpdateRSS_NextRun",str(UpdateRSS_NextRun))
        xbmcgui.Window(10000).setProperty("twitter.1.label", pushlist)
        xbmcgui.Window(10000).setProperty("twitter.2.label", gitlist)
        xbmcgui.Window(10000).setProperty("twitter.3.label", twitlist)
        
# Swap Org/Hub versions if 'Hub Installer' found.
def HubSwap():
    icon = ADDON_PATH + '/icon'
    HUB = xbmc.getCondVisibility('System.HasAddon(plugin.program.addoninstaller)') == 1
    if HUB == True:
        xbmc.log('script.pseudotv.live-Service: HubSwap = Hub Edition')
        if REAL_SETTINGS.getSetting('Hub') == 'false':
            xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live","Hub-Edition Activated", 4000, THUMB) )
            REAL_SETTINGS.setSetting("Hub","true")
    else:
        xbmc.log('script.pseudotv.live-Service: HubSwap = Master')
        if REAL_SETTINGS.getSetting('Hub') == 'true':
            REAL_SETTINGS.setSetting("Hub","false")
    return          

def donorCHK():
    DonorPath = (os.path.join(ADDON_PATH, 'resources', 'lib', 'Donor.pyo'))
    DL_DonorPath = (os.path.join(ADDON_PATH, 'resources', 'lib', 'Donor.py'))

    if xbmcvfs.exists(DonorPath) or xbmcvfs.exists(DL_DonorPath):
        xbmc.log('script.pseudotv.live-Service: donorCHK = Donor') 
        REAL_SETTINGS.setSetting("AT_Donor", "true")
        REAL_SETTINGS.setSetting("COM_Donor", "true")
        REAL_SETTINGS.setSetting("TRL_Donor", "true")
        REAL_SETTINGS.setSetting("CAT_Donor", "true")  
        xbmcgui.Window(10000).setProperty("Donor", "true") 
    else:
        xbmc.log('script.pseudotv.live-Service: donorCHK = FreeUser') 
        REAL_SETTINGS.setSetting("AT_Donor", "false")
        REAL_SETTINGS.setSetting("COM_Donor", "false")
        REAL_SETTINGS.setSetting("TRL_Donor", "false")
        REAL_SETTINGS.setSetting("CAT_Donor", "false")
        xbmcgui.Window(10000).setProperty("Donor", "false")
        
    # CHK Community list gmail for approval
    if REAL_SETTINGS.getSetting("Community_Enabled") == "true" and REAL_SETTINGS.getSetting('Gmail_Pass') != 'Password':  
        xbmcgui.Window(10000).setProperty("PTVL.COM_APP", "true")
    else:
        xbmcgui.Window(10000).setProperty("PTVL.COM_APP", "false")
            
        
    return
        
# execute service functions
def service():
    while not xbmc.abortRequested:
        xbmc.log("script.pseudotv.live-Service: Started")
        xbmc.log('script.pseudotv.live-Service: PseudoTVRunning = ' + xbmcgui.Window(10000).getProperty("PseudoTVRunning")) 
        UID()
        UpdateRSS()
        SettopUpdate()
        
        if xbmcgui.Window(10000).getProperty("PseudoTVRunning") != "True" and xbmc.getCondVisibility('Window.IsActive(addonsettings)') != True:
            donorCHK()
            HubSwap()
            
            # if autostart enabled, and first boot. Start PTVL!
            if REAL_SETTINGS.getSetting("Auto_Start") == "true" and xbmcgui.Window(10000).getProperty("Auto_Start_Exit") != "true":
                xbmcgui.Window(10000).setProperty("Auto_Start_Exit", "true")
                autostart()
        else:
            xbmc.log('script.pseudotv.live-Service: Ignored')
                
        xbmc.log('script.pseudotv.live-Service: Idle')
        xbmc.sleep(30000)

def autostart():
    xbmc.log('script.pseudotv.live-Service: autostart')   
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("AutoStart PseudoTV Live","Service Starting...", 4000, THUMB) )
    AUTOSTART_TIMER = [0,5,10,15,20]#in seconds
    IDLE_TIME = AUTOSTART_TIMER[int(REAL_SETTINGS.getSetting('timer_amount'))] 
    sleep(IDLE_TIME)
    xbmc.executebuiltin('RunScript("' + ADDON_PATH + '/default.py' + '")')
    return
    
service()