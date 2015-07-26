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

import xbmc, xbmcaddon

if __name__ == '__main__':	

    # PseudoTV Live Globals
    ADDON_ID = 'script.pseudotv.live'
    REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
    ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
    ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
    ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
    ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
    
    # InfoLabel Parameters  
    label    = xbmc.getInfoLabel('ListItem.Label')
    path     = xbmc.getInfoLabel('ListItem.FolderPath')
    filename = xbmc.getInfoLabel('ListItem.FilenameAndPath')
    dbidtype = xbmc.getInfoLabel('ListItem.DBTYPE')
    addonName = xbmc.getInfoLabel('Container.PluginName')
    addonType = xbmc.getInfoLabel('Container.Property(addoncategory)')
    description = xbmc.getInfoLabel('ListItem.Property(Addon.Description)')
    plot = xbmc.getInfoLabel('ListItem.Plot')
    plotOutline = xbmc.getInfoLabel('ListItem.PlotOutline')
    isPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)').lower() == 'true'
    isFolder = xbmc.getCondVisibility('ListItem.IsFolder') == 1
    
    if not plot:
        if plotOutline:
            description = plotOutline
        elif not description:   
            description = label
    else:  
        description = plot

    data = ['Label='+label,'Path='+path,'FileName='+filename,'DBIDType='+dbidtype,'AddonName='+addonName,'AddonType='+addonType,'Description='+description,'isPlayable='+str(isPlayable),'isFolder='+str(isFolder)]
    
    # Pass arguments to PseudoTV Live
    xbmc.executebuiltin("RunScript("+ADDON_PATH+"/capture.py, %s)" %str(data))
    