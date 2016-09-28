#   Copyright (C) 2016 Lunatixz
#
#
# This file is part of Smart Mirror.
#
# Smart Mirror is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Smart Mirror is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Smart Mirror.  If not, see <http://www.gnu.org/licenses/>.


#setting options
#trakt, imdb, rot tomato support, change image rotation, change marquee/sign image, enter marquee text, enable pseudo "onnow" banners

#todo
#autostart, detect kodi res, add trailers, custom marquee, event triggers, pseudotv onnow, random posters, random trailers, next airing, transition anim.
import threading, random, datetime, time
import re, os, sys
import json, urllib, requests
import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon

# Plugin Info
ADDON_ID = 'script.smart.mirror'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')
KODI_MONITOR = xbmc.Monitor()

class MIRROR(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.clockMode = 0
        self.isExiting = False
        self.updateTimer = threading.Timer(1.0, self.update)
        
        
    def log(self, msg, level = xbmc.LOGDEBUG):
        xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + msg, level)
        
        
    def onInit(self):
        self.log('onInit')
        if self.updateTimer.isAlive() == False:
            self.updateTimer.start()
          
          
    def update(self):
        while not KODI_MONITOR.abortRequested():
            self.log('update')
            if self.isExiting == True:
                return
            time.sleep(1)
            self.setTimeLabels()
          
          
    def onAction(self, act):
        action = act.getId()
        self.log('onAction ' + str(action))
        if action in [9, 10, 92, 247, 257, 275, 61467, 61448]:
            self.isExiting = True
            self.close()

            
    def getProperty(self, str):
        return xbmcgui.Window(10000).getProperty(str)
              
              
    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)
            
            
    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)    

        
    # set the time labels
    def setTimeLabels(self):
        self.log('setTimeLabels')
        now = datetime.datetime.now()
        self.setProperty('Mirror.DAY',now.strftime('%A'))
        self.setProperty('Mirror.DATE',now.strftime('%B %d'))
        
        if self.clockMode == 0:
            self.setProperty('Mirror.TIME',now.strftime('%i:%M'))
        else:
            self.setProperty('Mirror.TIME',now.strftime('%H:%M'))

        
        
        
myMIRROR = MIRROR("mirror.xml", ADDON_PATH, 'default')
myMIRROR.doModal()
del myMIRROR