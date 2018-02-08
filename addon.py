# -*- coding: utf-8 -*-
import urllib2, urllib, re, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import weblogin

__settings__ = xbmcaddon.Addon()
_thisPlugin = int(sys.argv[1])
_pluginName = (sys.argv[0])
username = __settings__.getSetting('username')
password = __settings__.getSetting('password')

BASE="http://www.bgtv-on.com/"
subscribe_url="http://bgtv-on.com/subscribe"
recording_url="http://bgtv-on.com/recording"

def MAIN_MENU():
    addDir('НА ЖИВО','none',10,'')
    addDir('НА ЗАПИС','none',50,'')	

def LIST_CHANNELS():
    # Check if account is active
    account_active='0'
    subscribe_source=weblogin.doLogin('',username,password,subscribe_url)
    match=re.compile('<p><span.*>(.+?)<\/span><\/p>').findall(subscribe_source)
    for subs_text in match:
        account_active='1'
        xbmc.log("Account is active: "+subs_text)
    # End of check
    source=weblogin.doLogin('',username,password,BASE)
    if(account_active == '1'):
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    elif(account_active == '0'):
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available', xbmcgui.NOTIFICATION_WARNING, 8000, sound=False)
        xbmc.log("You don't have a valide account, so you are going to watch only free TVs.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=re.compile(match_pattern).findall(source)
    for cid,ch_image,ch_current in match:
        ch_image = (BASE + ch_image)
        addDir(ch_current,cid,20,ch_image)

def INDEX_CHANNELS(cid):
    url=(BASE+"teko/getchaclap_mbr.php?cid="+cid)
    source_ch=weblogin.doLogin('',username,password,url)
    n=source_ch.count('m3u8')
    item_plus=',"(.+?)"'
    search_string='\["(.+?)"'
    end_string='\]'
    while n > 1:
        search_string=search_string+item_plus
        n -=1
    search_string=search_string+end_string
    match=re.compile(search_string).findall(source_ch)
    xbmc.log(str(match))
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
        for what_to_play in match_what_to_play:
            addLink('PLAY: '+what_to_play,match,'')

def LIST_REC():
    req=urllib2.Request(recording_url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response=urllib2.urlopen(req)
    source=response.read()
    response.close()
    match_rec=re.compile('<a href=recording(.+?).class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match_rec:
        rec_url=(recording_url+cid)
        addDir(name,rec_url,51,'')

def LIST_REC_CHAN(cid):
    req=urllib2.Request(cid)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
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
    source_rec=weblogin.doLogin('',username,password,url)
    match_rec=re.compile('source:."(.+?)"').findall(source_rec)
    if not match_rec:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available', xbmcgui.NOTIFICATION_ERROR, 8000, sound=True)
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
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('IsPlayable','true')
    ok=xbmcplugin.addDirectoryItem(handle=_thisPlugin,url=url,listitem=liz)
    return ok

def addDir(name,cid,mode,iconimage):
    u=_pluginName+"?cid="+urllib.quote_plus(cid)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
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
    MAIN_MENU()

elif mode==10:
    LIST_CHANNELS()

elif mode==20:
    INDEX_CHANNELS(cid)

elif mode==50:
    LIST_REC()

elif mode==51:
    LIST_REC_CHAN(cid)

elif mode==52:
    PLAY_REC_CHAN(cid,name)

xbmcplugin.endOfDirectory(_thisPlugin)
