'''
    ustvnow XBMC Plugin
    Copyright (C) 2015 t0mm0, Lunatixz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from resources.lib import Addon
import sys, os
import urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon.plugin_url = sys.argv[0]
Addon.plugin_handle = int(sys.argv[1])
Addon.plugin_queries = Addon.parse_query(sys.argv[2][1:])

email = Addon.get_setting('email')
password = Addon.get_setting('password')
premium = Addon.get_setting('subscription') == "true"
stream_type = ['rtmp', 'rtsp'][int(Addon.get_setting('stream_type'))]
quality_type = int(Addon.get_setting('quality'))
dlg = xbmcgui.Dialog()
addon = xbmcaddon.Addon(id='plugin.video.ustvnow')
plugin_path = addon.getAddonInfo('path')

if Addon.get_setting('version') == '0':
    from resources.lib import ustvnow_new
    ustv = ustvnow_new.Ustvnow(email, password, premium)
    usingNewCode = True
else:
    from resources.lib import ustvnow 
    ustv = ustvnow.Ustvnow(email, password, premium)
    usingNewCode = False

if not email:
    dlg.ok("USTVnow", "Please visit www.ustvnow.com", "and register for your login credentials")
    retval = dlg.input('Enter USTVnow Account Email', type=xbmcgui.INPUT_ALPHANUM)
    if retval and len(retval) > 0:
        Addon.set_setting('email', str(retval))
        email = Addon.get_setting('email')
    retval = dlg.input('Enter USTVnow Account Password', type=xbmcgui.INPUT_ALPHANUM)
    if retval and len(retval) > 0:
        Addon.set_setting('password', str(retval))
        password = Addon.get_setting('password')
    if dlg.yesno("USTVnow", 'Are you a premium subscriber?'):
        Addon.set_setting('subscription', 'true')
    else:
        Addon.set_setting('subscription', 'false')
        
if premium == False:
    Addon.set_setting('quality', '0')
    
Addon.log('plugin url: ' + Addon.plugin_url)
Addon.log('plugin queries: ' + str(Addon.plugin_queries))
Addon.log('plugin handle: ' + str(Addon.plugin_handle))
mode = Addon.plugin_queries['mode']

if mode == 'main':
    Addon.log(mode)
    Addon.add_directory({'mode': 'live'}, Addon.get_string(30001))
    if usingNewCode == True:
        # Addon.add_directory({'mode': 'favorites'}, Addon.get_string(30006))
        Addon.add_directory({'mode': 'tvguide'}, Addon.get_string(30007))
    if premium == True and not usingNewCode:
        Addon.add_directory({'mode': 'recordings'}, Addon.get_string(30002))

elif mode == 'live':
    Addon.log(mode)
    channels = ustv.get_channels(quality_type, stream_type)
    if channels:
        for c in channels:
            rURL = "plugin://plugin.video.ustvnow/?name="+c['name']+"&mode=play"
            item = xbmcgui.ListItem(path=rURL)
            if usingNewCode == True:
                name = c["name"];
                sname = c["sname"];
                icon = c["icon"];

                for quality in range(1,4):
                    parameters = urllib.urlencode( {
                        'c': sname,
                        'i': icon,
                        'q': str(quality),
                        'u': email,
                        'p': password } );

                    if quality==1:
                        quality_name = 'Low';
                    elif quality==2:
                        quality_name = 'Medium';
                    elif quality==3:
                        quality_name = 'High';

                # todo set HD flag
                Addon.add_video_item(rURL,
                                     {'title': '%s' % (c['name'])},
                                     img=c['icon'])

            else:
                Addon.add_video_item(rURL,
                                     {'title': '%s - %s' % (c['name'], 
                                                            c['now']['title']),
                                      'plot': c['now']['plot']},
                                     img=c['icon'])
                             
elif mode == 'recordings':
    Addon.log(mode)
    stream_type = ['rtmp', 'rtsp'][int(Addon.get_setting('stream_type'))]
    recordings = ustv.get_recordings(int(Addon.get_setting('quality')), 
                                     stream_type)
    if recordings:
        for r in recordings:
            cm_del = (Addon.get_string(30003), 
                      'XBMC.RunPlugin(%s/?mode=delete&del=%s)' % 
                           (Addon.plugin_url, urllib.quote(r['del_url'])))
            title = '%s (%s on %s)' % (r['title'], r['rec_date'], r['channel'])
            Addon.add_video_item(r['stream_url'], {'title': title, 
                                                   'plot': r['plot']},
                                 img=r['icon'], cm=[cm_del], cm_replace=True)
elif mode == 'delete':
    Addon.log(mode)
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno(Addon.get_string(30000), Addon.get_string(30004), 
                       Addon.get_string(30005))
    if ret == 1:
        ustv.delete_recording(Addon.plugin_queries['del'])

elif mode == 'favorites':
    Addon.log(mode)
    favorites = ustv.get_favorites(int(Addon.get_setting('quality')), 
                                     stream_type)
elif mode == 'guidedata':
    Addon.log(mode)  
    # ex. call
    # xbmc.executebuiltin("XBMC.RunPlugin(plugin://plugin.video.ustvnow/?file=%s&mode=guidedata)" %urllib.quote(fpath))
    fpath = Addon.plugin_queries['file']               
    Addon.makeXMLTV(ustv.get_guidedata(),urllib.unquote(fpath))
    
elif mode == 'tvguide':
    Addon.log(mode)
    fpath = os.path.join(Addon.get_setting('XMLTVfolder'), 'xmltv.xml')
    try:
        name = Addon.plugin_queries['name']
        listings = ustv.get_tvguide(fpath, 'programs', name)
        if listings:
            for l in range(len(listings)):
                print listings[l]
                # breakdown time and chname
                # if time > now set rec option
                # else play channel
                rURL = "plugin://plugin.video.ustvnow/?name="+listings[l][0]+"&mode=play"
                Addon.add_video_item(rURL,
                                     {'title': '%s - %s' % (listings[l][1], 
                                                            listings[l][2]),
                                      'plot': listings[l][3]},
                                     img=listings[l][6])
    except:
        if Addon.makeXMLTV(ustv.get_guidedata(),urllib.unquote(fpath)) == True:
            listings = ustv.get_tvguide(fpath)
            if listings:
                for l in range(len(listings)):
                    # print listings[l]
                    url = "plugin://plugin.video.ustvnow/?name="+listings[l]+"&mode=tvguide"
                    Addon.log('adding dir: %s' % (listings[l]))
                    img = ''
                    fanart = ''
                    listitem = xbmcgui.ListItem(listings[l], iconImage=img, thumbnailImage=img)
                    if not fanart:
                        fanart = plugin_path + '/fanart.jpg'
                    listitem.setProperty('fanart_image', fanart)
                    xbmcplugin.addDirectoryItem(Addon.plugin_handle, url, listitem, 
                                                isFolder=True, totalItems=len(listings))
        
elif mode=='play':
    Addon.log(mode)
    name = Addon.plugin_queries['name']
    Addon.log(name)
    channels = []
    if usingNewCode == True:
        channels = ustv.get_link(name, quality_type, stream_type)
    else:
        channels = ustv.get_channels(quality_type, stream_type)
    if channels:
        for c in channels:
            Addon.log(str(c['name']) +' , '+ name)
            if c['name'] == name:
                url = c['url']
                Addon.log(url)
                item = xbmcgui.ListItem(path=url)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
Addon.end_of_directory()