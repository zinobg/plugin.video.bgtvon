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

import urllib2
from os import path,remove
from re import search,IGNORECASE
from xbmc import translatePath,log
from xbmcgui import Dialog,NOTIFICATION_ERROR
from cookielib import LWPCookieJar

'''
setting up cookie jar
'''
cj=LWPCookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
'''
check if login is successful
'''
def checkLogin(source_login,username):
    logged_in_string1='logout'
    logged_in_string2='m3u8'
    if search(logged_in_string1,source_login,IGNORECASE) or search(logged_in_string2,source_login,IGNORECASE):
        return True
    else:
        return False
'''
login to page
'''
def doLogin(username,password):
    logged_in_string1='logout'
    login_url='http://bgtv-on.com/login'
    cookie_file='cookies_bgtv-on.lwp'
    cookie_dir=path.join(translatePath('special://temp'))
    cookiepath=path.join(cookie_dir,cookie_file)
    #log('function: doLogin - start - cookiepath: '+str(cookiepath))
    '''
    delete any old version of the cookie file
    '''
    try:
        remove(cookiepath)
    except:
        pass
    if username and password:
        req=urllib2.Request(login_url)
        req.add_data('user='+username+'&pass='+password+'&remember=on')
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36')
        response=opener.open(req)
        source_login=response.read()
        response.close()
        islogged=checkLogin(source_login,username)
        if search(logged_in_string1,source_login,IGNORECASE):
            cj.save(cookiepath)
            return cookiepath
        else:
            Dialog().notification('[ Login ERROR ]','Login FAILED!',NOTIFICATION_ERROR,10000,sound=True)
            raise SystemExit
'''
open an url using a cookie
'''
def openUrl(url,cookiepath):
    try:
        cj.load(cookiepath,False,False)  
    except:
        pass
    req=urllib2.Request(url)
    response=opener.open(req)
    source=response.read()
    response.close()
    try:
        cj.save(cookiepath)
    except:
        pass
    return source