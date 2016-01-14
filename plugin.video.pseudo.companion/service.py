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

while (not xbmc.abortRequested):
    PTVL_RUNNING = xbmcgui.Window(10000).getProperty('PseudoTVRunning') == "True"
    if PTVL_RUNNING == True:
        STATE = 'true'
        STATUS = '[COLOR=green]ONLINE[/COLOR]'
    else:
        STATE = 'false'
        STATUS = '[COLOR=red]OFFLINE[/COLOR]'
    xbmcgui.Window(10000).setProperty('PseudoCompanion.STATE', STATE)
    xbmcgui.Window(10000).setProperty('PseudoCompanion.STATUS', STATUS)
    xbmc.sleep(1000)