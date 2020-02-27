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

import datetime,time
from re import compile as Compile
import xbmc,xbmcgui
from xbmcaddon import Addon
from xbmcswift2 import Plugin,ListItem
import weblogin

plugin = plugin = Plugin()

'''
 Settings variables
'''
__settings__=Addon()
username=__settings__.getSetting('username')
password=__settings__.getSetting('password')
timezone=__settings__.getSetting('index_tz')
quality=__settings__.getSetting('quality')
vid_icon=xbmc.translatePath(__settings__.getAddonInfo('path')+"/resources/png/vid_icon.png")
prog_icon=xbmc.translatePath(__settings__.getAddonInfo('path')+"/resources/png/prog_icon.png")
'''
 Web links variables
'''
BASE="http://www.bgtv-on.com/"
subscribe_url=BASE+'subscribe'
recording_url=BASE+'recording'
programme_url=BASE+'programme'
  
@plugin.route('/')
def menu_index():
    dialog=xbmcgui.Dialog()
    menu=dialog.select('',['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    if menu==0:
        plugin.redirect(plugin.url_for('onair_index'))
    if menu==1:
        plugin.redirect(plugin.url_for('rec_index'))
    if menu==2:
        plugin.redirect(plugin.url_for('prog_index'))

@plugin.route('/stream/')
def onair_index():
    items=[]
    xbmc.log('path: [/stream/]')    
    account_active=check_validity()
    source=weblogin.openUrl(BASE,account_active[1])
    if account_active[0]==True:
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    elif account_active[0]==False:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=Compile(match_pattern).findall(source)
    for cid,ch_image,ch_current in match:
        ch_image=BASE+ch_image
        source_url=BASE+"teko/getchaclap_mbr.php?cid="+cid
        item={'label':ch_current,'thumbnail':ch_image,'path':plugin.url_for('onair_stream',url=source_url)}
        items.append(item)
    return plugin.finish(items)
            
@plugin.route('/stream/<url>/')    
def onair_stream(url):
    xbmc.log('path: [/stream/'+url+']')
    cookiepath=weblogin.doLogin(username,password)
    source=weblogin.openUrl(url,cookiepath)
    src_list=list(source.split(","))
    if quality=='moderate':
        xbmc.log('1-quality: '+quality+' and nuber of streams: '+str(len(src_list)))
        items=[]
        for i in range(len(src_list)):
            play_list=correct_stream_url(src_list[i])
            item={'label':play_list[0],'path':play_list[1],'is_playable':True}
            items.append(item)
        return plugin.finish(items)
    '''
    Presuming that the first steam has the lowest quality and the last - the highest
    0 - getting the first stream link
    1 - getting the last stream link
    '''
    if quality=='low' or len(src_list)==1:
        element=0
    if quality=='high' and len(src_list)>1:
        element=-1
    xbmc.log('2-quality: '+quality+' and nuber of streams: '+str(len(src_list)))
    play_list=correct_stream_url(src_list[element])
    item={'label':play_list[0],'path':play_list[1]}
    plugin.play_video(item)
    return plugin.set_resolved_url()
    
@plugin.route('/prog/')
def prog_index():
    xbmc.log('path: [/prog/')
    items=[]
    source=weblogin.openUrl(programme_url,'')
    match=Compile('<a href=programme\?cid=(.+?)#..class=tab >(.+?)<\/a>').findall(source)
    for cid,name in match:
        url=programme_url+'?cid='+cid
        item={'label':name,'path':plugin.url_for('prod_browse',url=url)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/prog/<url>/')
def prod_browse(url):
    xbmc.log('path: [/prog/'+url+']')
    items=[]
    source=weblogin.openUrl(url,'')
    match_prog=Compile('(<div class="day">(.+?)<\/div>)*(<li style="list-style: none;"><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,time,name in match_prog:
        del temp1,temp2
        if day:
            item={'label':'=['+day+']=','path':''}
            items.append(item)
        time_convd=time_convert(time)
        item={'label':'['+time_convd+'] '+name,'thumbnail':prog_icon,'path':plugin.url_for('prod_browse',url=url)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/rec/')    
def rec_index():
    xbmc.log('path: [/rec/]')
    items=[]
    source=weblogin.openUrl(recording_url,'')
    match=Compile('<a href=recording(.+?)#..class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match:
        url=(recording_url+cid)
        item={'label':name,'path':plugin.url_for('rec_browse',url=url)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/rec/<url>')
def rec_browse(url):
    xbmc.log('path: [/rec/'+url+']')
    items=[]
    source=weblogin.openUrl(url,'')
    match=Compile('(<div class="day">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,rec_url,time,name in match:
        del temp1,temp2
        if day:
            item={'label':'=['+day+']=','path':plugin.url_for('rec_browse',url=url)}
            items.append(item)
        time_convd=time_convert(time)
        rec_url=BASE+rec_url
        item={'label':'['+time_convd+'] '+name,'thumbnail':vid_icon,'path':plugin.url_for('rec_play',url=rec_url)}
        items.append(item)
    return plugin.finish(items)
    
@plugin.route('/rec/play/<url>')
def rec_play(url):
    xbmc.log('path: [/rec/play/'+url+']')
    account_active=check_validity()
    if account_active[0] == False:
        xbmcgui.Dialog().notification('[ You don\'t have valid subscription ]', 'Not Available without subscribtion!',xbmcgui.NOTIFICATION_WARNING,8000,sound=True)
        raise SystemExit
    source=weblogin.openUrl(url,account_active[1])
    match=Compile('source:."(.+?)"').findall(source)
    for rec_url in match:
        item={'label':rec_url,'path':rec_url}
        plugin.play_video(item)
    return plugin.set_resolved_url()
'''
function that returns a tupple: title to show and stripped stream link
'''
def correct_stream_url(raw_stream):
    stream=raw_stream.lstrip('[').rstrip(']').strip('"')
    titles=Compile('liveedge\/(.+?).stream').findall(stream)
    for title in titles:
        title="["+title.replace('_','] [').upper()+"]"
    return (title,stream)
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
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]','Only '+str(days_delta.days)+' days left!',xbmcgui.NOTIFICATION_INFO,8000,sound=False)
    return (account_active,cookiepath)
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
    del s
    time_modified=h+':'+m
    return time_modified
'''
the main function
'''
def main():
    if not username or not password or not __settings__:
        plugin.open_settings()
    plugin.run()

if __name__ == '__main__':
    main()
    