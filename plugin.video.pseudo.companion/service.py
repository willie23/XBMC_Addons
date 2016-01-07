#   Copyright (C) 2015 Kevin S. Graer
#
#
# This file is part of PseudoCompanion.
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

# -*- coding: utf-8 -*-

import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

def getProperty(str):
    return xbmcgui.Window(10000).getProperty(str)

def setProperty(str1, str2):
    xbmcgui.Window(10000).setProperty(str1, str2)

def clearProperty(str):
    xbmcgui.Window(10000).clearProperty(str)
    
while (not xbmc.abortRequested):
    PTVL_RUNNING = getProperty('PseudoTVRunning') == "True"
    if PTVL_RUNNING == True:
        STATE = 'true'
        STATUS = '[COLOR=green]ONLINE[/COLOR]'
    else:
        STATE = 'false'
        STATUS = '[COLOR=red]OFFLINE[/COLOR]'
    setProperty('PseudoCompanion.STATE', STATE)
    setProperty('PseudoCompanion.STATUS', STATUS)
    xbmc.sleep(1000)