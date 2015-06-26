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

import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os, sys, re

from urllib import unquote
from resources.lib.utils import *
from resources.lib.Globals import *
from resources.lib.ChannelList import *
from resources.lib.FileAccess import FileAccess

class SFParser:
    def __init__(self):
        self.chanlist = ChannelList()
        self.SuperFav = self.chanlist.plugin_ok('plugin.program.super.favourites')
          
    def log(self, msg, level = xbmc.LOGDEBUG):
        log('SFParser: ' + msg, level)
        
    def logDebug(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == 'true':
            log('SFParser: ' + msg, level)
 
    def SFAutotune(self, channelNum, limit):
        self.log("SFAutotune")
        self.log("SFAutotune, SF_FILTER = " + str(SF_FILTER))
        
        if self.SuperFav == True:
            plugin_details = self.chanlist.PluginQuery('plugin://plugin.program.super.favourites')
            for i in plugin_details:
                try:
                    filetypes = re.search('"filetype" *: *"(.*?)"', i)
                    labels = re.search('"label" *: *"(.*?)"', i)
                    files = re.search('"file" *: *"(.*?)"', i)

                    #if core variables have info proceed
                    if filetypes and files and labels:
                        filetype = filetypes.group(1)
                        file = (files.group(1))
                        label = (labels.group(1))
                        print filetype, file, label
                        
                        if label and label.lower() not in SF_FILTER:
                            if filetype == 'directory':
                                SFmatch = unquote(file)
                                SFmatch = SFmatch.split('Super+Favourites')[1].replace('\\','/')
                                self.log("SFAutotune, SFmatch = " + SFmatch)
                                
                                if SFmatch == '/PseudoTV_Live':
                                    plugin_details = self.chanlist.PluginQuery(file)
                                    break
                                elif SFmatch[0:9] != '/Channel_':
                                    plugin_details = self.chanlist.PluginQuery(file)
                                    
                                SFmatch = SFmatch.split('&')[0]
                                SFname = SFmatch.replace('/PseudoTV_Live/','').replace('/','')
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_type", "15")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_time", "0")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_1", 'plugin://plugin.program.super.favourites' + SFmatch)
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_2", "")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_3", str(limit))
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_4", "0")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rulecount", "1")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rule_1_id", "1")
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rule_1_opt_1", SFname)
                                ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_changed", "true")
                                channelNum += 1       
                except:
                    pass  
            return channelNum