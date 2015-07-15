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

import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os

from time import sleep
from resources.lib.utils import *

# Plugin Info
ADDON_ID = 'script.pseudotv.live'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
THUMB = (xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'images')) + '/' + 'icon.png')

def checkDisabled():
    if xbmc.getCondVisibility('System.HasAddon(script.pseudotv.live)') == 0:
        DeleteKeymap('ptvl_hot.xml')
        DeleteKeymap('ptvl_menu.xml')
        return True
    return False 
    
def autostart():
    xbmc.log('script.pseudotv.live-Service: autostart')   
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("AutoStart PseudoTV Live","Service Starting...", 4000, THUMB) )
    AUTOSTART_TIMER = [0,5,10,15,20]#in seconds
    IDLE_TIME = AUTOSTART_TIMER[int(REAL_SETTINGS.getSetting('timer_amount'))] 
    sleep(IDLE_TIME)
    xbmc.executebuiltin('RunScript("' + ADDON_PATH + '/default.py' + '")')

# Startup tasks
VerifyKeymaps()
        
if REAL_SETTINGS.getSetting("Auto_Start") == "true":
    autostart()

class MyMonitor(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.context = REAL_SETTINGS.getSetting('CONTEXT')  == 'true'

    def cmCHK(self):
        context = REAL_SETTINGS.getSetting('CONTEXT')  == 'true'
        if self.context == context:
            return
        self.context = context
        UpdateKeymaps()
                 
    def onSettingsChanged(self):
        self.cmCHK()
        
monitor = MyMonitor()

while (not xbmc.abortRequested):
    xbmc.sleep(1000)
    if checkDisabled():
        xbmc.sleep(1000)
        xbmc.executebuiltin('Action(reloadkeymaps)')

    if xbmc.getCondVisibility('Window.IsActive(addonsettings)') != True:
        # Disable PseudoTVRunning
        if getProperty("PseudoTVRunning") != "True":
            HubCHK()
            xbmc.sleep(1000)
            ComCHK()
            xbmc.sleep(1000)
            DonCHK()
            
    UpdateRSS()     
                
checkDisabled()
        
del monitor