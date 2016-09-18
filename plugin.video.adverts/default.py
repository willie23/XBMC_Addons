import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
from BeautifulSoup import BeautifulSoup

# Plugin Info
ADDON_ID = 'plugin.video.adverts'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
THUMB = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')


#TV Adverts - by LordIndy 2011, Lunatixz
baseurl='http://www.advertolog.com'
def replaceXmlEntities(link):
    entities = (
        ("%3A",":"),("%2F","/"),("%3D","="),("%3F","?"),("%26","&"),("%22","\""),("%7B","{"),("%7D",")"),("%2C",","),("%24","$"),("%23","#"),("%40","@")
      );
    for entity in entities:
       link = link.replace(entity[0],entity[1]);
    return link;

def CATEGORIES():
        addDir('Countries','http://www.advertolog.com/countries/',3,THUMB)
        addDir('Brands','http://www.advertolog.com/brands/',4,THUMB)
        addDir('Years','http://www.advertolog.com/countries/',33,THUMB)         
        addDir('Business Sectors','http://www.advertolog.com/business-sectors/',6,THUMB)
        # addDir('Awards','http://www.advertolog.com/festivals-awards/',6,THUMB)

def BRANDORCOUNTRYPAGE(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link=link.decode('utf-8')
        soup = BeautifulSoup(link,convertEntities=BeautifulSoup.HTML_ENTITIES)
        catlink=re.compile('<a href="(.+?)" >TV & Cinema</a>').findall(link)
        if catlink:
            url=baseurl+catlink[0]
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            soup = BeautifulSoup(link)
                
        #find the year links, if any
        # yearlink=soup.find(text='Year:')
        # if yearlink:
            # yearlink=soup.find(text='Year:').findNext('div').findAll('a')
            # years=[]
            # for links in yearlink:
                # temp=re.compile('<a href="(.+?)">(.+?)</a>').findall(str(links))
                # years.append(temp[0])
            # for yearurl, name in years:
                # addDir(name,baseurl+yearurl,1,THUMB)
        
        #find the adverts, if any                    
        if soup.find('ul', "col-media-list"):
            adverts=soup.find('ul', "col-media-list").findAll('li')
            for ad in adverts:
                if ad.find(text="  TV & Cinema"):
                    name=ad.a.img["alt"].encode('UTF-8')
                    adurl=ad.a["href"]
                    thumbnail=ad.a.img["src"]
                    addDir(name,baseurl+adurl,2,thumbnail)

        # #Get the "Next Page" link, if any
        # if soup.find(text=re.compile("Next \xbb\xbb")):
            # if soup.find(text=re.compile("Next \xbb\xbb")).findPrevious('span').findAll('a'):
                # nextpage=soup.find(text=re.compile("Next \xbb\xbb")).findPrevious('span').findAll('a')
                # nextpage=re.compile('\[<a href="(.+?)">Next').findall(str(nextpage))
                # nextpage=baseurl+nextpage[0]
                # addDir("Next Page >>",nextpage,1,THUMB)


def BRANDORCOUNTRYYEAR(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link=link.decode('utf-8')
        soup = BeautifulSoup(link,convertEntities=BeautifulSoup.HTML_ENTITIES)
        catlink=re.compile('<a href="(.+?)" >TV & Cinema</a>').findall(link)
        if catlink:
            url=baseurl+catlink[0]
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            soup = BeautifulSoup(link)
                
        # find the year links, if any
        yearlink=soup.find(text='Year:')
        if yearlink:
            yearlink=soup.find(text='Year:').findNext('div').findAll('a')
            years=[]
            for links in yearlink:
                temp=re.compile('<a href="(.+?)">(.+?)</a>').findall(str(links))
                years.append(temp[0])
            for yearurl, name in years:
                addDir(name,baseurl+yearurl,1,THUMB)
                

def VIDEOLINKS(url,name):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        soup = BeautifulSoup(link)
        #GET THE VIDEO LINKS FROM THE PAGE, IF ANY
        #get the image
        image=re.compile('meta property="og:image" content="(.+?)" />').findall(link)
        if image:
            image[0]=replaceXmlEntities(image[0])
        else:
            image=''
        #get the default video link (most are hidden due to subscription, but the low res video link is hidden in the header tag    
        vid=re.compile('meta property="og:video" content="(.+?)" />').findall(link)
        if vid:
            vid[0]=replaceXmlEntities(vid[0])
            vid[0]=re.sub('http.*?clip":{"url":','/',vid[0])
            vid[0]=re.search('h.*?.mp4', vid[0]).group()
        #get alternate high res links if any
        vids=soup.find('ul',"resolutions")
        if vids:
            vids=soup.find('ul',"resolutions").findAll('a')
            vid=[]
            if vids:
                vids=soup.find('ul',"resolutions").findAll('a')
                for url in vids:
                    addLink(url.string,url['name'],image[0])
        else:
            addLink('360p',vid[0],image[0])
    
    
def LISTCOUNTRIES(url, year=False):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        countries=re.compile('<a href="/countries/(.+?)">(.+?)</a>').findall(link)
        for url,country in countries:         
            if year: 
                addDir(country,'http://www.advertolog.com/countries/'+url,10,THUMB)
            else:
                 addDir(country,'http://www.advertolog.com/countries/'+url,1,THUMB)
                 
                 
def LISTBRANDLETTERS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<h3 style="font-weight:bold; font-size:24px;"><a href=".+?" style="text-decoration:none">(.+?)</a></h3>').findall(link)
        #Get the brand letters
        letters=re.compile('<h3 style="font-weight:bold; font-size:24px;"><a href=".+?" style="text-decoration:none">(.+?)</a></h3>').findall(link)
        letters=map(lambda x: x.lower(), letters)
        for letter in letters:
            addDir(letter,'http://www.advertolog.com/brands/letter-'+letter+'/',5,THUMB)
            
            
def LISTBRANDS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        soup = BeautifulSoup(link,convertEntities=BeautifulSoup.HTML_ENTITIES)
        brands=re.compile('<a href="(.+?)" id="CompanyListingTitle_.+?">(.+?)</a>').findall(link)
        for url, name in brands:
            addDir(name,baseurl+url,1,'')
        #Get the "Next Page" link, if any
        if soup.find(text=re.compile("Next ")):
            if soup.find(text=re.compile("Next ")).findPrevious('span').findAll('a'):
                nextpage=soup.find(text=re.compile("Next ")).findPrevious('span').findAll('a')
                nextpage=re.compile('\[<a href="(.+?)">Next ').findall(str(nextpage))
                nextpage=baseurl+nextpage[0]
                addDir("Next Page >>",nextpage,5,THUMB)

def LISTSECTORS(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        soup = BeautifulSoup(link,convertEntities=BeautifulSoup.HTML_ENTITIES)
        sectors=re.compile('<a href="(.+?)/">\n        (.+?)</a>').findall(str(soup))
        sectors.sort()
        for url, name in sectors:
            addDir(name,baseurl+url,1,'')

                  
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]             
        return param

        
def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

        
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
       
       
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
       
elif mode==1:
        print ""+url
        BRANDORCOUNTRYPAGE(url)
        
elif mode==10:
        print ""+url
        BRANDORCOUNTRYYEAR(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name)

elif mode==3:
        print ""+url
        LISTCOUNTRIES(url)
        
elif mode==33:
        print ""+url
        LISTCOUNTRIES(url,True)
        
elif mode==4:
        print ""+url
        LISTBRANDLETTERS(url)

elif mode==5:
        print ""+url
        LISTBRANDS(url)

elif mode==6:
        print ""+url
        LISTSECTORS(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))