#   Copyright (C) 2016 Lunatixz
#
#
# This file is part of Video Mirror Service.
#
# Video Mirror Service is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Video Mirror Service is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Video Mirror Service.  If not, see <http://www.gnu.org/licenses/>.

import os, xbmc, xbmcgui, xbmcaddon, xbmcvfs, string, re
from datetime import datetime, time
from Upnp import Upnp

# Plugin Info
ADDON_ID = 'script.video.mirror.service'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')
POLL = int(REAL_SETTINGS.getSetting('Poll_TIME'))*1000
DEBUG = REAL_SETTINGS.getSetting('Enable_Debugging')


class MyPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self, xbmc.Player())   
        self.Upnp = Upnp()


    def log(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == True:
            xbmc.log('VideoMirror: ' + msg, level)
        
        
    def getPlayerFile(self):
        try:
            return (self.getPlayingFile()).replace("\\\\","\\")
        except:
            return ''
            
            
    def getPlayerTime(self):
        try:
            return self.getTime()
        except:
            return 0
             
             
    def getPlayerTitle(self):
        try:
            title = xbmc.getInfoLabel('Player.Title')
            if not title:
                title = xbmc.getInfoLabel('VideoPlayer.Title')
        except:
            title = ''
        return title
        
        
    def isPlaybackValid(self):
        Playing = False
        xbmc.sleep(10)
        if self.isPlaying():
            Playing = True
        self.log('isPlaybackValid = ' + str(Playing))
        return Playing
        
        
    def onPlayBackPaused(self):
        self.log('onPlayBackPaused')
        self.UPNPcontrol('pause')

        
    def onPlayBackResumed(self):
        self.log('onPlayBackResumed')
        self.UPNPcontrol('resume')

        
    def onPlayBackStarted(self):
        self.log('onPlayBackStarted')     
        self.UPNPcontrol('play', self.getPlayerTitle(), self.getPlayerFile(), self.getPlayerTime())          
            
            
    def onPlayBackStopped(self):
        self.log('onPlayBackStopped')
        self.UPNPcontrol('stop')

        
    def UPNPcontrol(self, func, label='', file='', seektime=0):
        self.log('UPNPcontrol')
        self.Upnp.initUPNP()
        if len(self.Upnp.IPPlst) > 0:
            if func == 'play':
                self.Upnp.SendUPNP(label, file, seektime)
            elif func == 'stop':
                self.Upnp.StopUPNP()
            elif func == 'resume':
                self.Upnp.ResumeUPNP()
            elif func == 'pause':
                self.Upnp.PauseUPNP()
            elif func == 'rwd':
                self.Upnp.RWUPNP()
            elif func == 'fwd':
                self.Upnp.FFUPNP()
            elif func == 'chkplay':
                self.Upnp.chkUPNP(label, file, seektime)     
   
   
monitor = MyPlayer() 
while not xbmc.abortRequested:
    monitor.isPlaying()
    if monitor.isPlayingVideo() and xbmcgui.Window(10000).getProperty('PseudoTVRunning') != 'True':
        monitor.log(monitor.getPlayerTitle() +','+ monitor.getPlayerFile() +','+ str(monitor.getPlayerTime()))
        monitor.Upnp.chkUPNP(monitor.getPlayerTitle(), monitor.getPlayerFile(), monitor.getPlayerTime()) 
    xbmc.sleep(POLL)