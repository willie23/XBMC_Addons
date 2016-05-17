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

import sys, string, os, re, sys
import urlparse, urllib, urllib2, htmllib, threading
import platform, calendar, random, CommonFunctions
import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs
import xml.etree.ElementTree as ElementTree 

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

try:
    import StorageServer
    Cache_Enabled = settings.getSetting("cache") == "true"
except Exception,e:
    Cache_Enabled = False
    import storageserverdummy as StorageServer
    
try:
    from metahandler import metahandlers
    metaget = metahandlers.MetaData(preparezip=False)
    Meta_Enabled = True
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
#   Pull the arguments in. 
baseUrl = sys.argv[0]
addonHandle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

#
#   Pull the settings in. 
settings = xbmcaddon.Addon(id=addonId)
playonInternalUrl = settings.getSetting("playonserver").rstrip('/')
playonExternalUrl = settings.getSetting("playonid").rstrip('/')
debug = settings.getSetting("debug")
cachePeriod = 1 #hours
timeout = 15
KodiLibrary = False #todo strm contextMenu
#
#   Set-up some KODI defaults. 
common = CommonFunctions
common.plugin = addonId + '-' + addonVersion

#
#   Internal Functions 
#
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

def log_message(msg, information=False):
    """ Simple logging helper. """
    if (information or debug) and isinstance(msg, str):
        print addonId + "::" + addonVersion + ": " + msg
    elif (information or debug):
        print addonId + "::" + addonVersion + ":  ... \/ ..."
        print msg
        
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
        result = False
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
                image = playonInternalUrl + group.attrib.get('art')
                
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
                        image = playonInternalUrl + group.attrib.get('art')
                    
                    addDir(name,name,url,image,image)            
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + mediaIcon
                    else:
                        image = playonInternalUrl + group.attrib.get('art')
                    
                    playonUrl = build_playon_url(group.attrib.get('href'))
                    mediaXml = get_xml(playonUrl)
                    # mediaNode = mediaXml.find('media')
                    addLink(name,group.attrib.get('description'),url,image,image)  
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
                        image = playonInternalUrl + group.attrib.get('art')
                    
                    """
                    try:
                        
                        metaget = metahandlers.MetaData()
                        meta = metaget.get_meta('tvshow', name)
                    
                        li = xbmcgui.ListItem(name, iconImage=meta['cover_url'], thumbnailImage=meta['cover_url'])
                        li.setInfo(type="Video", infoLabels=meta)
                        li.setProperty('fanart_image', meta['backdrop_url'])
                        xbmcplugin.addDirectoryItem(handle=addonHandle, url=url, listitem=li, isFolder=True)
                    except Exception,e:
                    """
                    #log_message(str(e))
                    addDir(name,name,url,image,image)            
                elif group.attrib.get('type') == 'video':
                    if group.attrib.get('art') == None:
                        image = playonInternalUrl + mediaIcon
                    else:
                        image = playonInternalUrl + group.attrib.get('art')
                    
                    playonUrl = build_playon_url(group.attrib.get('href'))
                    mediaXml = get_xml(playonUrl)
                    # mediaNode = mediaXml.find('media')
                    """
                    try:
                        
                        metaget = metahandlers.MetaData()
                        meta = metaget.get_meta('movie', name)
                    
                        li = xbmcgui.ListItem(name, iconImage=meta['cover_url'], thumbnailImage=meta['cover_url'])
                        li.setInfo(type="Video", infoLabels=meta)
                        li.setProperty('fanart_image', meta['backdrop_url'])
                        xbmcplugin.addDirectoryItem(handle=addonHandle, url=url, listitem=li)
                    except Exception,e:
                        log_message(str(e))
                        """
                    addLink(name,group.attrib.get('description'),url,image,image)
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
                    image = playonInternalUrl + group.attrib.get('art')
                
                addDir(name,name,url,image,image)  
            elif group.attrib.get('type') == 'video':
                if group.attrib.get('art') == None:
                    image = playonInternalUrl + mediaIcon
                else:
                    image = playonInternalUrl + group.attrib.get('art')
                
                playonUrl = build_playon_url(group.attrib.get('href'))
                mediaXml = get_xml(playonUrl)
                # mediaNode = mediaXml.find('media')
                addLink(name,group.attrib.get('description'),url,image,image)      
    except:
        pass
    xbmcplugin.endOfDirectory(addonHandle)
       
def parseURLThread(nametree):
    parseURLTimer = threading.Timer(0.1, parseURL,[nametree])
    parseURLTimer.name = "parseURLTimer"
    if parseURLTimer.isAlive():
        parseURLTimer.cancel()
    parseURLTimer.start()
           
def parseURL(nametree):
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
                            return mediaNode.attrib.get('src'), group.attrib.get('name').encode('ascii', 'ignore')
   
def closeFailed():
    if xbmc.getCondVisibility('Window.IsActive(okdialog)') == 1:
        xbmc.executebuiltin('Dialog.Close(okdialog)')
        log_message("closeFailed dialog = True", True)
        return True
    log_message("closeFailed dialog = False", True)
    return False
   
def playList(src, name):       
    listitem=xbmcgui.ListItem(name)
    vplaylist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    vplaylist.clear()
    vplaylist.add(mediaPath + 'DummyEntry.mp4')
    vplaylist.add(playonExternalUrl + '/' + src.split('.')[0].split('/')[0] + '/',listitem) 
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)     
    xbmc.Player().play(vplaylist,listitem)
            
def playURL(src,name):
    cnt = 0
    # while xbmc.Player().isPlaying() == False and cnt < timeout:
    cnt += 1
    log_message("playThread: Playcount = " + str(cnt) + "/" + str(timeout), True)
    listitem=xbmcgui.ListItem(name)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
    xbmc.Player().play(playonExternalUrl + '/' + src.split('.')[0].split('/')[0] + '/',listitem)
    # xbmc.sleep(1000)
#
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
        src, name = parseURL(nametree)
        playURL(src, name)
    except:
        # Play the href directly. 
        playonUrl = build_playon_url(href)
        name = foldername.encode('ascii', 'ignore')
        mediaXml = get_xml(playonUrl)
        mediaNode = mediaXml.find('media')
        src = mediaNode.attrib.get('src')
        playURL(src, name)