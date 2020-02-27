# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from dotenv import load_dotenv
import os
import sys
import tempfile
import requests
import urllib.request
from google.cloud import storage
import logging
import pandas as pd


def request_nasa_photo_by_date(api_key, date, img_cloud_dir, metadata_filename, metadata_cloud_dir):
    url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?' \
          f'earth_date={date}&api_key={api_key}'
    response = requests.get(url)
    if response.status_code != 200:
        sys.exit("ERROR: Invalid API key")
    data = response.json()
    photos_list = data['photos']

    filename_list = []
    for photo_info in photos_list:
        url = photo_info['img_src']
        img_name = url.split('/')[-1]
        filename_list.append(img_name)
        response = requests.get(url)
        if response.status_code != 200:
            sys.exit("ERROR: Invalid image link")
        logging.info(f'{img_name} is successfully requested')
        upload_nasa_photo_to_cloud(img_name, url, img_cloud_dir)
    write_metadata_to_csv(photos_list, filename_list, metadata_filename, metadata_cloud_dir)

def upload_nasa_photo_to_cloud(img_name, url, cloud_directory):
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.name = img_name
    urllib.request.urlretrieve(url, fp.name)
    cloud_img_name = cloud_directory.blob(img_name)
    cloud_img_name.upload_from_filename(fp.name)
    os.unlink(fp.name)
    logging.info(f'{img_name} is uploaded to cloud directory {cloud_directory}')

def write_metadata_to_csv(photos_list, filename_list, metadata_filename, metadata_cloud_dir):
    clean_list_of_photo_dict = clean_nested_metadata(photos_list)

    df = pd.DataFrame(clean_list_of_photo_dict, index=filename_list)
    df.index.name = 'filename'

    upload_metadata_csv_to_cloud(df, metadata_filename, metadata_cloud_dir)

def clean_nested_metadata(photos_list):
    clean_list_of_photo_dict = []
    for img in photos_list:
        clean_photo_dict = {}
        clean_photo_dict['id'] = img['id']
        camera = img['camera']
        for key in camera.keys():
            clean_photo_dict[f'camera {key}'] = camera[key]

        rover = img['rover']
        for key in rover.keys():
            if key == 'cameras':
                cameras = ''
                for data_dict in rover[key]:
                    cameras = f'{cameras} {data_dict["name"]} ({data_dict["full_name"]})'
                clean_photo_dict[f"rover {key}"] = cameras[0:-2]
            else:
                clean_photo_dict[f"rover {key}"] = rover[key]
        clean_photo_dict['sol'] = img['sol']
        clean_photo_dict['earth_date'] = img['earth_date']
        clean_photo_dict['img_src'] = img['img_src']
        clean_list_of_photo_dict.append(clean_photo_dict)
    return clean_list_of_photo_dict

def upload_metadata_csv_to_cloud(df, metadata_filename, metadata_cloud_dir):
    fp = tempfile.NamedTemporaryFile(delete=False)
    fp.name = f'{metadata_filename}.csv'
    df.to_csv(fp.name)
    cloud_metadata_filename = metadata_cloud_dir.blob(fp.name)
    cloud_metadata_filename.upload_from_filename(fp.name)
    os.unlink(fp.name)
    logging.info(f'{metadata_filename}.csv is uploaded to cloud directory {metadata_cloud_dir}')

def manage_api_key(new_key):
    load_dotenv()
    if new_key:
        os.environ["NASA_API_KEY"] = new_key
        return new_key
    old_key = os.getenv("NASA_API_KEY")
    return old_key

def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", type=str, help="YYYY-MM-DD")
    parser.add_argument("img_cloud_bucket_name", type=str,
                        help="directory name to store photos in cloud")
    parser.add_argument("metadata_filename", type=str,
                        help="csv filename to store metadata of the photos")
    parser.add_argument("metadata_cloud_bucket_name", type=str,
                        help="directory name to store metadata csv in cloud")
    parser.add_argument("--api_key", help="NASA MARS Photo API key")
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    # cmd example: python3 NASA\ Photo.py 2016-02-02 nasa-test1 metadata1 nasa-test1

    args = parse_cmd_args()
    nasa_key = manage_api_key(args.api_key)

    logging.basicConfig(level=logging.INFO)

    storage_client = storage.Client()
    img_cloud_directory = storage_client.bucket(args.img_cloud_bucket_name)
    metadata_cloud_directory = storage_client.bucket(args.metadata_cloud_bucket_name)

    request_nasa_photo_by_date(nasa_key, args.date, img_cloud_directory,
                               args.metadata_filename, metadata_cloud_directory)