import urllib2, urllib, re, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import weblogin

__settings__ = xbmcaddon.Addon()
## Not needed for this addon. 
#__icon__ = __settings__.getAddonInfo('icon')
#__fanart__ = __settings__.getAddonInfo('fanart')
#__language__ = __settings__.getLocalizedString
_thisPlugin = int(sys.argv[1])
_pluginName = (sys.argv[0])
username = __settings__.getSetting('username')
password = __settings__.getSetting('password')

###
### Uncomment if you would like channel icons to be re-downloaded each time you start the addon 
###
#from sqlite3 import dbapi2 as sqlite
#DB = os.path.join(xbmc.translatePath("special://userdata/Database"), 'Textures13.db')
#db = sqlite.connect(DB)
#db.execute('Delete FROM texture WHERE url LIKE "%bgtv-on%"')
#db.commit()
#db.close()

BASE = "http://www.bgtv-on.com/"
subscribe_url = "http://bgtv-on.com/subscribe"

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
        addDir(ch_current,cid,1,ch_image)

def INDEX_CHANNELS(cid):
    url = (str(BASE) + "teko/getchaclap_mbr.php?cid=" + str(cid))
    source_ch=weblogin.doLogin('',username,password,url)
    n = source_ch.count('m3u8')
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
    LIST_CHANNELS()

elif mode==1:
    INDEX_CHANNELS(cid)

xbmcplugin.endOfDirectory(_thisPlugin)