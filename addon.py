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
import json
from xbmcswift2 import Plugin
import weblogin

plugin = Plugin()

'''
 Settings variables
'''
username=plugin.get_setting('username',str)
password=plugin.get_setting('password',unicode)
timezone=plugin.get_setting('index_tz',int)
quality=plugin.get_setting('quality',str)
vid_icon=xbmc.translatePath(plugin.addon.getAddonInfo('path')+'/resources/png/vid_icon.png')
prog_icon=xbmc.translatePath(plugin.addon.getAddonInfo('path')+'/resources/png/prog_icon.png')
'''
 Web links variables
'''
BASE='http://www.bgtv-on.com/'
subscribe_url=BASE+'subscribe'
recording_url=BASE+'recording'
programme_url=BASE+'programme'
  
@plugin.route('/')
def menu_index():
    try: 
        '''
        it is supported only in newer versions of kodi
        '''
        menu=xbmcgui.Dialog().contextmenu(['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    except:
        menu=xbmcgui.Dialog().select('',['НА ЖИВО','НА ЗАПИС','ПРОГРАМАТА'])
    if menu==0:
        plugin.redirect(plugin.url_for('onair_index'))
    if menu==1:
        plugin.redirect(plugin.url_for('rec_index'))
    if menu==2:
        plugin.redirect(plugin.url_for('prog_index'))

@plugin.route('/stream/')
def onair_index():
    xbmc.log('path: [/stream/]')    
    account_active=check_validity()
    source=weblogin.openUrl(BASE,account_active[1])
    if account_active[0]==True:
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n*\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    elif account_active[0]==False:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TVs are available',xbmcgui.NOTIFICATION_WARNING,10000,sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
        match_pattern='<a href="watch\?cid=(.+?)".*.\n.*.\n.*.<img src="(.+?)".*.\n.*.\n.*.\n.*.\n.*.\n.*.\n.*.<div class="thumb-text">(.+?)<\/div>'
    match=Compile(match_pattern).findall(source)
    items=[{'label':ch_current,'thumbnail':BASE+ch_image,'path':plugin.url_for('onair_stream',cid=cid)} for cid,ch_image,ch_current in match]
    return plugin.finish(items)
            
@plugin.route('/stream/<cid>')    
def onair_stream(cid):
    xbmc.log('path: [/stream/'+cid+']')
    url=BASE+"teko/getchaclap_mbr.php?cid="+cid
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
    plugin.play_video(item)
    xbmcgui.Dialog().notification(text1,text2,icon,10000,sound=False)
    return plugin.finish(None,succeeded=False)
    
@plugin.route('/prog/')
def prog_index():
    xbmc.log('path: [/prog/')
    items=[]
    source=weblogin.openUrl(programme_url,'')
    match=Compile('<a href=programme\?cid=(.+?)#..class=tab >(.+?)<\/a>').findall(source)
    for cid,name in match:
        item={'label':name,'path':plugin.url_for('prod_browse',cid=cid)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/prog/<cid>')
def prod_browse(cid):
    xbmc.log('path: [/prog/'+cid+']')
    items=[]
    url=programme_url+'?cid='+cid
    source=weblogin.openUrl(url,'')
    match_prog=Compile('(<div class="day">(.+?)<\/div>)*(<li style="list-style: none;"><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,time,name in match_prog:
        if day:
            item={'label':'=['+day+']=','path':plugin.url_for('prod_browse',cid=cid)}
            items.append(item)
        time_convd=time_convert(time)
        item={'label':'['+time_convd+'] '+name,'thumbnail':prog_icon,'path':plugin.url_for('prod_browse',cid=cid)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/rec/')    
def rec_index():
    xbmc.log('path: [/rec/]')
    items=[]
    source=weblogin.openUrl(recording_url,'')
    match=Compile('<a href=recording(.+?)#..class=tab.>(.+?)<\/a>').findall(source)
    for cid,name in match:
        item={'label':name,'path':plugin.url_for('rec_browse',cid=cid)}
        items.append(item)
    return plugin.finish(items)

@plugin.route('/rec/<cid>')
def rec_browse(cid):
    xbmc.log('path: [/rec/'+cid+']')
    items=[]
    url=recording_url+cid
    cid=cid.split('=')[1]
    source=weblogin.openUrl(url,'')
    match=Compile('(<div class="day">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1,day,temp2,rec_url,time,name in match:
        if day:
            item={'label':'=['+day+']=','path':plugin.url_for('rec_browse',cid='?cid='+cid)}
            items.append(item)
        time_convd=time_convert(time)
        rec_url=BASE+rec_url
        item={'label':'['+time_convd+'] '+name,'thumbnail':vid_icon,'path':plugin.url_for('rec_play',url=rec_url,name=name)}
        items.append(item)
    return plugin.finish(items)
    
@plugin.route('/rec/play/<url>/<name>')
def rec_play(url,name):
    items=[]
    xbmc.log('path: [/rec/play/'+url+'/'+name+']')
    account_active=check_validity()
    if account_active[0] == False:
        xbmcgui.Dialog().notification('[ You don\'t have valid subscription ]', 'Not Available without subscribtion!',xbmcgui.NOTIFICATION_WARNING,10000,sound=True)
        raise SystemExit
    '''
    getting the video url
    '''
    source=weblogin.openUrl(url,account_active[1])
    match=Compile('source:."(.+?)"').findall(source)
    match_info=Compile('<div class="content-title">(.+?)<\/div>').findall(source)
    item={'label':'PLAY: '+name,'path':match[0],'is_playable':True}
    items.append(item)
    return plugin.finish(items)
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
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]','Only '+str(days_delta.days)+' days left!',xbmcgui.NOTIFICATION_INFO,10000,sound=False)
    return (account_active,cookiepath)
'''
time convert based on TZ in conf
'''
def time_convert(time_orig):
    h,m=time_orig.split(':')
    time_orig=datetime.time(int(h),int(m))
    time_diff=abs(timezone-13)
    if timezone>13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)+datetime.timedelta(hours=time_diff)).time()
    elif timezone<13:
        hol=(datetime.datetime.combine(datetime.date(1900,01,01),time_orig)-datetime.timedelta(hours=time_diff)).time()
    h,m,s=str(hol).split(':')
    time_modified=h+':'+m
    return time_modified
'''
the main function
'''
def main():
    if not username or not password:
        plugin.open_settings()
    plugin.run()

if __name__ == '__main__':
    main() 
