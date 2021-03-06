# -*- coding: utf-8 -*-

# import urllib
import urllib2
import datetime
import json
import re
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from cookielib import LWPCookieJar
# import threading


class LoginAuth(object):
    def __init__(self, user, passwd):
        self.username = user
        self.password = passwd
        self.isActive = False
        cookie_file = 'cookies_bgtv-on.lwp'
        cookie_dir = os.path.join(xbmc.translatePath('special://temp'))
        self.cookie_f = os.path.join(cookie_dir, cookie_file)
        self.cj = LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)

    def account_active(self, login_url='http://www.bgtv-on.com/login', logged_in_string1='logout'):
        # delete any old version of the cookie file
        try:
            remove(self.cookie_f)
        except:
            pass
        req = urllib2.Request(login_url)
        req.add_data('user=' + self.username + '&pass=' + self.password + '&remember=on')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36')
        response = self.opener.open(req)
        source_login = response.read()
        response.close()
        if re.search(logged_in_string1, source_login, re.IGNORECASE):
            self.cj.save(self.cookie_f)
            self.isActive = True
            self.check_validity()
        else:
            xbmcgui.Dialog().notification('[ Login ERROR ]', 'Login FAILED!', xbmcgui.NOTIFICATION_ERROR, 10000, sound=True)
            raise SystemExit
        return self.isActive

    def openurl(self, url):
        try:
            self.cj.load(self.cookie_f, False, False)
        except:
            pass
        req = urllib2.Request(url)
        response = self.opener.open(req)
        url_source = response.read()
        response.close()
        try:
            self.cj.save(self.cookie_f)
        except:
            pass
        return url_source

    def check_validity(self, subscribe_url='http://www.bgtv-on.com/subscribe',alert_days=5):
        subscribe_source = self.openurl(subscribe_url)
        date_expire = re.compile('<p><span.*font-weight.* (.+?)-(.+?)-(.+?)\.').findall(subscribe_source)
        for s_day, s_month, s_year in date_expire:
            days_delta = datetime.datetime(int(s_year), int(s_month), int(s_day)) - datetime.datetime.now()
            xbmc.log("Account is active! You have " + str(days_delta.days) + " days until it expires")
            if days_delta.days <= alert_days:
                xbmcgui.Dialog().notification('[ Your subscription will expire soon ]', 'Only ' + str(days_delta.days) + ' days left!', xbmcgui.NOTIFICATION_INFO, 10000, sound=False)


class PlayVideo(object):
    def __init__(self,acc_active):
        self.is_active = acc_active
        if self.is_active:
            self.match_pattern = '<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
        else:
            xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available', xbmcgui.NOTIFICATION_WARNING, 10000, sound=True)
            xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
            self.match_pattern = '<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'

    def play_live(self,base_source):
        match = re.compile(match_pattern).findall(base_source)
        for cid, ch_image, ch_current in match:
            # here I hide babytv
            # if cid == '47' and hide_babytv == 'true':
            #    continue
            ch_image = (base_url + ch_image)
            liz = xbmcgui.ListItem(ch_current, iconImage="DefaultFolder.png", thumbnailImage=ch_image)
            liz.setInfo(type="Video", infoLabels={"Title": ch_current})
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
            return ok


'''
fill in the credentials
'''
if not xbmcaddon.Addon().getSetting('username') or not xbmcaddon.Addon().getSetting('password') or not xbmcaddon.Addon():
    xbmcaddon.Addon().openSettings()
'''
icons
'''
vid_icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path') + "/resources/png/vid_icon.png")
prog_icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path') + "/resources/png/prog_icon.png")
'''
settings
'''
username = xbmcaddon.Addon().getSetting('username')
password = xbmcaddon.Addon().getSetting('password')
quality = xbmcaddon.Addon().getSetting('quality')
timezone = xbmcaddon.Addon().getSetting('index_tz')
hide_babytv = xbmcaddon.Addon().getSetting('hide_babytv')
'''
web links
'''
base_url = "http://www.bgtv-on.com/"
# subscribe_url = base_url + 'subscribe'
# recording_url = base_url + 'recording'
# programme_url = base_url + 'programme'
# login_url = base_url + 'login'
'''
authenticating
'''
initiate_login = LoginAuth(username, password)
isActive = initiate_login.account_active()
source = initiate_login.openurl(base_url)
