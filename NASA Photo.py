# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
import urllib.request
from google.cloud import storage
from dotenv import load_dotenv
import os
import os.path

load_dotenv()
google_app_credential = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
nasa_key = os.getenv("NASA_API_KEY")

def download_photo_by_date(date):
    url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date='+date\
          +'&api_key=' + nasa_key
    res = requests.get(url).json()
    photos_list = res['photos']

    index_list = []

    for photo_info in photos_list:
        url = photo_info['img_src']
        filename = url.split('/')[-1]
        index_list.append(filename.split('.')[0])
        filepath = './images/' + filename
        urllib.request.urlretrieve(url, filepath)
        print(filename, ' is downloaded')
    create_metadata_csv(photos_list, index_list)


def upload_blob(bucket_name, source_file_directory):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for filename in os.listdir(source_file_directory):
        filepath = './images/'+filename
        blob = bucket.blob(filename)
        blob.upload_from_filename(filepath)
        print(filename, ' is uploaded')

def create_metadata_csv(list_of_dict, index_list):
    clean_list_of_dict = []
    for img in list_of_dict:
        clean_dict = {}
        clean_dict['id'] = img['id']
        camera = img['camera']
        for key in camera.keys():
            clean_dict["camera "+key] = camera[key]

        rover = img['rover']
        for key in rover.keys():
            if key == 'cameras':
                cameras = ''
                for data_dict in rover[key]:
                    cameras = cameras + data_dict['name']+' ( '+data_dict['full_name']+' ), '
                clean_dict["rover "+key] = cameras[0:-2]
            else:
                clean_dict["rover  " + key] = rover[key]
        clean_dict['sol'] = img['sol']
        clean_dict['earth_date'] = img['earth_date']
        clean_dict['img_src'] = img['img_src']
        clean_list_of_dict.append(clean_dict)


    df = pd.DataFrame(clean_list_of_dict, index=index_list)
    df.index.name = 'filename'
    df.to_csv(r'./metadata.csv')
    storage_client = storage.Client()
    bucket = storage_client.bucket('nasa-photos')
    blob = bucket.blob('metadata.csv')
    blob.upload_from_filename('./metadata.csv')

if __name__ == '__main__':
    download_photo_by_date('2016-2-2');
    upload_blob('nasa-photos', 'images')