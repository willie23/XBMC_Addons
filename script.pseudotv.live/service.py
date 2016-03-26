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

import os, xbmc, xbmcgui, xbmcaddon, xbmcvfs

# Plugin Info
ADDON_ID = 'script.pseudotv.live'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
THUMB = (xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'images')) + '/' + 'icon.png')

def autostart():
    xbmc.log('script.pseudotv.live-Service: autostart')
    xbmc.executebuiltin("Notification(%s, %s, %d, %s)" % (ADDON_NAME, "AutoStart Enabled", 1000, THUMB))
    AUTOSTART_TIMER = [0,5,10,15,20]#in seconds
    xbmc.sleep(AUTOSTART_TIMER[int(REAL_SETTINGS.getSetting('timer_amount'))] * 1000)
    xbmc.executebuiltin('RunScript("' + ADDON_PATH + '/default.py' + '")')

if REAL_SETTINGS.getSetting("Auto_Start") == "true":
    autostart()
    
# monitor = xbmc.Monitor()
# hasSomethingChanged = False
# while not monitor.abortRequested():
    # # Sleep/wait for abort for 1 seconds
    # if monitor.waitForAbort(1):
        # # Abort was requested while waiting. We should exit
        # break
        
    # #settings monitor causes severe performance issues, resorted to while loop
    # if xbmcgui.Window(10000).getProperty("PseudoTVRunning") != "True":
        # if xbmc.getCondVisibility('Window.IsActive(addonsettings)') == True:
            # hasSomethingChanged = True
        # if hasSomethingChanged == True:
            # hasSomethingChanged = False
            # chkChanges()
    # else:
        # if xbmcgui.Window(10000).getProperty("PTVL.LOWPOWER") == "true":
            # # Use kodi bug to force kill library scan which impacts PTVL performance # http://forum.kodi.tv/showthread.php?tid=241729
            # if monitor.onScanStarted('video'):
                # xbmc.executebuiltin("UpdateLibrary(video)")
            # elif monitor.onScanStarted('music'):
                # xbmc.executebuiltin("UpdateLibrary(music)")