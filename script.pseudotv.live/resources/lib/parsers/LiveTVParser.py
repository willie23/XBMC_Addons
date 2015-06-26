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

class LiveTVParser:
    def __init__(self):
        self.chanlist = ChannelList()
          
    def log(self, msg, level = xbmc.LOGDEBUG):
        log('LiveTVParser: ' + msg, level)
        
    def logDebug(self, msg, level = xbmc.LOGDEBUG):
        if DEBUG == 'true':
            log('LiveTVParser: ' + msg, level)
            
    def HDHRAutotune(self, channelNum):
        try:
            HDHRNameList, HDHRPathList = chanlist.fillHDHR()
            HDHRNameList = HDHRNameList[1:]
            HDHRPathList = HDHRPathList[1:]
            
            for HDUPNPnum in range(len(HDHRNameList)):
                HDHRname = HDHRNameList[HDUPNPnum]

                CHid = HDHRname.split(' - ')[0]
                CHname = HDHRname.split(' - ')[1]
                CHname = chanlist.CleanLabels(CHname, 'upper')
                path = HDHRPathList[HDUPNPnum]

                if xbmcvfs.exists(xmlTvFile): 
                    CHSetName, CHzapit = chanlist.findZap2itID(CHname, xmlTvFile)

                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_type", "8")
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_time", "0")
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_1", CHzapit)
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_2", path)
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_3", "xmltv")
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rulecount", "1")
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rule_1_id", "1")
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_rule_1_opt_1", CHname + ' HDHR')    
                    Globals.ADDON_SETTINGS.setSetting("Channel_" + str(channelNum) + "_changed", "true")                        
                    self.updateDialog.update(self.updateDialogProgress,"AutoTuning","adding HDHomeRun UPNP Channels",CHname)  
                    channelNum += 1 
        except Exception,e:
            self.log("autoFindLiveHD, Failed! " + str(e))

    def buildLiveTVFileList_NEW(self, setting1, setting2, setting3, setting4, limit):
        self.log("buildLiveTVFileList_NEW")  
        showList = []
        
        # Validate XMLTV Data #
        xmltvValid = self.xmltv_ok(setting3)
        
        if xmltvValid == True: 
            now = datetime.datetime.now()
            chname = (self.getChannelName(8, self.settingChannel))
                
            try:
                if setting3 == 'pvr':
                    showList = self.fillLiveTVPVR(setting1, setting2, setting3, setting4, chname, limit)
                    MSG = 'Listing Unavailable, Check your pvr backend'
                else:   
                    showList = self.fillLiveTV(setting1, setting2, setting3, setting4, chname, limit)
                    MSG = 'Listing Unavailable, Check your '+setting3+' xmltv file'
            except Exception,e:
                self.log("buildLiveTVFileList, Error: " + str(e))
                pass  

        if not showList:
            chname = (self.getChannelName(9, self.settingChannel))
            print chname, self.settingChannel
            showList = self.buildInternetTVFileList('5400', setting2, chname, 'Guide-data from ' + str(setting3) + ' is currently unavailable.' )
        return showList     
        
    def fillLiveTV(self, setting1, setting2, setting3, setting4, chname, limit):
        self.log("fillLiveTV")
        showList = []
        showcount = 0          
        now = datetime.datetime.now()
                
        try:
            if setting3[0:4] == 'http':
                f = open_url(self.xmlTvFile)
            else:
                f = FileAccess.open(self.xmlTvFile, "r")
                
            if setting3.lower() in UTC_XMLTV:                      
                offset = ((time.timezone / 3600) - 5 ) * -1     
            else:
                offset = 0
                
            if self.background == False:
                self.updateDialog.update(self.updateDialogProgress, "Updating channel " + str(self.settingChannel), "adding LiveTV", 'parsing ' + chname)

            context = ET.iterparse(f, events=("start", "end")) 
            context = iter(context)
            event, root = context.next()

            for event, elem in context:
                if self.threadPause() == False:
                    del showList[:]
                    break
                    
                id = 0
                imdbid = 0
                tvdbid = 0
                seasonNumber = 0
                episodeNumber = 0
                Managed = False
                episodeName = ''
                episodeDesc = ''
                episodeGenre = ''
                tagline = ''
                dd_progid = ''
                type = ''
                genre = 'Unknown'
                rating = 'NR'
                LiveID = 'tvshow|0|0|False|1|NR|'
                thumburl = 0
                
                if event == "end":
                    if elem.tag == "programme":
                        channel = elem.get("channel")
                        if setting1 == channel:
                            self.log("fillLiveTV, setting1 = " + setting1 + ', channel id = ' + channel)
                            title = elem.findtext('title')

                            try:
                                test = title.split(" *")[1]
                                title = title.split(" *")[0]
                                playcount = 0
                            except Exception,e:
                                playcount = 1
                                pass

                            icon = None
                            description = elem.findtext("desc")
                            iconElement = elem.find("icon")
                            # todo grab artwork, encode, pass as dbid
                            # todo improve v-chip, mpaa ratings
                            
                            if iconElement is not None:
                                icon = iconElement.get("src")
                                thumburl = (icon.encode('base64')).replace('\n','').replace('\r','').replace('\t','')
                                
                                # if icon[0:4] == 'http' and REAL_SETTINGS.getSetting('EnhancedGuideData') == 'true':
                                    # Download icon to channel logo folder
                                    # GrabLogo(icon, chname)
                                
                            subtitle = elem.findtext("sub-title")
                            if not description:
                                if not subtitle:
                                    description = title  
                                else:
                                    description = subtitle
                                    
                            if not subtitle:                        
                                subtitle = 'LiveTV'

                            #Parse the category of the program
                            movie = False
                            category = 'Unknown'
                            categories = ''
                            categoryList = elem.findall("category")
                            
                            for cat in categoryList:
                                categories += ', ' + cat.text
                                if cat.text == 'Movie':
                                    movie = True
                                    category = cat.text
                                elif cat.text == 'Sports':
                                    category = cat.text
                                elif cat.text == 'Children':
                                    category = 'Kids'
                                elif cat.text == 'Kids':
                                    category = cat.text
                                elif cat.text == 'News':
                                    category = cat.text
                                elif cat.text == 'Comedy':
                                    category = cat.text
                                elif cat.text == 'Drama':
                                    category = cat.text
                            
                            #Trim prepended comma and space (considered storing all categories, but one is ok for now)
                            categories = categories[2:]
                            
                            #If the movie flag was set, it should override the rest (ex: comedy and movie sometimes come together)
                            if movie == True:
                                category = 'Movie'
                                type = 'movie'
                            else:
                                type = 'tvshow'
                                
                            #TVDB/TMDB Parsing    
                            #filter unwanted ids by title
                            if title == ('Paid Programming') or subtitle == ('Paid Programming') or description == ('Paid Programming'):
                                ignoreParse = True
                            else:
                                ignoreParse = False
                                
                            if setting3.lower() == 'ptvlguide':
                                stopDate = self.parseUTCXMLTVDate(elem.get('stop'))
                                startDate = self.parseUTCXMLTVDate(elem.get('start'))
                            else:
                                stopDate = self.parseXMLTVDate(elem.get('stop'), offset)
                                startDate = self.parseXMLTVDate(elem.get('start'), offset)
                            
                            #Enable Enhanced Parsing
                            if REAL_SETTINGS.getSetting('EnhancedGuideData') == 'true' and ignoreParse == False: 
                                if (((now > startDate and now <= stopDate) or (now < startDate))):
                                    if type == 'tvshow':                                      
                                        try:
                                            year = (title.split(' ('))[1].replace(')','')
                                            title = (title.split(' ('))[0]
                                        except:
                                            try:
                                                year = elem.findtext('date')[0:4]
                                            except:
                                                year = 0
                                                
                                        #Decipher the TVDB ID by using the Zap2it ID in dd_progid
                                        episodeNumList = elem.findall("episode-num")
                                        
                                        for epNum in episodeNumList:
                                            if epNum.attrib["system"] == 'dd_progid':
                                                dd_progid = epNum.text
                                        
                                        #The Zap2it ID is the first part of the string delimited by the dot
                                        #  Ex: <episode-num system="dd_progid">MV00044257.0000</episode-num>
                                        
                                        dd_progid = dd_progid.split('.',1)[0]
                                        tvdbid = self.getTVDBIDbyZap2it(dd_progid)
                                        
                                        year, id, category, rating, Managed, tagline = self.getEnhancedGuideData(title, year, tvdbid, genre, rating, type)                              
      
                                        # #Find Episode info by subtitle (ie Episode Name). 
                                        # if year != 0:
                                            # titleYR = title + ' (' + str(year) + ')'
                                        # else:   
                                            # titleYR = title
                                        # if subtitle != 'LiveTV':
                                            # episodeName, seasonNumber, episodeNumber = self.getTVINFObySubtitle(titleYR, subtitle)                                       
                                        # else:
                                            # #Find Episode info by air date.
                                            # if tvdbid != 0:
                                                # #Date element holds the original air date of the program
                                                # airdateStr = elem.findtext('date')
                                                # if airdateStr != None:
                                                    # self.log('buildLiveTVFileList, tvdbid by airdate')
                                                    # try:
                                                        # #Change date format into the byAirDate lookup format (YYYY-MM-DD)
                                                        # t = time.strptime(airdateStr, '%Y%m%d')
                                                        # airDateTime = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                                                        # airdate = airDateTime.strftime('%Y-%m-%d')
                                                        # #Only way to get a unique lookup is to use TVDB ID and the airdate of the episode
                                                        # episode = ET.fromstring(self.tvdbAPI.getEpisodeByAirdate(tvdbid, airdate))
                                                        # episode = episode.find("Episode")
                                                        # seasonNumber = episode.findtext("SeasonNumber")
                                                        # episodeNumber = episode.findtext("EpisodeNumber")
                                                        # episodeDesc = episode.findtext("Overview")
                                                        # episodeName = episode.findtext("EpisodeName")
                                                        # try:
                                                            # int(seasonNumber)
                                                            # int(episodeNumber)
                                                        # except:
                                                            # seasonNumber = 0
                                                            # episodeNumber = 0
                                                            # pass
                                                    # except Exception,e:
                                                        # pass

                                        # # Find Episode info by SeasonNum x EpisodeNum
                                        # if (seasonNumber != 0 and episodeNumber != 0):
                                            # episodeName, episodeDesc, episodeGenre = self.getTVINFObySE(titleYR, seasonNumber, episodeNumber)
                                        
                                        # if episodeName:
                                            # subtitle = episodeName

                                        # if episodeDesc:
                                            # description = episodeDesc                                              

                                        # if episodeGenre and category == 'Unknown':
                                            # category = episodeGenre
                                        
                                    else:#Movie
                                        
                                        try:
                                            year = (title.split(' ('))[1].replace(')','')
                                            title = (title.split(' ('))[0]
                                        except:
                                            #Date element holds the original air date of the program
                                            try:
                                                year = elem.findtext('date')[0:4]
                                            except:
                                                year = 0
                                                
                                        if subtitle == 'LiveTV':
                                            tagline = ''
                                            
                                        year, id, category, rating, Managed, subtitle = self.getEnhancedGuideData(title, year, imdbid, genre, rating, type, tagline)
                                        
                            if seasonNumber > 0:
                                seasonNumber = '%02d' % int(seasonNumber)
                            
                            if episodeNumber > 0:
                                episodeNumber = '%02d' % int(episodeNumber)
                                     
                            #Read the "new" boolean for this program
                            if elem.find("new") != None:
                                playcount = 0
                            else:
                                playcount = 1                        
                                
                            GenreLiveID = [category,type,id,thumburl,Managed,playcount,rating] 
                            genre, LiveID = self.packGenreLiveID(GenreLiveID) 
                            description = description.replace("\n", "").replace("\r", "")
                            subtitle = subtitle.replace("\n", "").replace("\r", "")
                            
                            try:
                                description = (self.trim(description, 350, '...'))
                            except Exception,e:
                                self.log("description Trim failed" + str(e))
                                description = (description[:350])
                                pass
                                
                            try:
                                subtitle = (self.trim(subtitle, 350, ''))
                            except Exception,e:
                                self.log("subtitle Trim failed" + str(e))
                                subtitle = (subtitle[:350])
                                pass
                            
                            #skip old shows that have already ended
                            if now > stopDate:
                                continue
                            
                            #adjust the duration of the current show
                            if now > startDate and now <= stopDate:
                                try:
                                    dur = ((stopDate - startDate).seconds)
                                except Exception,e:
                                    dur = 3600  #60 minute default
                                    
                            #use the full duration for an upcoming show
                            if now < startDate:
                                try:
                                    dur = (stopDate - startDate).seconds
                                except Exception,e:
                                    dur = 3600  #60 minute default
                                
                            if type == 'tvshow':
                                episodetitle = (('0' if seasonNumber < 10 else '') + str(seasonNumber) + 'x' + ('0' if episodeNumber < 10 else '') + str(episodeNumber) + ' - '+ (subtitle)).replace('  ',' ')

                                if str(episodetitle[0:5]) == '00x00':
                                    episodetitle = episodetitle.split("- ", 1)[-1]
                                    
                                tmpstr = str(dur) + ',' + title + "//" + episodetitle + "//" + description + "//" + genre + "//" + str(startDate) + "//" + LiveID + '\n' + setting2
                            
                            else: #Movie
                                tmpstr = str(dur) + ',' + title + "//" + subtitle + "//" + description + "//" + genre + "//" + str(startDate) + "//" + LiveID + '\n' + setting2
                        
                            tmpstr = tmpstr.replace("\\n", " ").replace("\\r", " ").replace("\\\"", "\"")
                            showList.append(tmpstr)
                            showcount += 1
                            
                            if showcount > limit:
                                break

                            if self.background == False:
                                self.updateDialog.update(self.updateDialogProgress, "Updating channel " + str(self.settingChannel), "adding LiveTV, parsing " + chname, "added " + str(showcount) + " entries")
                root.clear()                  
            f.close()                   
            if showcount == 0:
                self.log('Unable to find xmltv data for ' + setting1)
        except:
            self.log("fillLiveTV Failed!", xbmc.LOGERROR)
            buggalo.onExceptionRaised()
        return showList
        
    def fillLiveTVPVR(self, setting1, setting2, setting3, setting4, chname, limit):
        self.log("fillLiveTVPVR")
        showList = []
        showcount = 0
        json_query = ('{"jsonrpc":"2.0","method":"PVR.GetBroadcasts","params":{"channelid":%s,"properties":["title","plot","plotoutline","starttime","endtime","runtime","genre","episodename","episodenum","episodepart","firstaired","hastimer","parentalrating","thumbnail","rating"]}, "id": 1}' % setting1)
        json_folder_detail = self.sendJSON(json_query)
        detail = re.compile("{(.*?)}", re.DOTALL ).findall(json_folder_detail)
        now = self.parsePVRDate((str(datetime.datetime.utcnow())).split(".")[0])
        
        if self.background == False:
            self.updateDialog.update(self.updateDialogProgress, "Updating channel " + str(self.settingChannel), "adding LiveTV", 'parsing ' + chname)

        try:
            for f in detail:
                if self.threadPause() == False:
                    del showList[:]
                    return
                    
                titles = re.search('"title" *: *"(.*?)"', f)
                if titles:
                    title = titles.group(1)
                else:
                    try:
                        labels = re.search('"label" *: *"(.*?)"', f)
                        title = labels.group(1)
                    except:
                        title = None
                
                if title:
                    startDates = re.search('"starttime" *: *"(.*?)",', f)
                    stopDates = re.search('"endtime" *: *"(.*?)",', f)
                    subtitle = 'LiveTV'
                    Managed = False
                    id = 0
                    seasonNumber = 0
                    episodeNumber = 0
                    
                    if startDates:
                        startDate = self.parsePVRDate(startDates.group(1))
                        stopDate = self.parsePVRDate(stopDates.group(1))

                    if now > stopDate:
                        continue

                    runtimes = re.search('"runtime" *: *"(.*?)",', f)
                    #adjust the duration of the current show
                    if now > startDate and now <= stopDate:
                        print ' now > startDate'
                        if runtimes:
                            dur = int(runtimes.group(1)) * 60
                        else:
                            dur = int((stopDate - startDate).seconds)

                    #use the full duration for an upcoming show
                    if now < startDate:
                        print 'now < startDate'
                        if runtimes:
                            dur = int(runtimes.group(1)) * 60
                        else:
                            dur = ((stopDate - startDate).seconds)   
             
                    movie = False
                    genres = re.search('"genre" *: *"(.*?)",', f)
                    if genres:
                        genre = genres.group(1)
                        if genre.lower() == 'movie':
                            movie = True
                    else:
                        genre = 'Unknown'
                        
                    tvtypes = ['Episodic','Series','Sports','News','Paid Programming']
                    if dur >= 7200 and genre not in tvtypes:
                        movie = True
                        
                    if movie == True:
                        type = 'movie'
                    else:
                        type = 'tvshow'

                    try:
                        test = title.split(" *")[1]
                        title = title.split(" *")[0]
                        playcount = 0
                    except Exception,e:
                        playcount = 1
                        pass

                    plots = re.search('"plot" *: *"(.*?)"', f)
                    if plots:
                        description = plots.group(1)
                    else:
                        description = ''

                    ratings = re.search('"rating" *: *"(.*?)"', f)
                    if ratings:
                        rating = ratings.group(1)
                    else:
                        rating = 'NR'
                    
                    # if type == 'tvshow':
                        # episodenames = re.search('"episodename" *: *"(.*?)"', f)
                        # if episodename and len(episodenames) > 0:
                            # episodename = episodenames.group(1)
                        # else:
                            # episodename = ''
                        # episodenums = re.search('"episodenum" *: *"(.*?)"', f)
                        # if episodenums and len(episodenums) > 0:
                            # episodenum = episodenums.group(1) 
                        # else:
                            # episodenum = 0 
                        # episodeparts = re.search('"episodepart" *: *"(.*?)"', f)
                        # if episodeparts and len(episodeparts) > 0:
                            # episodepart = episodeparts.group(1)
                        # else:
                            # episodepart = 0 

                    #filter unwanted ids by title
                    if title == ('Paid Programming') or description == ('Paid Programming'):
                        ignoreParse = True
                    else:
                        ignoreParse = False
                                            
                    #Enable Enhanced Parsing
                    if REAL_SETTINGS.getSetting('EnhancedGuideData') == 'true' and ignoreParse == False: 
                        if (((now > startDate and now <= stopDate) or (now < startDate))):
                            year = 0
                            if type == 'tvshow': 
                                tvdbid = 0                                     
                                try:
                                    year = (title.split(' ('))[1].replace(')','')
                                    title = (title.split(' ('))[0]
                                except:
                                    try:
                                        year = elem.findtext('date')[0:4]
                                    except:
                                        year = 0

                                year, id, genre, rating, Managed, tagline = self.getEnhancedGuideData(title, year, tvdbid, genre, rating, type)                                            
                            else:#Movie
                                imdbid = 0
                                try:
                                    year = (title.split(' ('))[1].replace(')','')
                                    title = (title.split(' ('))[0]
                                except:
                                    #Date element holds the original air date of the program
                                    try:
                                        year = elem.findtext('date')[0:4]
                                    except:
                                        year = 0
                                        
                                if subtitle == 'LiveTV':
                                    tagline = ''
                                    
                                year, id, genre, rating, Managed, subtitle = self.getEnhancedGuideData(title, year, imdbid, genre, rating, type, tagline)                                            

                    if seasonNumber > 0:
                        seasonNumber = '%02d' % int(seasonNumber)
                    
                    if episodeNumber > 0:
                        episodeNumber = '%02d' % int(episodeNumber)
                             
                    try:
                        description = (self.trim(description, 350, '...'))
                    except Exception,e:
                        self.log("description Trim failed" + str(e))
                        description = (description[:350])
                        pass
                            
                    GenreLiveID = [genre,type,id,0,Managed,playcount,rating] 
                    genre, LiveID = self.packGenreLiveID(GenreLiveID) 
                   
                    if type == 'tvshow':
                        episodetitle = (('0' if seasonNumber < 10 else '') + str(seasonNumber) + 'x' + ('0' if episodeNumber < 10 else '') + str(episodeNumber) + ' - '+ (subtitle)).replace('  ',' ')

                        if str(episodetitle[0:5]) == '00x00':
                            episodetitle = episodetitle.split("- ", 1)[-1]
                            
                        tmpstr = str(dur) + ',' + title + "//" + episodetitle + "//" + description + "//" + genre + "//" + str(startDate) + "//" + LiveID + '\n' + setting2
                    
                    else: #Movie
                        tmpstr = str(dur) + ',' + title + "//" + subtitle + "//" + description + "//" + genre + "//" + str(startDate) + "//" + LiveID + '\n' + setting2
                
                    tmpstr = tmpstr.replace("\\n", " ").replace("\\r", " ").replace("\\\"", "\"")
                    showList.append(tmpstr)
                    showcount += 1
                    
                    if showcount > limit:
                        break

                    if self.background == False:
                        self.updateDialog.update(self.updateDialogProgress, "Updating channel " + str(self.settingChannel), "adding LiveTV, parsing " + chname, "added " + str(showcount))
        
            if showcount == 0:
                self.log('Unable to find pvr guidedata for ' + setting1)
        except Exception: 
            pass
        return showList

    def readXMLTV_NEW(self, filename):
        self.log('readXMLTV_NEW')
        if len(self.cached_readXMLTV) == 0:
            try:
                if filename[0:4] == 'http':
                    self.log("findZap2itID, filename http = " + filename)
                    f = open_url(filename)
                else:
                    self.log("findZap2itID, filename local = " + filename)
                    f = open(filename, "r")
                context = ET.iterparse(f, events=("start", "end"))
                context = iter(context)
                event, root = context.next()
                for event, elem in context:
                    if event == "end":
                        if elem.tag == "channel":
                            CHid = elem.get("id")
                            for title in elem.findall('display-name'):
                                channel = (title.text.replace('<display-name>','').replace('</display-name>','').replace('-DT','DT').replace(' DT','DT').replace('DT','').replace('-HD','HD').replace(' HD','HD').replace('HD','').replace('-SD','SD').replace(' SD','SD').replace('SD','').replace("'",'').replace(')',''))
                                channel = channel+' : '+CHid
                                self.cached_readXMLTV.append(channel)
                f.close()
                return self.cached_readXMLTV
            except Exception,e:
                self.log("readXMLTV, Failed! " + str(e))
                self.cached_readXMLTV = []
                channels = ['XMLTV ERROR : IMPROPER FORMATING']
                return channels
                    
    def findZap2itID(self, CHname, filename):
        if len(CHname) <= 1:
            CHname = 'Unknown'
        self.log("findZap2itID, CHname = " + CHname)
        show_busy_dialog()
        orgCHname = CHname
        CHname = CHname.upper()
        XMLTVMatchlst = []
        sorted_XMLTVMatchlst = []
        found = False
        # try:
        if filename == 'pvr':
            self.log("findZap2itID, pvr backend")             
            if not self.cached_json_detailed_xmltvChannels_pvr:
                self.log("findZap2itID, no cached_json_detailed_xmltvChannels")
                json_query = uni('{"jsonrpc":"2.0","method":"PVR.GetChannels","params":{"channelgroupid":2,"properties":["thumbnail"]},"id": 1 }')
                json_detail = self.sendJSON(json_query)
                self.cached_json_detailed_xmltvChannels_pvr = re.compile( "{(.*?)}", re.DOTALL ).findall(json_detail)
            file_detail = self.cached_json_detailed_xmltvChannels_pvr
            
            for f in file_detail:
                CHids = re.search('"channelid" *: *(.*?),', f)
                dnames = re.search('"label" *: *"(.*?)"', f)
                thumbs = re.search('"thumbnail" *: *"(.*?)"', f)
               
                if CHids and dnames:
                    CHid = CHids.group(1)
                    dname = dnames.group(1)       
                    CHname = CHname.replace('-DT','DT').replace(' DT','DT').replace('DT','').replace('-HD','HD').replace(' HD','HD').replace('HD','').replace('-SD','SD').replace(' SD','SD').replace('SD','')
                    matchLST = [CHname, 'W'+CHname, CHname+'HD', CHname+'DT', str(CHid)+' '+CHname, orgCHname.upper(), 'W'+orgCHname.upper(), orgCHname.upper()+'HD', orgCHname.upper()+'DT', str(CHid)+' '+orgCHname.upper(), orgCHname]
                    dnameID = dname + ' : ' + CHid
                    self.logDebug("findZap2itID, dnameID = " + dnameID)
                    XMLTVMatchlst.append(dnameID)
        else:
            XMLTVMatchlst = self.readXMLTV(filename)
            
            try:
                CHnum = CHname.split(' ')[0]
                CHname = CHname.split(' ')[1]
            except:
                CHnum = 0
                pass
            
            CHname = CHname.replace('-DT','DT').replace(' DT','DT').replace('DT','').replace('-HD','HD').replace(' HD','HD').replace('HD','').replace('-SD','SD').replace(' SD','SD').replace('SD','')
            matchLST = [CHname, 'W'+CHname, CHname+'HD', CHname+'DT', str(CHnum)+' '+CHname, orgCHname.upper(), 'W'+orgCHname.upper(), orgCHname.upper()+'HD', orgCHname.upper()+'DT', str(CHnum)+' '+orgCHname.upper(), orgCHname]
            self.logDebug("findZap2itID, Cleaned CHname = " + CHname)
            
        sorted_XMLTVMatchlst = sorted_nicely(XMLTVMatchlst)
        self.logDebug("findZap2itID, sorted_XMLTVMatchlst = " + str(sorted_XMLTVMatchlst))

        for n in range(len(sorted_XMLTVMatchlst)):
            CHid = '0'
            found = False
            dnameID = sorted_XMLTVMatchlst[n]
            dname = dnameID.split(' : ')[0]
            CHid = dnameID.split(' : ')[1]

            if dname.upper() in matchLST: 
                found = True
                hide_busy_dialog()
                return orgCHname, CHid
                    
        if not found:
            hide_busy_dialog()
            XMLTVMatchlst = []

            for s in range(len(sorted_XMLTVMatchlst)):
                dnameID = sorted_XMLTVMatchlst[s]
                dname = dnameID.split(' : ')[0]
                CHid = dnameID.split(' : ')[1]
                                
                try:
                    CHid = CHid.split(', icon')[0]
                except:
                    pass
                    
                line = dname + ' : ' + CHid 
                if dname[0:3] != 'en': 
                    XMLTVMatchlst.append(line)
                    
            select = selectDialog(XMLTVMatchlst, 'Select matching id to [B]%s[/B]' % orgCHname, 30000)
            dnameID = XMLTVMatchlst[select]
            CHid = dnameID.split(' : ')[1]
            dnameID = dnameID.split(' : ')[0]
            return dnameID, CHid
        # except Exception,e:
            # self.log("findZap2itID, Failed! " + str(e))
            
    def fillPVR(self):
        self.log('fillPVR')
        show_busy_dialog()
        json_query = uni('{"jsonrpc":"2.0","method":"PVR.GetChannels","params":{"channelgroupid":2,"properties":["thumbnail"]},"id": 1 }')
        json_detail = self.sendJSON(json_query)
        file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_detail)
        TMPPVRList = []
        PVRNameList = []
        PVRPathList = []
        self.cached_json_detailed_xmltvChannels_pvr = [] 
        
        #PVR Path by XBMC Version, no json paths?
        XBMCver = self.XBMCversion()
        if XBMCver < 14:
            PVRverPath = "pvr://channels/tv/All TV channels/"
        else:
            PVRverPath = "pvr://channels/tv/All channels/"          
        try:         
            for f in file_detail:
                CHid = 0
                CHname = ''
                thumb = ''
                CHids = re.search('"channelid" *: *(.*?),', f)
                CHnames = re.search('"label" *: *"(.*?)"', f)
                thumbs = re.search('"thumbnail" *: *"(.*?)"', f)
                
                if CHids and CHnames:
                    CHid = int(CHids.group(1))
                    CHname = CHnames.group(1)
                    
                    #Download icon to channel logo folder
                    if thumbs and REAL_SETTINGS.getSetting('EnhancedGuideData') == 'true':
                        thumb = thumbs.group(1)
                        GrabLogo(thumb, CHname + ' PVR')
                                               
                    name = '[COLOR=blue][B]'+str(CHid)+'[/B][/COLOR] - ' + CHname
                    path = PVRverPath + str(CHid - 1) + ".pvr"
                    TMPPVRList.append(name+'@#@'+path)  

            SortedPVRList = sorted_nicely(TMPPVRList)
            for i in range(len(SortedPVRList)):  
                PVRNameList.append((SortedPVRList[i]).split('@#@')[0])  
                PVRPathList.append((SortedPVRList[i]).split('@#@')[1])          
        except Exception,e:
            self.log("fillPVR, Failed! " + str(e))

        if len(TMPPVRList) == 0:
            PVRNameList = ['Kodi PVR is empty or unavailable!']
        hide_busy_dialog() 
        return PVRNameList, PVRPathList

    def fillHDHR(self):
        self.log("fillHDHR")
        show_busy_dialog()
        Chanlist = []
        HDHRNameList = ['']
        HDHRPathList  = ['']
        list = ''
        try:
            devices = hdhr.discover()
            for i in range(len(devices)):
                url = (str(devices[i]).split(':url=')[1]).replace('>','')
                try:
                    list = list + urlopen(url).read()
                except:
                    pass
            file_detail = re.compile( "{(.*?)}", re.DOTALL ).findall(list)
            
            for f in file_detail:
                match = ''
                link = ''
                chnum = 0
                fav = False
                drm = False
                tmp = ''
                match = re.search('"GuideName" *: *"(.*?)",', f)    
                if match != None and len(match.group(1)) > 0:
                    chname = match.group(1)
                    links = re.search('"URL" *: *"(.*?)"', f)
                    chnums = re.search('"GuideNumber" *: *"([\d.]*\d+)"', f)
                    favs = re.search('"Favorite" *: *([\d.]*\d+)', f)
                    drms = re.search('"DRM" *: *([\d.]*\d+)', f)

                    if links != None and len(links.group(1)) > 0:
                        link = links.group(1)

                    if chnums != None and len(chnums.group(1)) > 0:
                        chnum = chnums.group(1)

                    if favs != None and len(favs.group(1)) > 0:
                        fav = bool(favs.group(1))
                        
                    if drms != None and len(drms.group(1)) > 0:
                        drm = bool(drms.group(1))

                    if fav:
                        chname = chname+'[COLOR=gold] [Favorite][/COLOR]'                    
                    if drm:
                        chname = chname+'[COLOR=red] [DRM][/COLOR]'
                                           
                    chname = '[COLOR=blue][B]'+chnum+'[/B][/COLOR] - ' + chname
                    tmp = chname + '@#@' + link
                    Chanlist.append(tmp)
            SortChanlist = sorted_nicely(Chanlist)
            
            for n in range(len(SortChanlist)):
                if SortChanlist[n] != None:
                    HDHRNameList.append((SortChanlist[n]).split('@#@')[0])   
                    HDHRPathList.append((SortChanlist[n]).split('@#@')[1])
        except Exception,e:
            self.log("fillHDHR, Failed! " + str(e))

        if len(Chanlist) == 0:
            HDHRNameList = ['HDHR ERROR: Unable to find device or favorite channels']
        hide_busy_dialog() 
        return removeStringElem(HDHRNameList), removeStringElem(HDHRPathList)
        
    def parsePVRDate(self, dateString):
            if dateString is not None:
                t = time.strptime(dateString, '%Y-%m-%d %H:%M:%S')
                tmpDate = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                timestamp = calendar.timegm(tmpDate.timetuple())
                local_dt = datetime.datetime.fromtimestamp(timestamp)
                assert tmpDate.resolution >= timedelta(microseconds=1)
                return local_dt.replace(microsecond=tmpDate.microsecond) 
            else:
                return None
       
    def parseUTCXMLTVDate(self, dateString):
        if dateString is not None:
            if dateString.find(' ') != -1:
                # remove timezone information
                dateString = dateString[:dateString.find(' ')]
            t = time.strptime(dateString, '%Y%m%d%H%M%S')
            tmpDate = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            timestamp = calendar.timegm(tmpDate.timetuple())
            local_dt = datetime.datetime.fromtimestamp(timestamp)
            assert tmpDate.resolution >= timedelta(microseconds=1)
            return local_dt.replace(microsecond=tmpDate.microsecond) 
        else:
            return None
       
    def parseXMLTVDate(self, dateString, offset=0):
        if dateString is not None:
            if dateString.find(' ') != -1:
                # remove timezone information
                dateString = dateString[:dateString.find(' ')]
            t = time.strptime(dateString, '%Y%m%d%H%M%S')
            d = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
            d += datetime.timedelta(hours = offset)
            return d
        else:
            return None
