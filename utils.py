# import statements
import time
import io
import os
import csv
import hashlib
import re
from tqdm import tqdm
import requests
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

import logging

def collect_web_urls(file_path):
    """
    Reads a url text file for urls and extracts all the web urls saved.
    """
    logging.info("Reading the url text file.")
    urls = set()
    with open(file_path, 'r') as urls_file:
        url_list = urls_file.readlines()
        for url in url_list:
            urls.add(url.strip())
        
    return list(urls)


def extract_images(website_urls, folder_path):
    """
    This method goes over each url and extracts all the images and associated text and
    creates 5 files:
    1. image_urls.txt (contains image source urls for all the images extracted)
    2. img_url_to_captions_new.csv (image urls and corresponding alt text)
    3. img_url_to_text_above_new.csv (image urls and corresponding preceding text)
    4. img_url_to_text_below_new.csv (image urls and corresponding succeeding text)
    5. image_url_to_image_class_names_new.csv (image-urls and the correspinding img tag class name)
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    # scraping all web urls
    logging.info("Processing all web_urls.")

    # Extract images from the website urls
    image_url_dict = {}
    image_urls = []
    image_alt_text = []
    text_above = []
    text_below = []
    image_class_names = []
    img_url_to_caption = {}
    img_url_to_text_above = {}
    img_url_to_text_below = {}
    img_url_to_class_name = {}
    web_url_cntr = 0
    for web_url in tqdm(website_urls):
        logging.info(f"Scraping : {web_url}")
        webpage_image_urls, webpage_image_alt_text, webpage_text_above, webpage_text_below, webpage_image_class_names = fetch_images(web_url)
        time.sleep(1)
        # remove any duplicate images
        idx = 0
        for url in webpage_image_urls:
            if url in image_url_dict:
                idx += 1
                continue
            else:
                image_url_dict[url] = 1
                image_urls.append(url)
                image_alt_text.append(webpage_image_alt_text[idx])
                text_above.append(webpage_text_above[idx])
                text_below.append(webpage_text_below[idx])
                image_class_names.append(webpage_image_class_names[idx])

                # Add to img_url dictionaries
                img_url_to_caption[url] = webpage_image_alt_text[idx]
                img_url_to_class_name[url] = webpage_image_class_names[idx]
                img_url_to_text_above[url] = webpage_text_above[idx]
                img_url_to_text_below[url] = webpage_text_below[idx]
                idx += 1
        web_url_cntr += 1
        
    
    # Dump all image_urls
    write_list(image_urls, os.path.join(query_folder_path, 'ui_images.p'))

    # Write the image url dictionaries
    write_dict(query_folder_path, img_url_to_caption, 'ui_alt_texts.csv', ['Image_Url', 'Image_Alt_Text'])
    write_dict(query_folder_path, img_url_to_text_above, 'ui_instructions_preceding.csv', ['Image_Url', 'Text_Above'])
    write_dict(query_folder_path, img_url_to_text_below, 'ui_instructions_succeeding.csv', ['Image_Url', 'Text_Below'])
    # Classnames can be useful in filtering noisy images like ads etc.
    write_dict(query_folder_path, img_url_to_class_name, 'ui_image_url_to_image_class_names.csv', ['Image_Url', 'Class_Name'])


def fetch_images(website_url):
    """
    This method extracts the data on a web url and then extracts all images present on the
    webpage. For each img tag, it then extracts the class name for it and the preceding
    and succeeding text inside a ul, l, p or div tag. We also apply the length filter on the
    text extracted, i.e. if the number of words is less than 3, we extract more preceding text.
    """
    try:
        response = requests.get(website_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Website url: {website_url} was not retrieved.")
        return [],[],[],[],[]
    
    img_tags = soup.find_all('img', src=True, alt=True)
    
    urls = [img['src'] for img in img_tags]
    
    # Extract all image captions. If img does not have alt text, append empty string.
    image_alt_text = [img['alt'] for img in img_tags]
    
    # Format urls to get list of all image urls from the webpage
    image_urls = []  
    for url in urls:
        if 'http' not in url:
            url = '{}{}'.format(website_url, url)
        image_urls.append(url)

    # Extract text
    text_above = []
    text_below = []
    img_class_names = []
    for img_tag in img_tags:
        if img_tag.has_attr('class'):
            img_class_names.append(img_tag['class'])
        else:
            img_class_names.append("")
        prev_not_found = True
        current_tag = img_tag
        while prev_not_found:
            prev_tag = current_tag.previous_element
            if not prev_tag:
                break
            # EXTRACT TEXT FROM WHATEVER THE PARENT TAG IS (<p>, <div>, <ul>, <l> etc.)
            if prev_tag.name in ['p', 'div', 'ul', 'l']:
                if not filter_text(prev_tag.getText()): #TODO: make sure total number of words is > 2 len(prev_tag.getText()) >= 5 and (not filter_p_tag(prev_tag.getText()))
                    prev_not_found = False
                else:
                    current_tag = prev_tag  
            else:
                current_tag = prev_tag

        next_not_found = True
        current_tag = img_tag
        while next_not_found:
            next_tag = current_tag.next_element
            if not next_tag:
                break
            # EXTRACT TEXT FROM WHATEVER THE PARENT TAG IS (<p>, <div>, <ul>, <l> etc.)
            if next_tag.name in ['p', 'div', 'ul', 'l']:
                if not filter_text(next_tag.getText()): #TODO: make sure total number of words is > 2
                    next_not_found = False
                else:
                    current_tag = next_tag
            else:
                current_tag = next_tag

        if prev_not_found:
            text_above.append('')
        else:
            text_above.append(clean_text(prev_tag.getText()))
        
        if next_not_found:
            text_below.append('')
        else:

            text_below.append(clean_text(next_tag.getText()))


    return image_urls, image_alt_text, text_above, text_below, img_class_names


def download_images(image_urls, query_folder_path):
    """
    Traverses through the list of validated image urls and downloads each of them 
    and saves the image-url to image path map to image_urls_processed.csv file
    """
    done_image_urls_fname = os.path.join(query_folder_path, 'image_urls_processed.csv')

    img_url_to_img_id = {}
    if os.path.exists(done_image_urls_fname):
        with open(done_image_urls_fname,newline='') as processed_file:
            file_reader = csv.reader(processed_file, delimiter='\t')
            for row in file_reader:
                img_url = urlparse(row[0].strip()).geturl()
                img_url_to_img_id[img_url] = row[1]

    print('Downloading all images now...')
    with open(done_image_urls_fname, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Image_Url", "Image_Name"], delimiter='\t')
        idx = 0
        for image_url in tqdm(image_urls):
            img_fname = ''
            if image_url not in img_url_to_img_id:
                img_fname = persist_image(query_folder_path, image_url)
                if img_fname == '':
                    continue
                img_url_to_img_id[image_url] = img_fname
            data = {"Image_Url": image_url, "Image_Name": img_fname}
            writer.writerow(data)
