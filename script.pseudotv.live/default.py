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
    
import os, sys, re, shutil, threading
import xbmc, xbmcgui, xbmcaddon, xbmcvfs

from resources.lib.Globals import *
from resources.lib.utils import *

# Script constants
__scriptname__ = "PseudoTV Live"
__author__     = "Lunatixz, Jason102"
__url__        = "https://github.com/Lunatixz/script.pseudotv.live"
__settings__   = xbmcaddon.Addon(id='script.pseudotv.live')
__cwd__        = __settings__.getAddonInfo('path')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString
       
def startPseudoTV():
    # Run Prestart functions
    ChkSettings()
    
    # Backup/Restore settings2
    ChkSettings2()

    #Start PseudoTV
    PseudoTV()
       
def PseudoTV():
    import resources.lib.Overlay as Overlay
    setProperty("PseudoTVRunning", "True")
    
    try:
        MyOverlayWindow = Overlay.TVOverlay("script.pseudotv.live.TVOverlay.xml", __cwd__, Skin_Select)
    except Exception,e:
        log('default: PseudoTV Overlay Failed! ' + str(e))
        Error('PseudoTV Live','Error loading "' + Skin_Select + '" skin!','Verify selected skin.') 
        return
        
    for curthread in threading.enumerate():
        try:
            log("Active Thread: " + str(curthread.name), xbmc.LOGERROR)
            if curthread.name != "MainThread":
                try:
                    curthread.join()      
                except: 
                    pass
                log("Joined " + curthread.name)               
        except: 
            pass
            
    del MyOverlayWindow
    setProperty("PseudoTVRunning", "False")
    
# Adapting a solution from ronie (http://forum.xbmc.org/showthread.php?t=97353)
if getProperty("PseudoTVRunning") != "True":
    try:
        PTVL_Version = REAL_SETTINGS.getSetting("PTVL_Version")
        if not PTVL_Version:
            raise
    except:
        REAL_SETTINGS.setSetting("PTVL_Version", __version__)
        PTVL_Version = REAL_SETTINGS.getSetting("PTVL_Version") 
    
    if PTVL_Version != __version__:
        REAL_SETTINGS.setSetting("PTVL_Version", __version__)
        
        # Remove m3u playlists
        # ClearPlaylists()
        
        # Force Channel rebuild
        # REAL_SETTINGS.setSetting('ForceChannelReset', 'true')
      
        # Optimize settings based on sys.platform
        chkLowPower()
        
        # VideoWindow Patch.
        VideoWindow()
        
        # Call showChangeLog like this to workaround bug in openElec, *Thanks spoyser
        xbmc.executebuiltin("RunScript("+__cwd__+"/utilities.py,-showChangelog)") 
        
        # Check if autoplay is enabled
        CHKAutoplay()
    else:
        startPseudoTV()
else:
    log('default: Already running, exiting', xbmc.LOGERROR)
    xbmc.executebuiltin("Notification( %s, %s, %d, %s)" % ("PseudoTV Live", "Already running please wait and try again later.", 4000, THUMB) )