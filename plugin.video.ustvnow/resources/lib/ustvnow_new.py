'''
    ustvnow XBMC Plugin
    Copyright (C) 2015 t0mm0, jwdempsey, esxbr, Lunatixz

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
import cookielib
import os
import re
import urllib, urllib2
import simplejson as json
import xbmcgui, xbmc, xbmcvfs
import Addon

from xml.dom import minidom
from time import time
from datetime import datetime, timedelta

# Commoncache plugin import
try:
    import StorageServer
except Exception,e:
    import storageserverdummy as StorageServer


class Ustvnow:
    __BASE_URL = 'http://m.ustvnow.com'
    def __init__(self, user, password, premium):
        self.token = None
        self.user = user
        self.password = password
        self.premium = premium
        self.dlg = xbmcgui.Dialog()
        self.cache  = StorageServer.StorageServer("plugin://plugin.video.ustvnow/" + "cache",1)
        
    def get_tvguide(self, filename, type='channels', name=''):
        Addon.log('get_tvguide,' + type + ',' + name)
        return Addon.readXMLTV(filename, type, name)
        
    def get_channels(self, quality=1, stream_type='rtmp'):
        Addon.log('get_channels,' + str(quality) + ',' + stream_type)
        write_type = int(Addon.get_setting('write_type'))
        if self._login():
            content = self._get_json('gtv/1/live/listchannels', {'token': self.token})
            channels = []
            #print json.dumps(content);
            results = content['results']['streamnames'];
            for i in results:
                name = Addon.cleanChanName(i['sname'])
                url = "plugin://plugin.video.ustvnow/?name="+name+"&mode=play"
                channels.append({
                    'name': name,
                    'sname' : i['callsign'],
                    'url': url,
                    'icon': self.__BASE_URL + '/' + i['img']
                    })  
                if Addon.get_setting('enablewrite') == "true" and write_type == 0:
                    Addon.makeSTRM(name, url)
            if Addon.get_setting('enablewrite') == "true" and write_type > 0:
                Addon.makeM3U(self.get_link(quality, stream_type, self.token))
            return channels
            
# LIVETV           = BASE_URL + '/iphone/1/live/playingnow?pgonly=true&token=%s'
# RECORDINGS       = BASE_URL + '/iphone/1/dvr/viewdvrlist?pgonly=true&token=%s'
# FAVORITES        = BASE_URL + '/iphone/1/live/showfavs?pgonly=true&token=%s'

    def get_favorites(self, quality=1, stream_type='rtmp'):
        print 'get_channels'
        # if self.token == None:
            # if self._login():
                # content = self._get_json('gtv/1/live/listchannels', {'token': self.token})
        # channels = []
        # #print json.dumps(content);
        # results = content['results']['streamnames'];
        # print results
        # for i in results:
            # url = "plugin://plugin.video.ustvnow/?name="+i['sname']+"&mode=play"
            # name = (i['sname'])
            # # name = name.replace('WLYH','CW').replace('WHTM','ABC').replace('WPMT','FOX').replace('WPSU','PBS').replace('WHP','CBS').replace('WGAL','NBC').replace('My9','MY9').replace('AETV','AE').replace('Channel','').replace('Network','')
            # channels.append({
                # 'name': name,
                # 'sname' : i['callsign'],
                # 'url': url, 
                # 'icon': self.__BASE_URL + '/' + i['img']
                # })  
        # print channels
        # return channels

    def get_guidedata(self):
        try:
            result = self.cache.cacheFunction(self.get_guidedata_NEW)
        except:
            result = self.get_guidedata_NEW()
            pass
        if not result:
            result = self.get_guidedata_NEW()
        return result  

    def get_guidedata_NEW(self):
        Addon.log('get_guidedata')
        if self._login():
            content = self._get_json('gtv/1/live/channelguide', {'token': self.token})
            results = content['results'];
            now = time();
            doc = minidom.Document();
            base = doc.createElement('tv');
            base.setAttribute("cache-version", str(now));
            base.setAttribute("cache-time", str(now));
            base.setAttribute("generator-info-name", "IPTV Plugin");
            base.setAttribute("generator-info-url", "http://www.xmltv.org/");
            doc.appendChild(base)
            channels = self.get_channels();

            for channel in channels:
                name = channel['name'];
                id = channel['sname'];
                c_entry = doc.createElement('channel');
                c_entry.setAttribute("id", id);
                base.appendChild(c_entry)
                dn_entry = doc.createElement('display-name');
                dn_entry_content = doc.createTextNode(name);
                dn_entry.appendChild(dn_entry_content);
                c_entry.appendChild(dn_entry);
                dn_entry = doc.createElement('display-name');
                dn_entry_content = doc.createTextNode(id);
                dn_entry.appendChild(dn_entry_content);
                c_entry.appendChild(dn_entry);
                icon_entry = doc.createElement('icon');
                icon_entry.setAttribute("src", channel['icon']);
                c_entry.appendChild(icon_entry);

            for programme in results:
                start_time 	= datetime.fromtimestamp(float(programme['ut_start']));
                stop_time	= start_time + timedelta(seconds=int(programme['guideremainingtime']));
                
                pg_entry = doc.createElement('programme');
                pg_entry.setAttribute("start", start_time.strftime('%Y%m%d%H%M%S 0'));
                pg_entry.setAttribute("stop", stop_time.strftime('%Y%m%d%H%M%S 0'));
                pg_entry.setAttribute("channel", programme['callsign']);
                base.appendChild(pg_entry);
                
                t_entry = doc.createElement('title');
                t_entry.setAttribute("lang", "en");
                t_entry_content = doc.createTextNode(programme['title']);
                t_entry.appendChild(t_entry_content);
                pg_entry.appendChild(t_entry);
                
                st_entry = doc.createElement('sub-title');
                st_entry.setAttribute("lang", "en");
                st_entry_content = doc.createTextNode(programme['episode_title']);
                st_entry.appendChild(st_entry_content);
                pg_entry.appendChild(st_entry);

                d_entry = doc.createElement('desc');
                d_entry.setAttribute("lang", "en");
                d_entry_content = doc.createTextNode(programme['synopsis']);
                d_entry.appendChild(d_entry_content);
                pg_entry.appendChild(d_entry);

                dt_entry = doc.createElement('date');
                dt_entry_content = doc.createTextNode(start_time.strftime('%Y%m%d'));
                dt_entry.appendChild(dt_entry_content);
                pg_entry.appendChild(dt_entry);

                c_entry = doc.createElement('category');
                c_entry_content = doc.createTextNode(programme['xcdrappname']);
                c_entry.appendChild(c_entry_content);
                pg_entry.appendChild(c_entry);


                en_entry = doc.createElement('episode-num');
                en_entry.setAttribute('system', 'dd_progid');
                en_entry_content = doc.createTextNode(programme['content_id']);
                en_entry.appendChild(en_entry_content);
                pg_entry.appendChild(en_entry);

                i_entry = doc.createElement('icon');
                i_entry.setAttribute("src", self.__BASE_URL + '/' + programme['img']);
                pg_entry.appendChild(i_entry);
            return doc


    def _build_url(self, path, queries={}):
        if queries:
            query = urllib.urlencode(queries)
            return '%s/%s?%s' % (self.__BASE_URL, path, query)
        else:
            return '%s/%s' % (self.__BASE_URL, path)

    def _fetch(self, url, form_data=False):
        if form_data:
            req = urllib2.Request(url, form_data)
        else:
            req = url
        try:
            response = urllib2.urlopen(url)
            return response
        except urllib2.URLError, e:
            return False

    def _get_json(self, path, queries={}):
        content = False
        url = self._build_url(path, queries)
        response = self._fetch(url)
        if response:
            content = json.loads(response.read())
        else:
            content = False
        return content

    def _get_html(self, path, queries={}):
        html = False
        url = self._build_url(path, queries)

        response = self._fetch(url)
        if response:
            html = response.read()
        else:
            html = False
        return html

    def get_link(self, quality=1, stream_type='rtmp', token=False):
        Addon.log('get_link')
        if self._login(token):
            self.__BASE_URL = 'http://lv2.ustvnow.com';
            # self.__BASE_URL = 'http://lv5.ustvnow.com';
            # self.__BASE_URL = 'http://lv7.ustvnow.com';
            # self.__BASE_URL = 'http://lv9.ustvnow.com';
            html = self._get_html('iphone_ajax', {'tab': 'iphone_playingnow', 'token': self.token})
            channels = []
            achannels = []
            for channel in re.finditer('class="panel".+?title="(.+?)".+?src="' +
                                       '(.+?)".+?class="nowplaying_item">(.+?)' +
                                       '<\/td>.+?class="nowplaying_itemdesc".+?' +
                                       '<\/a>(.+?)<\/td>.+?href="(.+?)"',
                                       html, re.DOTALL):
                name, icon, title, plot, url = channel.groups()
                name = name.replace('\n','').replace('\t','').replace('\r','').replace('<fieldset> ','').replace('<div class=','').replace('>','').replace('"','').replace(' ','')
                if not name:
                    name = ((icon.rsplit('/',1)[1]).replace('.png','')).upper()
                    name = Addon.cleanChanName(name)
                try:
                    if not url.startswith('http'):
                        now = {'title': title, 'plot': plot.strip()}
                        url = '%s%s%d' % (stream_type, url[4:-1], quality + 1)
                        aChannelname = {'name': name}
                        aChannel = {'name': name, 'url': url, 
                                    'icon': icon, 'now': now}
                        if aChannelname not in achannels:
                           achannels.append(aChannelname)
                           channels.append(aChannel)
                except:
                    pass
            return channels
                    
    def _login(self, token=False, force=False):
        Addon.log('_login')
        if token != False:
            self.token = token
            return True
        self.token = None
        self.cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        url = self._build_url('gtv/1/live/login', {'username': self.user,
                                               'password': self.password,
                                               'device':'gtv',
                                               'redir':'0'})
        response = self._fetch(url)
        #response = opener.open(url)
        for cookie in self.cj:
            # print '%s: %s' % (cookie.name, cookie.value)
            if cookie.name == 'token':
                self.token = cookie.value
                return True
        return False