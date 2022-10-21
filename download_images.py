# import statements
import time
import io
import os
import csv
import hashlib
import re
from tqdm import tqdm
import requests
import argparse
import pickle
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from UICaption.utils import extract_orig_dname, download_images

parser = argparse.ArgumentParser()
    
parser.add_argument("--i", help='Absolute path to the image url file.', required=True)

args = parser.parse_args()

img_url_fname = args.i

folder_path = os.path.split()[0]

# Read all image_urls 
with open(image_url_fname, 'rb') as in_file:
    lines = pickle.load(in_file)

idx_to_valid_urls = {}
for line in lines:
    # validate if this is a url
    # else join with next line until we have a valid url
    if line.startswith('https'):
        idx_to_valid_urls[len(idx_to_valid_urls)] = urlparse(line.strip()).geturl()
    else:
        prev_idx = len(idx_to_valid_urls)-1
        prev_component = idx_to_valid_urls[prev_idx]
        idx_to_valid_urls[prev_idx] = urljoin(prev_component, line.strip())

image_urls = []
for idx in idx_to_valid_urls:
    image_urls.append(idx_to_valid_urls[idx])

download_images(image_urls, folder_path)
