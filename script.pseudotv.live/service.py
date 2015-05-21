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


import os, xbmc, xbmcgui, xbmcaddon, xbmcvfs, feedparser, datetime, time, _strptime, urllib2
from time import sleep

# Plugin Info
ADDON_ID = 'script.pseudotv.live'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
THUMB = (xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'images')) + '/' + 'icon.png')


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
                if '@PseudoTV_Live' in tost.title:
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
        if xbmcgui.Window(10000).getProperty("Donor") != "true":
            REAL_SETTINGS.setSetting("AT_Donor", "true")
            REAL_SETTINGS.setSetting("COM_Donor", "true")
            REAL_SETTINGS.setSetting("TRL_Donor", "true")
            REAL_SETTINGS.setSetting("CAT_Donor", "true")  
            xbmcgui.Window(10000).setProperty("Donor", "true") 
    else:
        xbmc.log('script.pseudotv.live-Service: donorCHK = FreeUser') 
        if xbmcgui.Window(10000).getProperty("Donor") != "false":
            REAL_SETTINGS.setSetting("AT_Donor", "false")
            REAL_SETTINGS.setSetting("COM_Donor", "false")
            REAL_SETTINGS.setSetting("TRL_Donor", "false")
            REAL_SETTINGS.setSetting("CAT_Donor", "false")
            xbmcgui.Window(10000).setProperty("Donor", "false")
    return
        
        
# execute service functions
def service():
    while not xbmc.abortRequested:
        xbmc.log("script.pseudotv.live-Service: Started")
        xbmc.log('script.pseudotv.live-Service: PseudoTVRunning = ' + xbmcgui.Window(10000).getProperty("PseudoTVRunning")) 
        UpdateRSS()
        
        if xbmcgui.Window(10000).getProperty("PseudoTVRunning") != "true" and not xbmc.getCondVisibility('Window.IsActive(addonsettings)'):
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