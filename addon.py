# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 zinobg [at] gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from re import compile as Compile
import urllib,datetime,json
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
import weblogin
#import threading


'''
fill in the credentials
'''
if not xbmcaddon.Addon().getSetting('username') or not xbmcaddon.Addon().getSetting('password') or not xbmcaddon.Addon():
    xbmcaddon.Addon().openSettings()
'''
icons
'''
vid_icon=xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+"/resources/png/vid_icon.png")
prog_icon=xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+"/resources/png/prog_icon.png")
'''
settings
'''
username=xbmcaddon.Addon().getSetting('username')
password=xbmcaddon.Addon().getSetting('password')
quality=xbmcaddon.Addon().getSetting('quality')
timezone=xbmcaddon.Addon().getSetting('index_tz')
hide_babytv=xbmcaddon.Addon().getSetting('hide_babytv')
'''
web links
'''
BASE="http://www.bgtv-on.com/"
subscribe_url=BASE+'subscribe'
recording_url=BASE+'recording'
programme_url=BASE+'programme'
'''
time convert based on TZ in conf
'''
def time_convert(time_orig):
    h,m=time_orig.split(':')
    time_orig=datetime.time(int(h),int(m))
    time_diff=abs(int(timezone)-13)
    if int(timezone)>13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)+datetime.timedelta(hours=time_diff)).time()
    elif int(timezone)<13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)-datetime.timedelta(hours=time_diff)).time()
    h,m,s=str(hol).split(':')
    time_modified=h+':'+m
    return time_modified
'''
returns True if the account has a valid subscription
'''
def check_validity(account_active=False):
    cookiepath=weblogin.doLogin(username,password)
    subscribe_source=weblogin.openUrl(subscribe_url,cookiepath)
    match=Compile('<p><span.*>(.+?)<\/span><\/p>').findall(subscribe_source)
    for subs_text in match:
        account_active=True
        dates_match=Compile('.* (.+?)-(.+?)-(.+?)\.').findall(subs_text)
        for s_day,s_month,s_year in dates_match:
            date_expire=datetime.datetime(int(s_year),int(s_month),int(s_day))
            date_today=datetime.datetime.now()
            days_delta=date_expire-date_today
            xbmc.log("Account is active! You have "+str(days_delta.days)+" days until it expires")
            if days_delta.days <= 5:
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]','Only '+str(days_delta.days)+' days left!',xbmcgui.NOTIFICATION_INFO,10000,sound=False)
    return (account_active,cookiepath)
'''
function that returns a tupple: title to show and stripped stream link
'''
def correct_stream_url(raw_stream):
    stream=raw_stream.lstrip('[').rstrip(']').strip('"')
    titles=Compile('\/(.+?).stream').findall(stream)
    if not titles:
        titles = Compile('\/(.+?).smil').findall(stream)
    for title in titles:
        title="["+title.replace('_','] [').upper()+"]"
        return (title,stream)
'''
Live TV functions
'''
def LIST_CHANNELS():
    account_active=check_validity()
    source=weblogin.openUrl(BASE,account_active[1])
    if account_active[0]:
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    else:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available',xbmcgui.NOTIFICATION_WARNING,10000,sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=Compile(match_pattern).findall(source)
    for cid,ch_image,ch_current in match:
        '''
        Here I hide babytv 
        '''
        if cid=='47' and hide_babytv=='true':
            continue
        '''
        '''
        ch_image = (BASE + ch_image)
        addDir(ch_current,cid,21,ch_image)
'''
'''
def INDEX_CHANNELS(cid):
    url=(BASE+"teko/getchaclap_mbr.php?cid="+cid)
    cookiepath=weblogin.doLogin(username,password)
    source=weblogin.openUrl(url,cookiepath)
    src_list=list(source.split(","))
    if quality=='moderate':
        for i in range(len(src_list)):
            play_list=correct_stream_url(src_list[i])
            addLink('PLAY: '+play_list[0],play_list[1],vid_icon)
    else:
        '''
        Presuming that the first stream has the lowest quality and the last - the highest
         0 : getting the first stream link
        -1 : getting the last stream link
        '''
        if quality=='low' or len(src_list)==1:
            element=0
        if quality=='high' and len(src_list)>1:
            element=-1
        xbmc.log('2-quality: '+quality+' and nuber of streams: '+str(len(src_list)))
        play_list=correct_stream_url(src_list[element])
        #xbmc.log(play_list)
        '''
        loading json clap conf
        '''
        source_clap=weblogin.openUrl(BASE+'teko/onairclap.php',cookiepath)
        clap_json_config=json.loads(source_clap)
        for i in range(len(clap_json_config)):
            if clap_json_config[i]['cid']==cid:
                text1=clap_json_config[i]['chName']
                text2=clap_json_config[i]['name']
                icon=clap_json_config[i]['logo']
        '''
        playing the stream
        '''
        liz=xbmcgui.ListItem(play_list[0])
        liz.setInfo(type="Video",infoLabels={"Title":play_list[0]})
        liz.setProperty('IsPlayable','true')
        xbmc.Player().play(item=play_list[1],listitem=liz,windowed=False,startpos=-1)
        xbmcgui.Dialog().notification(text1,text2,icon,10000,sound=False)
        return xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=False)
'''
'''
def LIST_REC():
    cookiepath = weblogin.doLogin(username,password)
    source=weblogin.openUrl(recording_url,cookiepath)
    match=Compile('<a href=recording(.+?)#..class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match:
        rec_url=(recording_url+cid)
        addDir(name,rec_url,31,vid_icon)
'''
Recorded channels
'''
def LIST_REC_CHAN(url):
    cookiepath = weblogin.doLogin(username, password)
    source=weblogin.openUrl(url,cookiepath)
    match=Compile('(<div class="day">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,rec_url,time,name in match:
        del temp1,temp2
        if day is not '':
            addLink('=['+day+']=','','')
        time_convd=time_convert(time)
        desc_txt=('['+time_convd+'] '+name)
        addDir(desc_txt,rec_url.strip('"'),32,vid_icon)
'''
'''
def PLAY_REC_CHAN(cid,name):
    url=(BASE+cid)
    account_active=check_validity()
    if not account_active[0]:
        xbmcgui.Dialog().notification('[ You don\'t have valid subscription ]', 'Not Available without subscription!',xbmcgui.NOTIFICATION_WARNING,10000,sound=True)
        raise SystemExit
    source_rec=weblogin.openUrl(url,account_active[1])
    match_rec=Compile('source:."(.+?)"').findall(source_rec)
    for rec_url in match_rec:
        addLink('PLAY: '+name,rec_url,vid_icon)
'''
TV schedule
'''
def INDEX_PROG_CH():
    cookiepath = weblogin.doLogin(username, password)
    source=weblogin.openUrl(programme_url,cookiepath)
    match=Compile('<a href=programme\?cid=(.+?)#..class=tab >(.+?)<\/a>').findall(source)
    for cid,name in match:
        addDir(name,cid,41,prog_icon)    
'''
'''
def LIST_PROG_CH(cid):
    url=programme_url+'?cid='+cid
    cookiepath = weblogin.doLogin(username, password)
    source=weblogin.openUrl(url,cookiepath)
    match=Compile('(<div class="day">(.+?)<\/div>)*(<li style="list-style: none;"><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,time,name in match:
        del temp1,temp2
        if day is not '':
            addDir('=['+day+']=',cid,42,prog_icon)
        time_convd=time_convert(time)
        desc_txt=('['+time_convd+'] '+name)
        addDir(desc_txt,cid,42,prog_icon)
'''
dictionaly of parameters
'''
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

'''
defining xbmcplugin lists
'''
def addLink(name,url,iconimage):
    liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video",infoLabels={ "Title": name })
    liz.setProperty('IsPlayable','true')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok
def addDir(name,cid,mode,iconimage):
    u=sys.argv[0]+"?cid="+urllib.quote_plus(cid)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
'''
'''
params=get_params()
cid=None
name=None
mode=None

try:
    cid=urllib.unquote_plus(params["cid"])
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

xbmc.log("Mode: "+str(mode))
xbmc.log("CID: "+str(cid))
xbmc.log("Name: "+str(name))

if mode==None or cid==None or len(cid)<1:
    try:
        '''
        it is supported only in newer versions of kodi
        '''
        menu_index=xbmcgui.Dialog().contextmenu(['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    except:
        menu_index=xbmcgui.Dialog().select('',['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    if(menu_index==0):
        xbmc.log('Selected from menu: onair')
        LIST_CHANNELS()
    elif(menu_index==1):
        xbmc.log('Selected from menu: recording')
        LIST_REC()
    elif(menu_index==2):
        xbmc.log('Selected from menu: programme')
        INDEX_PROG_CH()

elif mode==21:
    INDEX_CHANNELS(cid)
elif mode==31:
    LIST_REC_CHAN(cid)
elif mode==32:
    PLAY_REC_CHAN(cid,name)
elif mode==41:
    LIST_PROG_CH(cid)
elif mode==42:
    INDEX_CHANNELS(cid)


#xbmc.executebuiltin('Container.Refresh')
#xbmc.log(sys.argv[0]+"?mode="+str(21))
#guiUpdateTimer = threading.Timer(5.0,xbmc.executebuiltin('Container.Refresh(sys.argv[0]+"?mode="+str(21))'))
#guiUpdateTimer.start()
xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=True)
'''
def populateList(self):
    for oneContent in myContents:
        li = xbmcgui.ListItem(oneContent["name"])
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=oneContent["url"], listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    guiUpdateTimer = threading.Timer(
        4.0, # fire after  4 seconds
        self.refreshGuiItems)
    guiUpdateTimer.start()

def refreshGuiItems(self):
    xbmc.executebuiltin('Container.Refresh')
'''
