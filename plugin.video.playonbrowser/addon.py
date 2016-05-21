#   Copyright (C) 2016 Lunatixz
#
#
# This file is part of Playon Browser
#
# Playon Browser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Playon Browser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Playon Browser.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, re, sys, random
import urlparse, urllib, urllib2, htmllib, threading, socket
import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs
import xml.etree.ElementTree as ElementTree 
socket.setdefaulttimeout(30)

# Plugin Info
addonId = 'plugin.video.playonbrowser'
addon = xbmcaddon.Addon(id=addonId)
addonId = addon.getAddonInfo('id')
addonName = addon.getAddonInfo('name')
addonPath = (addon.getAddonInfo('path').decode('utf-8'))
addonVersion = addon.getAddonInfo('version')
addonIcon = os.path.join(addonPath, 'icon.png')
addonFanart = os.path.join(addonPath, 'fanart.jpg')
random.seed()
mediaPath = addonPath + '/resources/media/' 
playonDataPath = '/data/data.xml'
mediaIcon = '/images/play_720.png'

#
#   Pull the arguments in. 
baseUrl = sys.argv[0]
addonHandle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

#
#   Pull the settings in. 
settings = xbmcaddon.Addon(id=addonId)

#
#   Set-up some KODI defaults. 
cachePeriod = 1 #hours
timeout = 15

KodiLibrary = False #todo strm contextMenu
debug            = settings.getSetting("debug") == "true"
Meta_Enabled     = settings.getSetting("Meta_Enabled") == "true"
useUPNP          = settings.getSetting("useUPNP") == "true"
playDirect       = settings.getSetting("playDirect") == "true"
TVDB_API_KEY     = settings.getSetting("TVDB_API_KEY")
TMDB_API_KEY     = settings.getSetting("TMDB_API_KEY")
FANARTTV_API_KEY = settings.getSetting("FANARTTV_API_KEY")

try:
    import StorageServer
    Cache_Enabled = settings.getSetting("cache") == "true"
except Exception,e:
    Cache_Enabled = False
    import storageserverdummy as StorageServer
    
try:
    from metahandler import metahandlers
    Meta_Enabled = settings.getSetting("Meta_Enabled") == "true"
    metaget = metahandlers.MetaData(preparezip=False, tmdb_api_key=TMDB_API_KEY)
except Exception,e:
    Meta_Enabled = False

displayCategories = {'MoviesAndTV': 3,
                    'Comedy': 128,
                    'News': 4,
                    'Sports': 8,
                    'Kids': 16,
                    'Music': 32,
                    'VideoSharing': 64,
                    'LiveTV': 2048,
                    'MyMedia': 256,
                    'Plugins': 512,
                    'Other': 1024}
                        
displayTitles = {'MoviesAndTV': 'Movies And TV',
                'News': 'News',
                'Popular': 'Popular',
                'All': 'All',
                'Sports': 'Sports',
                'Kids': 'Kids',
                'Music': 'Music',
                'VideoSharing': 'Video Sharing',
                'Comedy': 'Comedy',
                'MyMedia': 'My Media',
                'Plugins': 'Plugins',
                'Other': 'Other',
                'LiveTV': 'Live TV'}
                    
displayImages = {'MoviesAndTV': '/images/categories/movies.png',
                'News': '/images/categories/news.png',
                'Popular': '/images/categories/popular.png',
                'All': '/images/categories/all.png',
                'Sports': '/images/categories/sports.png',
                'Kids': '/images/categories/kids.png',
                'Music': '/images/categories/music.png',
                'VideoSharing': '/images/categories/videosharing.png',
                'Comedy': '/images/categories/comedy.png',
                'MyMedia': '/images/categories/mymedia.png',
                'Plugins': '/images/categories/plugins.png',
                'Other': '/images/categories/other.png',
                'LiveTV': '/images/categories/livetv.png'}

#
#   Internal Functions 
#       
def log_message(msg, information=False):
    """ Simple logging helper. """
    if (information or debug) and isinstance(msg, str):
        print addonId + "::" + addonVersion + ": " + msg
    elif (information or debug):
        print addonId + "::" + addonVersion + ":  ... \/ ..."
        print msg
        
def getUPNP():
    upnpID = settings.getSetting("playonUPNPid").rstrip('/')
    if len(upnpID) > 0:
        return upnpID
    else:
        json_query = ('{"jsonrpc":"2.0","method":"Files.GetDirectory","params":{"directory":"upnp://"},"id":1}')      
        data = xbmc.executeJSONRPC(json_query)
        detail = re.compile("{(.*?)}", re.DOTALL ).findall(data)
        for f in detail:
            labels = re.search('"label" *: *"(.*?)"', f)
            if labels and len(labels.group(1)) > 0 and labels.group(1).startswith('PlayOn:'):
                files = re.search('"file" *: *"(.*?)"', f)
                upnpID = files.group(1)  
                if len(upnpID) > 0:
                    settings.setSetting("playonUPNPid",files.group(1))
                    return upnpID
        settings.openSettings()
   
def folderIcon(val):
    return random.choice(['/images/folders/folder_%s_0.png' %val,'/images/folders/folder_%s_1.png' %val])

def addDir(name,description,u,thumb=addonIcon,ic=addonIcon,fan=addonFanart,infoList=False,infoArt=False,content_type='movies'):
    liz = xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'false')

    if KodiLibrary == True:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s)'%(build_url({'mode': 'strmDir', 'url':u}))))
        liz.addContextMenuItems(contextMenu)

    if infoList == False:
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "mediatype": content_type})
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
        
    if infoArt == False:
        liz.setArt({'thumb': ic, 'fanart': fan})
    else:
        liz.setArt(infoArt) 
    xbmcplugin.setContent(addonHandle, content_type)
    xbmcplugin.addDirectoryItem(handle=addonHandle,url=u,listitem=liz,isFolder=True)
      
def addLink(name,description,u,thumb=addonIcon,ic=addonIcon,fan=addonFanart,infoList=False,infoArt=False,content_type='movies',total=0):
    liz = xbmcgui.ListItem(name)
    liz.setProperty('IsPlayable', 'true')
    
    if KodiLibrary == True:
        contextMenu = []
        contextMenu.append(('Create Strm','XBMC.RunPlugin(%s)'%(build_url({'mode': 'strmFile', 'url':u}))))
        liz.addContextMenuItems(contextMenu)

    if infoList == False:
        liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description})
    else:
        liz.setInfo(type="Video", infoLabels=infoList)
    
    if infoArt == False:
        liz.setArt({'thumb': ic, 'fanart': fan})
    else:
        liz.setArt(infoArt)
    xbmcplugin.setContent(addonHandle, content_type)
    xbmcplugin.addDirectoryItem(handle=addonHandle,url=u,listitem=liz,totalItems=total)

def build_url(query):
    """ This will build and encode the URL for the addon. """
    log_message(query)
    return baseUrl + '?' + urllib.urlencode(query)

def build_playon_url(href = ""):
    """ This will generate the correct URL to access the XML pushed out by the machine running playon. """
    log_message('build_playon_url: '+ href)
    if not href:
        return playonInternalUrl + playonDataPath
    else:
        return playonInternalUrl + href

def build_playon_search_url(id, searchterm):
    """ Generates a search URL for the given ID. Will only work with some providers. """
    log_message('build_playon_search_url: '+ id + "::" + searchterm)
    #TODO: work out the full search term criteria.
    #TODO: Check international encoding.
    searchterm = urllib.quote_plus(searchterm)
    log_message('build_playon_search_url: '+ id + "::" + searchterm)
    return playonInternalUrl + playonDataPath + "?id=" + id + "&searchterm=dc:description%20contains%20" + searchterm

def get_xml(url):
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    if Cache_Enabled == True:  
        commoncache = StorageServer.StorageServer("plugin.video.playonbrowser",cachePeriod)
        try:
            result = commoncache.cacheFunction(get_xml_request, url)
        except:
            result = get_xml_request(url)
    else:
        result = get_xml_request(url)
    if len(result) == 0:
        result = []
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    return result  
        
def get_xml_request(url):
    """ This will pull down the XML content and return a ElementTree. """
    try:
        log_message('get_xml: ' + url)
        usock = urllib2.urlopen(url)
        response = usock.read()
        usock.close()
        return ElementTree.fromstring(response)
    except: return False 

def get_argument_value(name):
    """ pulls a value out of the passed in arguments. """
    if args.get(name, None) is None:
        return None
    else:
        return args.get(name, None)[0]

def build_menu_for_mode_none():
    """
        This generates a static structure at the top of the menu tree. 
        It is the same as displayed by m.playon.tv when browsed to. 
    """
    log_message('build_menu_for_mode_none')
    
    for key, value in sorted(displayCategories.iteritems(), key=lambda (k,v): (v,k)):
        url = build_url({'mode': 'category', 'category':displayCategories[key]})
        image = playonInternalUrl + displayImages[key]
        addDir(displayTitles[key],displayTitles[key],url,image,image)   
    xbmcplugin.endOfDirectory(addonHandle)

def build_menu_for_mode_category(category):
    log_message('build_menu_for_mode_category:' + category)
    ranNum = random.randrange(9)
    """
        This generates a menu for a selected category in the main menu. 
        It uses the category value to & agains the selected category to see if it
        should be shown. 
    """
    """ Pull back the whole catalog
        Sample XMl blob:
            <catalog apiVersion="1" playToAvailable="true" name="server" href="/data/data.xml?id=0" type="folder" art="/images/apple_touch_icon_precomposed.png" server="3.10.13.9930" product="PlayOn">
                <group name="PlayMark" href="/data/data.xml?id=playmark" type="folder" childs="0" category="256" art="/images/provider.png?id=playmark" />
                <group name="PlayLater Recordings" href="/data/data.xml?id=playlaterrecordings" type="folder" childs="0" category="256" art="/images/provider.png?id=playlaterrecordings" />
                <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" childs="0" searchable="true" id="netflix" category="3" art="/images/provider.png?id=netflix" />
                <group name="Amazon Instant Video" href="/data/data.xml?id=amazon" type="folder" childs="0" searchable="true" id="amazon" category="3" art="/images/provider.png?id=amazon" />
                <group name="HBO GO" href="/data/data.xml?id=hbogo" type="folder" childs="0" searchable="true" id="hbogo" category="3" art="/images/provider.png?id=hbogo" />
                ...
    """
    try:
        for group in get_xml(build_playon_url()).getiterator('group'):
            # Category number. 
            if group.attrib.get('category') == None:
                nodeCat = 1024
            else:
                nodeCat = group.attrib.get('category')

            # Art if there is any. 
            if group.attrib.get('art') == None:
                image = playonInternalUrl + folderIcon(ranNum)
            else:
                image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                
            # if we & them and it is not zero add it to this category. otherwise ignore as it is another category.                        
            if int(nodeCat) & int(category) != 0:
                name = group.attrib.get('name').encode('ascii', 'ignore') #TODO: Fix for international characters.
                url = build_url({'mode': group.attrib.get('type'), 
                                 'foldername': name, 
                                 'href': group.attrib.get('href'), 
                                 'nametree': name})
                addDir(name,name,url,image,image)  
        xbmcplugin.endOfDirectory(addonHandle)
    except:
        pass
        
def build_menu_for_search(xml):
    ranNum = random.randrange(9)
    """ 
        Will generate a list of directory items for the UI based on the xml values. 
        This breaks the normal name tree approach for the moment

        Results can have folders and videos. 
        
        Example XML Blob:
        http://192.168.0.140:54479/data/data.xml?id=netflix&searchterm=dc:description%20contains%20american+dad
        <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
            <group name="American Dad!" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
        </group>

        http://192.168.0.140:54479/data/data.xml?id=netflix&searchterm=dc:description%20contains%20dog

        <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
            <group name="Clifford the Big Red Dog" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="Courage the Cowardly Dog" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="Dogs with Jobs" href="/data/data.xml?id=netflix-..." type="folder" childs="0" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="The 12 Dogs of Christmas" href="/data/data.xml?id=netflix-..." type="video" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
            <group name="12 Dogs of Christmas: Great Puppy Rescue" href="/data/data.xml?id=netflix-..." type="video" art="/images/poster.jpg?id=netflix-...&amp;size=large" />
    """
    try:
        for group in xml.getiterator('group'):
            log_message(group.attrib.get('href'))
            # This is the top group node, just need to check if we can search. 
            if group.attrib.get('searchable') != None:
                # We can search at this group level. Add a list item for it. 
                name = "Search" #TODO: Localize
                url = build_url({'mode': 'search', 'id': group.attrib.get('id')})
                addDir(name,name,url,image,image)  
            else:
            
                # Build up the name tree.
                name = group.attrib.get('name').encode('ascii', 'ignore')
                url = build_url({'mode': group.attrib.get('type'), 
                                    'foldername': name, 
                                    'href': group.attrib.get('href'), 
                                    'parenthref': group.attrib.get('href')}) #,'nametree': nametree + '/' + name

                if group.attrib.get('type') == 'folder':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + folderIcon(ranNum)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                        
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = (playonInternalUrl + mediaIcon)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                    # playonUrl = build_playon_url(group.attrib.get('href'))
                    # mediaXml = get_xml(playonUrl)
                    # mediaNode = mediaXml.find('media')
                    
                List, Art = getMeta(nametree, name, group.attrib.get('description'), image)
                if group.attrib.get('type') == 'folder':
                    addDir(name,name,url,image,image,infoList=List, infoArt=Art)  
                elif group.attrib.get('type') == 'video':
                    addLink(name,group.attrib.get('description'),url,image,image,infoList=List, infoArt=Art) 
    except:
        pass
    xbmcplugin.endOfDirectory(addonHandle)

def build_menu_for_mode_folder(href, foldername, nametree):
    log_message("Entering build_menu_for_mode_folder")
    ranNum = random.randrange(9)
    """ 
        Will generate a list of directory items for the UI based on the xml values. 

        The folder could be at any depth in the tree, if the category is searchable
        then we can render a search option. 
        
        Example XML Blob:
            <group name="Netflix" href="/data/data.xml?id=netflix" type="folder" art="/images/provider.png?id=netflix" searchable="true" id="netflix" childs="0" category="3">
                <group name="My List" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Browse Genres" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Just for Kids" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
                <group name="Top Picks for Jon" href="/data/data.xml?id=netflix-..." type="folder" childs="0" />
    """
    try:
        for group in get_xml(build_playon_url(href)).getiterator('group'):
            log_message(group.attrib.get('href') + href)
            # This is the top group node, just need to check if we can search. 
            if group.attrib.get('href') == href:
                if group.attrib.get('searchable') != None:
                    # We can search at this group level. Add a list item for it. 
                    name = "Search" #TODO: Localize
                    url = build_url({'mode': 'search', 'id': group.attrib.get('id')})
                    addDir(name,name,url)
            else:
            
                # Build up the name tree.
                name = group.attrib.get('name').encode('ascii', 'ignore')
                if nametree == None:
                    url = build_url({'mode': group.attrib.get('type'), 
                                    'foldername': name, 
                                    'href': group.attrib.get('href'), 
                                    'parenthref': href})
                else:
                    url = build_url({'mode': group.attrib.get('type'), 
                                    'foldername': name, 
                                    'href': group.attrib.get('href'), 
                                    'parenthref': href, 
                                    'nametree': nametree + '/' + name})
                
                log_message("url = " + url)

                if group.attrib.get('type') == 'folder':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + folderIcon(ranNum)
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')        
                
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + mediaIcon
                    else:
                        image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large') 
                    # playonUrl = build_playon_url(group.attrib.get('href'))
                    # mediaXml = get_xml(playonUrl)
                    # mediaNode = mediaXml.find('media')

                List, Art = getMeta(nametree, name, group.attrib.get('description'), image)
                if group.attrib.get('type') == 'folder':
                    addDir(name,name,url,image,image,infoList=List, infoArt=Art)  
                elif group.attrib.get('type') == 'video':
                    addLink(name,group.attrib.get('description'),url,image,image,infoList=List, infoArt=Art) 
                    
        xbmcplugin.endOfDirectory(addonHandle)
    except:
        pass
        
def generate_list_items(xml, href, foldername, nametree):
    ranNum = random.randrange(9)
    """ Will generate a list of directory items for the UI based on the xml values. """
    try:
        for group in xml.getiterator('group'):
            if group.attrib.get('href') == href:
                continue
            
            # Build up the name tree. 
            name = group.attrib.get('name').encode('ascii', 'ignore')
            url = build_url({'mode': group.attrib.get('type'), 
                                'foldername': name, 
                                'href': group.attrib.get('href'), 
                                'parenthref': href, 
                                'nametree': nametree + '/' + name})

            if group.attrib.get('type') == 'folder':
                if group.attrib.get('art') == None:
                    image = playonInternalUrl + folderIcon(ranNum)
                else:
                    image = (playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')
                    
            elif group.attrib.get('type') == 'video':
                if group.attrib.get('art') == None:
                    image = playonInternalUrl + mediaIcon
                else:
                    image = ((playonInternalUrl + group.attrib.get('art')).replace('&size=tiny','&size=large')).replace('&size=tiny','&size=large')
                
                # playonUrl = build_playon_url(group.attrib.get('href'))
                # mediaXml = get_xml(playonUrl)
                # mediaNode = mediaXml.find('media')
            
            List, Art = getMeta(nametree, name, group.attrib.get('description'), image)
            if group.attrib.get('type') == 'folder':
                addDir(name,name,url,image,image,infoList=List, infoArt=Art)  
            elif group.attrib.get('type') == 'video':
                addLink(name,group.attrib.get('description'),url,image,image,infoList=List, infoArt=Art)      
    except:
        pass
    xbmcplugin.endOfDirectory(addonHandle)
       
def getTitleYear(showtitle, showyear=0):  
    # extract year from showtitle, merge then return
    try:
        showyear = int(showyear)
    except:
        showyear = showyear
    try:
        labelshowtitle = re.compile('(.+?) [(](\d{4})[)]$').findall(showtitle)
        title = labelshowtitle[0][0]
        year = int(labelshowtitle[0][1])
    except Exception,e:
        try:
            year = int(((showtitle.split(' ('))[1]).replace(')',''))
            title = ((showtitle.split('('))[0])
        except Exception,e:
            if showyear != 0:
                showtitle = showtitle + ' ('+str(showyear)+')'
                year, title, showtitle = getTitleYear(showtitle, showyear)
            else:
                title = showtitle
                year = 0
    if year == 0 and int(showyear) !=0:
        year = int(showyear)
    if year != 0 and '(' not in title:
        showtitle = title + ' ('+str(year)+')' 
    log_message("getTitleYear, return " + str(year) +', '+ title +', '+ showtitle) 
    return year, title, showtitle
         
def getMeta(nametree, name, plot, poster):
    log_message("getMeta")
    if len(nametree) > 0:
        print nametree
        if 'movie' in nametree.lower():
            return getMovieMeta(name, plot, poster)
    return False, False
    
def getMovieMeta(name, plot, poster):
    log_message("getMovieMeta")
    try:
        year, title, showtitle = getTitleYear(name)
        if Meta_Enabled == False:
            log_message("Meta_Enabled = False")
            raise Exception()
            
        if year == 0 and Meta_Bypass == False:
            log_message("Meta_Bypass = False")
            raise Exception()
            
        meta = metaget.get_meta('movie', title, str(year))
        infoList = {}
        infoList['mediatype'] = 'movie'
        infoList['year']      = int(year                              or (meta['year']               or '0'))
        infoList['duration']  = int((meta['duration']                 or '0'))
        infoList['plot']      = (plot                                 or (meta['plot']               or ''))
        infoList['title']     = (title                                or (meta['title']              or ''))
        infoList['tagline']   = ((meta['tagline']                     or ''))
        infoList['code']      = (meta['imdb_id']                      or '0')
        infoList['playcount'] = int((meta['playcount']                or '1'))
        infoList['rating']    = float(meta['rating']                  or '0.0')
        infoList['genre']     = (meta['genre'].split(',')[0]          or 'Unknown')
        infoList['mpaa']      = (meta['mpaa']                         or 'NR')
        
        infoArt = {}
        infoList['icon']      = poster
        infoArt['thumb']      = poster
        infoArt['poster']     = (poster                               or meta['cover_url'])
        infoArt['fanart']     = (meta['backdrop_url']                 or '')
        infoArt['landscape']  = (meta['backdrop_url']                 or '')
        infoArt['banner']     = (meta['banner_url']                   or '')
        return infoList, infoArt
    except Exception, e:
        log_message(e)
        return False, False
    
def getTVmeta(name, plot, poster):
    log_message("getTVmeta")
    try:
        year, title, showtitle = getTitleYear(name)
        if Meta_Enabled == False:
            log_message("Meta_Enabled = False")
            raise Exception()
            
        if year == 0 and Meta_Bypass == False:
            log_message("Meta_Bypass = False")
            raise Exception()
            
        meta = metaget.get_meta('tvshow', title, str(year))
        year     = int(year                              or (meta['year']               or '0'))
        duration = int((meta['duration']                 or '0'))
        plot     = (plot                                 or (meta['plot']               or ''))
        title    = (title                                or (meta['title']              or ''))
        tvdb_id  = (meta['tvdb_id']                      or '0')
        playcount= int((meta['playcount']                or '1'))
        stars    = float(meta['rating']                  or '0.0')
        genre    = (meta['genre'].split(',')[0]          or 'Unknown')
        rating   = (meta['mpaa']                         or 'NR')
        poster   = (poster                               or meta['cover_url'])
        fanart   = (meta['backdrop_url']                 or '')
        banner   = (meta['banner_url']                   or '')
        return infoList, infoArt
    except Exception, e:
        log_message(e)
        return False, False
  
def parseURL(nametree):
    log_message("parseURL", True)
    # Run though the name tree! No restart issues but slower.
    nametreelist = nametree.split('/')
    roothref = None
    for group in get_xml(build_playon_url()).getiterator('group'):
        if group.attrib.get('name') == nametreelist[0]:
            roothref = group.attrib.get('href')

    if roothref != None:
        for i, v in enumerate(nametreelist):
            log_message("Level:" + str(i) + " Value:" + v)
            if i != 0:
                xml = get_xml(build_playon_url(roothref))
                for group in xml.getiterator('group'):
                    if group.attrib.get('name') == v:
                        roothref = group.attrib.get('href')
                        type = group.attrib.get('type')
                        if type == 'video':
                            mediaNode = get_xml(build_playon_url(group.attrib.get('href'))).find('media')
                            return mediaNode.attrib.get('src'), group.attrib.get('name').encode('ascii', 'ignore'), mediaNode.attrib.get('art')
def closeFailed():
    if xbmc.getCondVisibility('Window.IsActive(okdialog)') == 1:
        xbmc.executebuiltin('Dialog.Close(okdialog)')
        log_message("closeFailed dialog = True", True)
        return True
    log_message("closeFailed dialog = False", True)
    return False

def play_resolved_url(src, name, art):
    log_message("play_resolved_url")
    if useUPNP == False:
        url = playonInternalUrl + '/' + src
    else:
        url = playonExternalUrl + '/' + src.split('.')[0].split('/')[0] + '/'
    listitem = xbmcgui.ListItem(name, iconImage=art, thumbnailImage=art)
    listitem = xbmcgui.ListItem(path=url)
    listitem.setProperty('IsPlayable', 'true')
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def direct_play(src, name, art):
    log_message("direct_play")
    if useUPNP == False:
        url = playonInternalUrl + '/' + src
    else:
        url = playonExternalUrl + '/' + src.split('.')[0].split('/')[0] + '/'

    xlistitem = xbmcgui.ListItem(name, iconImage=art, thumbnailImage=art, path=url)
    xlistitem.setInfo( "video", { "Title": name } )
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    playlist.add(mediaPath + 'DummyEntry.mp4')
    playlist.add( url, xlistitem )
    player_type = xbmc.PLAYER_CORE_AUTO
    xbmcPlayer = xbmc.Player( player_type )
    xbmcPlayer.play(playlist)

def playURL(src, name, art):
    log_message("playURL", True)
    # play_resolved_url(src, name, art)
    direct_play(src, name, art)

#    Main Loop
log_message("Base URL:" + baseUrl, True)
log_message("Addon Handle:" + str(addonHandle), True)
log_message("Arguments", True)
log_message(args, True)

# Pull out the URL arguments for usage. 
mode = get_argument_value('mode')
foldername = get_argument_value('foldername')
nametree = get_argument_value('nametree')
href = get_argument_value('href')
searchable = get_argument_value('searchable')
category = get_argument_value('category')
id = get_argument_value('id')

playonInternalUrl = settings.getSetting("playonserver").rstrip('/')
playonExternalUrl = getUPNP().rstrip('/')
log_message('playonInternalUrl = ' + playonInternalUrl)
log_message('playonExternalUrl = ' + playonExternalUrl)

if mode is None: #building the main menu... Replicate the XML structure. 
    build_menu_for_mode_none()

elif mode == 'search':
    searchvalue = xbmcgui.Dialog().input("What are you looking for?")
    log_message("Search Request:" +searchvalue)
    if (log_message != ""):
        searchurl = build_playon_search_url(id, searchvalue)
        xml = get_xml(searchurl)
        log_message(xml)
        build_menu_for_search(xml)

elif mode == 'category': # Category has been selected, build a list of items under that category. 
    build_menu_for_mode_category(category)

elif mode == 'folder': # General folder handling. 
    build_menu_for_mode_folder(href, foldername, nametree)

elif mode == 'video' : # Video link from Addon or STRM. Parse and play. 
    """ We are doing a manual play to handle the id change during playon restarts. """
    log_message("In a video:" + foldername + "::" + href )   
    try:
        if playDirect == True:
            raise Exception()
        src, name, art = parseURL(nametree)
        playURL(src, name, art)
    except Exception:
        # Play the href directly. 
        playonUrl = build_playon_url(href)
        name = foldername.encode('ascii', 'ignore')
        mediaXml = get_xml(playonUrl)
        mediaNode = mediaXml.find('media')
        src = mediaNode.attrib.get('src')
        art = mediaNode.attrib.get('art')
        playURL(src, name, art)