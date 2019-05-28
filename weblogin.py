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

import os,re,urllib,urllib2
import xbmc, xbmcgui
import cookielib

# setting variables
login_url='http://bgtv-on.com/login.php'
header_string='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'

# load cookie
def initCookie():
    # if exist load file and cookie information 
    if (os.path.isfile(cookiepath)):
        cj.load(cookiepath, False, False)       
    else:             
        False

# check if login is successful
def checkLogin(source_login,username):
    logged_in_string1='logout'
    logged_in_string2='m3u8'
    if re.search(logged_in_string1,source_login,re.IGNORECASE) or re.search(logged_in_string2,source_login,re.IGNORECASE):
        return True
    else:
        return False

# open an url using a cookie
def openUrl(url):
    initCookie()
    req=urllib2.Request(url)
    req.add_header('User-Agent',header_string)
    response=urllib2.urlopen(req)
    source=response.read()
    response.close()
    cj.save(cookiepath)
    return source

# login to page
def doLogin(cookiepath, username, password):
    #check if user has supplied only a folder path, or a full path
    if not os.path.isfile(cookiepath):
        #if the user supplied only a folder path, append on to the end of the path a filename.
        cookiepath=os.path.join(cookiepath,cookie_dir_path,cookie_file)
    #delete any old version of the cookie file
    try:
        os.remove(cookiepath)
    except:
        pass
    if username and password:
        req=urllib2.Request(login_url)
        req.add_data('user='+username+'&pass='+password+'&remember=on')
        req.add_header('User-Agent',header_string)
        response=opener.open(req)
        source_login=response.read()
        response.close()
        islogged=checkLogin(source_login,username)
        if islogged==True:
            cj.save(cookiepath)
            return source_login
        else:
            xbmcgui.Dialog().notification('[ Login ERROR ]', 'Wrong username or password!', xbmcgui.NOTIFICATION_ERROR, 8000, sound=True)
            raise SystemExit

# setting cookies' variables
cookie_file='cookies_bgtv-on.lwp'
cookiepath=cookie_file
cookie_dir_path=os.path.join(xbmc.translatePath('special://temp'))
cookiepath=os.path.join(cookiepath,cookie_dir_path,cookie_file)
cj=cookielib.LWPCookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
initCookie()