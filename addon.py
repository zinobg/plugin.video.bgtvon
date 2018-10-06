# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 zinobg@gmail.com
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

import urllib2, urllib, re, os, datetime
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import weblogin

__settings__ = xbmcaddon.Addon()
_thisPlugin = int(sys.argv[1])
_pluginName = (sys.argv[0])
username = __settings__.getSetting('username')
password = __settings__.getSetting('password')
header_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
BASE="http://www.bgtv-on.com/"
subscribe_url=BASE+'subscribe'
recording_url=BASE+'recording'

def check_validity(account_active):
    subscribe_source=weblogin.doLogin('',username,password)
    subscribe_source=weblogin.openUrl(subscribe_url)
    match=re.compile('<p><span.*>(.+?)<\/span><\/p>').findall(subscribe_source)
    for subs_text in match:
        account_active='1'
        dates_match=re.compile('.* (.+?)-(.+?)-(.+?)\.').findall(subs_text)
        for s_day,s_month,s_year in dates_match:
            date_expire=datetime.datetime(int(s_year),int(s_month),int(s_day))
            date_today=datetime.datetime.now()
            days_delta=date_expire-date_today
            xbmc.log("Account is active! You have "+str(days_delta.days)+" days until it expires")
            if(days_delta.days <= 5):
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]', 'Only '+str(days_delta.days)+' days left!',xbmcgui.NOTIFICATION_INFO,8000,sound=False)
	    return account_active

def LIST_CHANNELS():
    account_active='0'
    account_active=check_validity(account_active)
    source=weblogin.openUrl(BASE)
    if(account_active == '1'):
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    elif(account_active == '0'):
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch only free TVs.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=re.compile(match_pattern).findall(source)
    for cid,ch_image,ch_current in match:
        ch_image = (BASE + ch_image)
        addDir(ch_current,cid,20,ch_image)

def INDEX_CHANNELS(cid):
    url=(BASE+"teko/getchaclap_mbr.php?cid="+cid)
    source_ch=weblogin.doLogin('',username,password)
    source_ch=weblogin.openUrl(url)
    n=source_ch.count('m3u8')
    item_plus=',"(.+?)"'
    search_string='\["(.+?)"'
    end_string='\]'
    while n > 1:
        search_string=search_string+item_plus
        n -=1
    search_string=search_string+end_string
    match=re.compile(search_string).findall(source_ch)
    xbmc.log('match='+str(match))
    if(source_ch.count('m3u8') > 1):
        match=match[0]
        i = 0
        for i in range(len(match)):
            match_what_to_play=re.compile('liveedge\/(.+?).stream').findall(match[i])
            for what_to_play in match_what_to_play:
                addLink('PLAY: '+what_to_play,match[i],'')
    elif(source_ch.count('m3u8') == 1):
        match=match[0]
        match_what_to_play=re.compile('liveedge\/(.+?).stream').findall(match)
        if not match_what_to_play:
            addLink('PLAY: '+match,match,'')
        for what_to_play in match_what_to_play:
            addLink('PLAY: '+what_to_play,match,'')

def LIST_REC():
    req=urllib2.Request(recording_url)
    req.add_header('User-Agent',header_string)
    response=urllib2.urlopen(req)
    source=response.read()
    response.close()
    match_rec=re.compile('<a href=recording(.+?).class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match_rec:
        rec_url=(recording_url+cid)
        addDir(name,rec_url,51,'')

def LIST_REC_CHAN(cid):
    req=urllib2.Request(cid)
    req.add_header('User-Agent',header_string)
    response=urllib2.urlopen(req)
    source=response.read()
    response.close()
    match_rec=re.compile('(<div class=\"day\">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span><div class="clear"><\/div><\/li><\/a>)').findall(source)
    for temp1,day,temp2,rec_url,time,name in match_rec:
        del temp1,temp2
        if(day):
            day_previous=day
        else:
            day=day_previous
        name=('['+day+'] '+'('+time+') '+name)
        addDir(name,rec_url,52,'')
        
def PLAY_REC_CHAN(cid,name):
    url=(BASE+cid)
    account_active='0'
    account_active=check_validity(account_active)
    if(account_active == '0'):
        xbmcgui.Dialog().notification('[ You don\'t have valide subscription ]', 'Not Available without subscribtion!',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        sys.exit("Subscribtion problem")
    source_rec=weblogin.openUrl(url)
    match_rec=re.compile('source:."(.+?)"').findall(source_rec)
    for rec_url in match_rec:
        addLink('PLAY: '+name,rec_url,'')
	
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
    liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video",infoLabels={ "Title": name })
    liz.setProperty('IsPlayable','true')
    ok=xbmcplugin.addDirectoryItem(handle=_thisPlugin,url=url,listitem=liz)
    return ok

def addDir(name,cid,mode,iconimage):
    u=_pluginName+"?cid="+urllib.quote_plus(cid)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=_thisPlugin,url=u,listitem=liz,isFolder=True)
    return ok

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
    dialog=xbmcgui.Dialog()
    ret=dialog.select('',['НА ЖИВО','НА ЗАПИС'])
    if(ret==0):
        xbmc.log('Starting live tv')
        LIST_CHANNELS()
    elif(ret==1):
        xbmc.log('Starting recordings')
        LIST_REC()

elif mode==20:
    INDEX_CHANNELS(cid)

elif mode==50:
    LIST_REC()

elif mode==51:
    LIST_REC_CHAN(cid)

elif mode==52:
    PLAY_REC_CHAN(cid,name)

xbmcplugin.endOfDirectory(_thisPlugin)
