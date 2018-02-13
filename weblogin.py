import os,re,urllib,urllib2
import xbmc, xbmcgui
import cookielib

def check_login(source_login,username):
    logged_in_string = 'logout'
    logged_in_string2 = 'm3u8'
    if re.search(logged_in_string,source_login,re.IGNORECASE) or re.search(logged_in_string2,source_login,re.IGNORECASE):
        return True
    else:
        return False

def doLogin(cookiepath, username, password, url_to_open):
    #check if user has supplied only a folder path, or a full path
    if not os.path.isfile(cookiepath):
        #if the user supplied only a folder path, append on to the end of the path a filename.
        cookiepath = os.path.join(cookiepath,os.path.join(xbmc.translatePath("special://temp"), 'cookies_bgtvon.lwp'))
    #delete any old version of the cookie file
    try:
        os.remove(cookiepath)
    except:
        pass

    if username and password:
        login_url = 'http://bgtv-on.com/login.php'
        header_string = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
        login_data = urllib.urlencode({'user':username,'pass':password,'rememberme':'on'})
        req = urllib2.Request(login_url, login_data)
        req.add_header('User-Agent',header_string)
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.open(req)
        response = opener.open(url_to_open)
        source_login = response.read()
        response.close()
        login = check_login(source_login,username)
        if login == True:
            cj.save(cookiepath)
            return source_login
        else:
            xbmcgui.Dialog().notification('[ Login ERROR ]', 'Wrong username or password!', xbmcgui.NOTIFICATION_ERROR, 8000, sound=True)
            raise SystemExit
