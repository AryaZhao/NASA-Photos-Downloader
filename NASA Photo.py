# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
import urllib.request


def download_photo_by_date(date):
    my_key = 'hum8hHccg2KFrhKW5fFCJ0y9M8SVfcye3CS5SnJ4'
    url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date='+date\
          +'&api_key=' + my_key
    res = requests.get(url).json()
    photos_list = res['photos']
    for photo_info in photos_list:
        url = photo_info['img_src']
        filename = url.split('/')[-1]
        filepath = './images/' + filename
        urllib.request.urlretrieve(url, filepath)
        # print('downloading photo '+ filename)

if __name__ == '__main__':
    download_photo_by_date('2016-2-2');