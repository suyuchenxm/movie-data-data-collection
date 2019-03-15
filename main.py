#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 03:42:43 2019

@author: surichen
"""
import functions as PY
import functions_parsing as parsing
import pandas as pd
#define a dataframe
data=pd.DataFrame()
year='2018'  #input of an interest year

#0. feteching data from Box Office Mojo to get annual top100 moviesName and Rank, Distributor, Gross, Release
data[['Rank','MovieName','Distributor','Gross','Release']],data['Week']=PY.get_annual_list(year) 
mve_top100=[i for i in data['MovieName']] #get the list of annual top100 movies
genre_tb=pd.DataFrame(columns=['MovieName','Genre'])

#the comment below is for chunking the test one by one, for testing. if you want to fetch the data from different website 
#one by one, then you can comment/uncomment each module 
#module list:
#1. fetching data from Box Office MOJO to get ReleaseInfo
#2. fetching data from Douban to get DoubanRate, Year
#3. fetching data from IMDB to get Genre, Runtime, Budget, ProduceCountry
#4. fetching data from Maoyan to get Resource, WeiboClicks, WechatClicks

#data.to_csv(f'{year}_data.csv')
#data=pd.read_csv(f'{year}_data.csv',index_col=0)


#get information for each movie
#=============================if you want to chunk the test, rerun block from here==============================
for idx in data.index:
    print(idx)
    pool=PY.get_proxy_list()
    mve,mve_week=data.loc[idx,['MovieName','Week']]
    #1. fetching data from Box Office Mojo
    try:
        data.loc[idx,'BOM_link'],data.loc[idx,'ReleaseInfo']=PY.get_info_BOM(mve,mve_week,pool,data,idx,year)
    except:
        print('get info from box office mojo error')

    #2. fetching data from DouBan
    try:
        data.loc[idx,'db_link'],data.loc[idx,'db_id'],data.loc[idx,'rating'],data.loc[idx,'year']=PY.get_info_db(mve)
    except:
        print('get info from douban error')
     
   #3. fetching data from imdb        
    try:
        data.loc[idx,'imdb_id'],data.loc[idx,'imdb_link'],genre,data.loc[idx,'Runtime'],data.loc[idx,'Budget'],data.loc[idx,'Country']=PY.get_info_imdb(mve,pool)
    except:
        print('get info from imdb error')
        pass
    try:
        if genre!=None:
            if isinstance(genre,list)!=True:
                genre=[genre]
            i=genre_tb['Genre'].count()
            for item in genre:
                genre_tb.loc[i,['MovieName','Genre']]=mve,item
                i+=1
    except:
        raise GenreError('genre read to list, error')
    
   #4. fetching data from Maoyan
    try:
        page_link,maoyan_id=PY.get_link_maoyan(mve,pool)
        data.loc[idx,'Maoyan_link']=page_link
        data.loc[idx,'TotalWeboClicks']=PY.get_weibo_detail(maoyan_id[0],year)
        data.loc[idx,'TotalWechatClicks']=PY.get_wechat_info(page_link,pool)
        data.loc[idx,'Resource']=PY.get_resource(page_link,pool)
    except:
        print('get info from Maoyan error')
        pass
#============================if you want to chunk the test, rerun block end here=================================


#genre_tb.to_csv('genre_tb_2016.csv')
#parsing data
data1=parsing.release_info(data)
data1=parsing.genre_catagorize(data1,genre_tb)
data1.to_csv(f'{year}_data.csv')
