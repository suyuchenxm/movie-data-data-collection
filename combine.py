#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 04:58:49 2019

@author: surichen
"""
import pandas as pd
data_maoyan=pd.read_csv('2015_maoyan_data.csv',index_col=0)
data_raw=pd.read_csv('2015_data.csv',index_col=0)

data_=pd.merge(data_raw,data_maoyan,on='MovieName',how='left')
data_.to_csv('data_2015.csv',encoding='utf_8_sig')

