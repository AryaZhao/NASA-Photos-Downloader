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
    for photo_info in photos_list:
        url = photo_info['img_src']
        filename = url.split('/')[-1]
        filepath = './images/' + filename
        urllib.request.urlretrieve(url, filepath)
        # print(filename, ' is downloaded')


def upload_blob(bucket_name, source_file_directory):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for filename in os.listdir(source_file_directory):
        filepath = './images/'+filename
        blob = bucket.blob(filename)
        blob.upload_from_filename(filepath)
        print(filename, ' is uploaded')


if __name__ == '__main__':
    # download_photo_by_date('2016-2-2');
    upload_blob('nasa-photos', 'images')