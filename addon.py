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

import urllib2, urllib, re, os, datetime, time
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import weblogin

# Base variables
__addon_id__='plugin.video.bgtvon'
__Addon=xbmcaddon.Addon(__addon_id__)
__settings__=xbmcaddon.Addon(id=__addon_id__)
_thisPlugin=int(sys.argv[1])
_pluginName=(sys.argv[0])
# Icon variables
recicon=xbmc.translatePath(__Addon.getAddonInfo('path')+"/resources/png/recicon.png")
tvchannel=xbmc.translatePath(__Addon.getAddonInfo('path')+"/resources/png/tvchannel.png")
tvchannelhd=xbmc.translatePath(__Addon.getAddonInfo('path')+"/resources/png/tvchannelhd.png")
programme=xbmc.translatePath(__Addon.getAddonInfo('path')+"/resources/png/programme.png")
dot=xbmc.translatePath(__Addon.getAddonInfo('path')+"/resources/png/dot.png")
# Settings variables
username=__settings__.getSetting('username')
password=__settings__.getSetting('password')
timezone=__settings__.getSetting('index_tz')
# Web links variables
BASE="http://www.bgtv-on.com/"
subscribe_url=BASE+'subscribe'
recording_url=BASE+'recording'
programme_url=BASE+'programme'
onair_url=BASE+'onair'

if not username or not password or not __settings__:
    xbmcaddon.Addon().openSettings()

def time_convert(time_orig):
    h,m=time_orig.split(':')
    time_orig=datetime.time(int(h),int(m))
    time_diff=abs(int(timezone)-13)
    if int(timezone)>13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)+datetime.timedelta(hours=time_diff)).time()
    elif int(timezone)<13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)-datetime.timedelta(hours=time_diff)).time()
    h,m,s=str(hol).split(':')
    time_mod=h+':'+m
    return time_mod

def check_validity(account_active):
    subscribe_source=weblogin.doLogin('',username,password)
    subscribe_source=weblogin.openUrl(subscribe_url)
    match=re.compile('<p><span.*>(.+?)<\/span><\/p>').findall(subscribe_source)
    for subs_text in match:
        account_active=True
        dates_match=re.compile('.* (.+?)-(.+?)-(.+?)\.').findall(subs_text)
        for s_day,s_month,s_year in dates_match:
            date_expire=datetime.datetime(int(s_year),int(s_month),int(s_day))
            date_today=datetime.datetime.now()
            days_delta=date_expire-date_today
            xbmc.log("Account is active! You have "+str(days_delta.days)+" days until it expires")
            if days_delta.days <= 5:
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]', 'Only '+str(days_delta.days)+' days left!',xbmcgui.NOTIFICATION_INFO,8000,sound=False)
    return account_active

def tvi(name):
    if "high" in name:
        return tvchannelhd
    else:
        return tvchannel

def source_list(src):
    src_list=src.split(',')
    for i in range(len(src_list)):
        src_list[i]=src_list[i].lstrip('[').rstrip(']').strip('"')
    return src_list
    
def LIST_CHANNELS():
    account_active=False
    account_active=check_validity(account_active)
    source=weblogin.openUrl(BASE)
    if account_active == True:
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    elif account_active == False:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=re.compile(match_pattern).findall(source)
    for cid,ch_image,ch_current in match:
        ch_image = (BASE + ch_image)
        addDir(ch_current,cid,20,ch_image)

def INDEX_CHANNELS(cid):
    url=(BASE+"teko/getchaclap_mbr.php?cid="+cid)
    source_ch=weblogin.doLogin('',username,password)
    source_ch=weblogin.openUrl(url)
    src_lst=source_list(source_ch)
    for play_lst in src_lst:
        title_lst=re.compile('liveedge\/(.+?).stream').findall(play_lst)
        for title_ply in title_lst:
            try:
                tvicon=tvi(title_ply)
                title_ply="["+title_ply.replace('_','] [').upper()+"]"
                addLink('PLAY: '+title_ply,play_lst,tvicon)
            except:
                continue
                
def LIST_REC():
    source=weblogin.openUrl(recording_url)
    match_rec=re.compile('<a href=recording(.+?)#t.class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match_rec:
        rec_url=(recording_url+cid)
        addDir(name,rec_url,51,recicon)

def LIST_REC_CHAN(url):
    source=weblogin.openUrl(url)
    match_rec=re.compile('(<div class="day">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,rec_url,time,name in match_rec:
        del temp1,temp2
        if day is not '':
            addLink('=['+day+']=','','')
        time_convd=time_convert(time)
        desc_txt=('['+time_convd+'] '+name)
        addDir(desc_txt,rec_url,52,recicon)
        
def PLAY_REC_CHAN(cid,name):
    url=(BASE+cid)
    account_active=False
    account_active=check_validity(account_active)
    if account_active == False:
        xbmcgui.Dialog().notification('[ You don\'t have valid subscription ]', 'Not Available without subscribtion!',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        sys.exit("Subscribtion problem")
    source_rec=weblogin.openUrl(url)
    match_rec=re.compile('source:."(.+?)"').findall(source_rec)
    for rec_url in match_rec:
        addLink('PLAY: '+name,rec_url,dot)

def INDEX_PROG_CH():
    source=weblogin.openUrl(programme_url)
    match_prog=re.compile('<a href=programme\?cid=(.+?)#t.class=tab >(.+?)<\/a>').findall(source)
    for cid,name in match_prog:
        addDir(name,cid,71,programme)    

def LIST_PROG_CH(cid,name):
    url=programme_url+'?cid='+cid
    source=weblogin.openUrl(url)
    match_prog=re.compile('(<div class="day">(.+?)<\/div>)*(<li style="list-style: none;"><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,time,name in match_prog:
        del temp1,temp2
        if day is not '':
            addDir('=['+day+']=',cid,72,dot)
        time_convd=time_convert(time)
        desc_txt=('['+time_convd+'] '+name)
        addDir(desc_txt,cid,72,dot)

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

# defining xbmc functions
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
#

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
    menu=dialog.select('',['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    if(menu==0):
        xbmc.log('Selected from menu: onair')
        LIST_CHANNELS()
    elif(menu==1):
        xbmc.log('Selected from menu: recording')
        LIST_REC()
    elif(menu==2):
        xbmc.log('Selected from menu: programme')
        INDEX_PROG_CH()

elif mode==20:
    INDEX_CHANNELS(cid)

elif mode==50:
    LIST_REC()

elif mode==51:
    LIST_REC_CHAN(cid)

elif mode==52:
    PLAY_REC_CHAN(cid,name)

elif mode==71:
    LIST_PROG_CH(cid,name)

elif mode==72:
    INDEX_CHANNELS(cid)

xbmcplugin.endOfDirectory(_thisPlugin)
