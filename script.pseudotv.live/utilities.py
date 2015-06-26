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
# along with PseudoTV Live.  If not, see <http://www.gnu.org/licenses/>.
        
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os, sys, time, urllib

from resources.lib.Globals import *
from resources.lib.utils import *
  
# showInfo
def showText(heading, text):
    xbmc.log('script.pseudotv.live-utilities: showText')
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
            
def showInfo(addonID=None, type='changelog'):
    xbmc.log('script.pseudotv.live-utilities: showInfo')
    try:
        if addonID:
            ADDON = xbmcaddon.Addon(addonID)
        else: 
            ADDON = xbmcaddon.Addon(ADDONID)
        if type == 'changelog':
            title = "PseudoTV Live - Changelog"
            f = open(ADDON.getAddonInfo('changelog'))
        if type == 'readme':
            title = "PseudoTV Live - Readme"
            f = open(os.path.join(ADDON_PATH,'README.md'))
        if type == 'disclaimer':
            title = "PseudoTV Live - Privacy Disclaimer"
            f = open(os.path.join(ADDON_PATH,'disclaimer'))
            
        text  = f.read()
        showText(title, text)
    except:
        pass      

#DonorDownload  

DonorURLPath = (PTVLURL + 'Donor.py')
DonorPath = xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib', 'Donor.pyo'))
DL_DonorPath = xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib', 'Donor.py'))

def DonorDownloader(auto=False):
    xbmc.log('script.pseudotv.live-utilities: DonorDownloader')
    REAL_SETTINGS.setSetting("AT_Donor", "false")
    REAL_SETTINGS.setSetting("COM_Donor", "false")
    REAL_SETTINGS.setSetting("TRL_Donor", "false")
    REAL_SETTINGS.setSetting("CAT_Donor", "false")
    if auto == True:
        MSG = 'Updated'
        Install = True
    else: 
        MSG = 'Activated'
        InstallStatusMSG = 'Activate'
        Install = False
        
        if xbmcvfs.exists(DonorPath) or xbmcvfs.exists(DL_DonorPath):
            InstallStatusMSG = 'Update'
        if dlg.yesno("PseudoTV Live", str(InstallStatusMSG) + " Donor Features?"):
            Install = True
                
    if Install:
        try:
            if xbmcvfs.exists((DL_DonorPath)):
                xbmcvfs.delete(xbmc.translatePath(DL_DonorPath))
                xbmc.log('script.pseudotv.live-utilities: DonorDownloader, Removed DL_DonorPath')
                
            if xbmcvfs.exists(xbmc.translatePath(DonorPath)):
                xbmcvfs.delete(xbmc.translatePath(DonorPath))  
                xbmc.log('script.pseudotv.live-utilities: DonorDownloader, Removed DonorPath')
        except Exception,e:
            print str(e)
            
        try:
            urllib.urlretrieve(DonorURLPath, (xbmc.translatePath(DL_DonorPath)))
            if xbmcvfs.exists(DL_DonorPath):
                xbmc.log('script.pseudotv.live-utilities: DonorDownloader, DL_DonorPath Downloaded')
                REAL_SETTINGS.setSetting("AT_Donor", "true")
                REAL_SETTINGS.setSetting("COM_Donor", "true")
                REAL_SETTINGS.setSetting("TRL_Donor", "true")
                REAL_SETTINGS.setSetting("CAT_Donor", "true")
                xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Donor Features "+MSG, 4000, THUMB) ) 
        except Exception,e:
            print str(e)
            
    if auto == True:
        # Return to PTVL Settings
        REAL_SETTINGS.openSettings()
         
def DeleteSettings2():
    xbmc.log('script.pseudotv.live-utilities: DeleteSettings2')
    if xbmcvfs.exists(os.path.join(SETTINGS_LOC, 'settings2.xml')):
        if dlg.yesno("PseudoTV Live", "Delete Current Channel Configurations?"):
            try:
                xbmcvfs.delete(xbmc.translatePath(os.path.join(SETTINGS_LOC, 'settings2.xml')))
                xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Channel Configurations Cleared", 1000, THUMB) )
            except:
                pass
    # Return to PTVL Settings
    REAL_SETTINGS.openSettings()
    
    
def ClearChanFavorites():
    xbmc.log('script.pseudotv.live-utilities: ClearChanFavorites')
    REAL_SETTINGS.setSetting("FavChanLst","0")
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Channel Favourites Cleared", 1000, THUMB) )
    # Return to PTVL Settings
    REAL_SETTINGS.openSettings()
    
    
if sys.argv[1] == '-DDautopatch':
    DonorDownloader(True)   
elif sys.argv[1] == '-DonorDownloader':
    DonorDownloader()  
    
elif sys.argv[1] == '-SimpleDownloader':
    xbmcaddon.Addon(id='script.module.simple.downloader').openSettings()
    
elif sys.argv[1] == '-showChangelog':
    showInfo(ADDON_ID, 'changelog') 
elif sys.argv[1] == '-showReadme':
    showInfo(ADDON_ID, 'readme') 
elif sys.argv[1] == '-showDisclaimer':
    showInfo(ADDON_ID, 'disclaimer') 
    
elif sys.argv[1] == '-DeleteSettings2':
    DeleteSettings2()
elif sys.argv[1] == '-repairSettings2':
    from resources.lib.Settings import *
    Setfun = Settings()
    Setfun.repairSettings()
elif sys.argv[1] == '-ClearChanFavorites':
    ClearChanFavorites()