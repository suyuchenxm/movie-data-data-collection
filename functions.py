#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 03:28:58 2019

@author: surichen
"""

import requests
import json
import datetime
import re
import pandas as pd
from bs4 import BeautifulSoup

def get_annual_list(year):
   '''This function scrap the top100 movie in China from Box Office mojo'''
   import pandas as pd
   from datetime import datetime
   url=f'https://www.boxofficemojo.com/intl/china/yearly/?yr={year}&p=.htm'
   dfs = pd.read_html(url,header=0)
   week=[datetime.strptime(dfs[2].loc[i,'Release'],'%m/%d').isocalendar()[1] for i in dfs[2].index]
   return dfs[2],week

def get_proxy_list():
    '''function get_proxy_list() return a list of free proxies from the website free-proxy-list '''
    url='https://free-proxy-list.net/'
    response=requests.get(url)
    proxies_=pd.read_html(response.text)
    proxies=list()
    for idx in range(0,300):
        if proxies_[0].loc[idx,'Https'] == 'yes':
            proxy=":".join([proxies_[0].loc[idx,'IP Address'],str(proxies_[0].loc[idx,'Port'])[:-2]])
            proxies.append(proxy)
    return proxies
                                                 
def generate_proxy(proxies):
    '''function generate_proxy randomly genrate one proxies from the pool   '''
    import random as rd
    return proxies[rd.randint(0,len(proxies))]

def get_tag(proxy,url,tag,mve):
    '''function get_tag return the desired tag from a website'''
    soup,tag_=None,None
    try:
        response=requests.get(url,proxies={'http':proxy,'https':proxy},headers={"User-Agent":"Mozilla/5.0"},timeout=10)
        soup=BeautifulSoup(response.text,'html.parser')
        tag_=soup.find(tag,string=mve)
    except:
        print (f'proxy doesnt work, skip {proxy}')
    return tag_


def get_info_BOM(mve,mve_week,pool,data,idx,year):
    '''function get_info_BOM return data of duration and the movie page on box office mojo website'''
    from datetime import datetime
    mve_week=str(int(mve_week)+1)
    url=f'https://www.boxofficemojo.com/intl/china/?yr={year}&wk={mve_week}&p=.htm'
    tag,i=None,0
    while tag==None and i<=10:
        proxy=generate_proxy(pool)
        tag=get_tag(proxy,url,'a',mve)
        i+=1
    print(f'succeed, using proxy {proxy}, tag: {tag}')
    try:
        url2='https://www.boxofficemojo.com/'+tag.get('href')
        #getting release duration
        if 'intl' in url2:
            response=requests.get(url2,proxies={'http':proxy,'https':proxy})
            df_mve=pd.read_html(response.text,header=0)
            duration=len(df_mve[6].index)-1
        if 'default' in url2:
            url2=url2.replace('default.htm?','?page=intl&')
            response=requests.get(url2,proxies={'http':proxy,'https':proxy})
            df_mve=pd.read_html(response.text,match='China',header=0)
            end=df_mve[-1][df_mve[-1]['Country(click to view weekend breakdown)']=='China']['Unnamed: 6'].item()
            date_release=datetime.strptime(data.loc[idx,'Release']+f'/{year}','%m/%d/%Y')
            date_end=datetime.strptime(end,'%m/%d/%y')
            duration=((date_end-date_release).days//7)+1
    except:
        print(f'get {mve} info from Box Office Mojo error')
        url2,duration=None,None
        pass
    return url2, duration    

def get_info_db(mve):
    '''function get_info_db connect to the api of douban.com, there is no need to rotate the proxy, however, if the request
        doesn't work, uncomment the lines followed in this function'''
    import requests
    import json
    try:
        db_link,db_id,rating,year=None,None,None,None
        api_search=f'https://api.douban.com/v2/movie/search?q={mve}'
        resp=json.loads(requests.get(api_search).text)
        db_link=resp['subjects'][0]['alt']        
        db_id=resp['subjects'][0]['id']
        rating=resp['subjects'][0]['rating']['average']
        year=resp['subjects'][0]['year']
    except:
        print('douban mve api error')
        pass
    return db_link,db_id,rating,year

def get_info_imdb(mve,pool):
    import json
    import re
    imdbid,imdb_url,genre,runtime,budget,country=None,None,None,None,None,None
    try:
        omdb_key='7adfdc0c'
        omdb=f'http://www.omdbapi.com/?apikey={omdb_key}&t={mve}'
        resp=json.loads(requests.get(omdb).text)
        imdbid=resp['imdbID']
        imdb_url=f'https://www.imdb.com/title/{imdbid}/?ref_=nv_sr_1'
        proxy=generate_proxy(pool)
        error=1
        while error==1:
            try:
                response=requests.get(imdb_url,proxies={'http':proxy,'https':proxy})
                error=0
                print(f'succeed, using proxy:{proxy} for imdb')
            except:
                error=1
                proxy=generate_proxy(pool)
                
        r=response.text
        #genre: getting the list of genre of the mve, by index searching
        genre_idx_start = r.find('<script type="application/ld+json">')
        genre_idx_end = 0
        while genre_idx_end < genre_idx_start:
                genre_idx_end = r.find('</script>', genre_idx_end+5)
        genre_json=r[genre_idx_start+len('<script type="application/ld+json">'):genre_idx_end]
        genre_json=json.loads(genre_json)
        genre=genre_json['genre']
            
        #runtime: getting run time of the mve
        runtime_idx_start=r.find('Runtime:')
        runtime_idx_end=r[runtime_idx_start:].find('</time>')
        runtime=re.findall(r'(?<=>)[0-9]\w+',r[runtime_idx_start:runtime_idx_end+runtime_idx_start])
        if runtime==[]:
           runtime=None
        
        #buget：getting budget information of the mve, by index searching
        budget_idx_start = r.find('<h4 class="inline">Budget:</h4>')
        budget_idx_end=0
        while budget_idx_end < budget_idx_start:
              budget_idx_end = r.find('<span class="attribute">(estimated)</span>', budget_idx_end+5)
        budget=r[budget_idx_start+len('<h4 class="inline">Budget:</h4>'):budget_idx_end]
        
        #country: getting country information by regex method
        soup=BeautifulSoup(r,'html.parser')
        info_text=soup.find('div',{'class': "article",'id':"titleDetails"}).get_text()
        country=re.findall(r'(?<=Country:\n)[a-zA-Z]\w+',info_text)
        if country==[]:
           country=None     
        #return: imdb id, imdb link, genre(list), runtime, budget and producecountry
    except:
        print(f'get {mve} from imdb failed')
        pass
    return imdbid,imdb_url,genre,runtime,budget,country 


def get_info_maoyan(mve,pool):
    '''function get_info_maoyan get resource and maoyan_id from maoyan movie page'''
    import re
    mve=re.sub('[()]', '', mve)
    resource,page_url,mve_id=None,None,None
    search_page=f'https://piaofang.maoyan.com/search?key={mve}'
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
    try:
        proxy=generate_proxy(pool)
        error=1
        while error==1:
            try:
                response=requests.get(search_page,headers=headers,proxies={'http':proxy,'https':proxy})
                error=0
                print(f'succeed, using proxy:{proxy} for maoyan')
            except:
                error=1
                proxy=generate_proxy(pool)
        r=response.text
        soup=BeautifulSoup(r,'html.parser')
        print('succeed')
        if soup==None:
            print('maoyan searching process error')
            return page_url, mve_id
        else:
            data_url=soup.find('article',{'class':"indentInner canTouch"}).get('data-url')
            page_url=f'https://piaofang.maoyan.com{data_url}'
            mve_id=re.findall(r'(?<=/)[0-9]\w+',page_url)
    except:
        print('get info from maoyan failed')
        pass
    if mve_id==None:return resource, page_url, mve_id
    else:return page_url,mve_id


def get_weibo_detail(movie_id,year):
    '''function get_weibo_detail get info of weiboclickNum from maoyan movie page'''
    from functools import reduce
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
    }
    #released_date, movie_name = get_infos(movie_id)
    # I accidentally found this api through the network page of Chrome Web Developer tools, while i was selecting the dates.
    # It returns all the data in json format, which starts from the date the system starts collecting data(around released_date + 45)
    # The data of the last few dates are all zeros due to the fact you cannot select them in the web. You may want to delete them.
    query_url = 'https://piaofang.maoyan.com/movie/{}/promption-ajax?method=change&type=weibo&startDate={}&endDate={}'.format(movie_id,
                                                   year+'-01-01',
                                                   datetime.datetime.today().strftime('%Y-%m-%d'))
    json_string = requests.get(query_url, headers=headers).text
    json_data = json.loads(json_string)
    data = json_data['data']
    if data!=[]:
        sum_=reduce(lambda x,y: x+y, [int(data[idx]['likeNum']) for idx in range(len(data))])
    else:
        sum_=None
    return sum_

def get_resource(url,proxies):
    '''function get_resource input maoyan url of one movie and ouput Resource'''
    url_promo=url+'/promotion/trailers'
    proxy=generate_proxy(proxies)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
    }
    page=requests.get(url_promo,proxies={'http':proxy,'https':proxy},headers=headers)
    while page.status_code!=200:
        resources=None
        print('request error, change proxy')
        proxy=generate_proxy(proxies)
        page=requests.get(url_promo,proxies={'http':proxy,'https':proxy},headers=headers)
    print('request success')
    soup=BeautifulSoup(page.content,'html.parser')
    resources= soup.find('div',{'class':'tralier'}).find('div',{'class':'play-number'}).find('div',{'class':'value-style'}).get_text()
    if resources!=[]:
        pass
    else:
        resources=None
    return resources
    
def get_wechat_info(url,proxies):
    '''function get_wechat_info input maoyan url of one movie and output WechatTotalClick'''
    url_promo=url+'/promotion/wechat'
    proxy=generate_proxy(proxies)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
    }
    page=requests.get(url_promo,proxies={'http':proxy,'https':proxy},headers=headers)
    while page.status_code!=200:
        weibo_click=None
        print('request error, change proxy')
        proxy=generate_proxy(proxies)
        page=requests.get(url_promo,proxies={'http':proxy,'https':proxy},headers=headers)
    print('request success')
    soup=BeautifulSoup(page.content,'html.parser')
    tmp= soup.find('div',{'class':'wechat-summary'}).find_all('span',{'class':'summary-cotnent-val'})
    wechat_click=tmp[1].get_text()
    if wechat_click!=[]:
        unit=soup.find('div',{'class':'wechat-summary'}).find_all('span',{'class':'summary-cotnent-unit'})
        wechat_click=wechat_click+unit[1].get_text()
    else:
        wechat_click=None
    return wechat_click

def get_link_maoyan(mve,pool):
    '''function get_info_maoyan input movie name and output maoyan url and maoyan_id from maoyan movie page'''
    import re
    mve=re.sub('[()]', '', mve)
    resource,page_url,mve_id=None,None,None
    search_page=f'https://piaofang.maoyan.com/search?key={mve}'
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
    try:
        proxy=generate_proxy(pool)
        error=1
        while error==1:
            try:
                response=requests.get(search_page,headers=headers,proxies={'http':proxy,'https':proxy})
                error=0
                print(f'succeed, using proxy:{proxy} for maoyan')
            except:
                error=1
                proxy=generate_proxy(pool)
        r=response.text
        soup=BeautifulSoup(r,'html.parser')
        print('succeed')
        if soup==None:
            print('maoyan searching process error')
            return resource,page_url, mve_id
        else:
            data_url=soup.find('article',{'class':"indentInner canTouch"}).get('data-url')
            page_url=f'https://piaofang.maoyan.com{data_url}'
            mve_id=re.findall(r'(?<=/)[0-9]\w+',page_url)
    except:
        print('get info from maoyan failed')
        pass
    #if mve_id==None:return resource, page_url, mve_id
    else:return page_url,mve_id

#if  __name__ == '__main__':
  
    
