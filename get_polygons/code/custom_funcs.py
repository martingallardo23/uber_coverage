"""
Includes custom functions for the main module.
"""

# Get packages
import os
from urllib.request import Request
from urllib.request import urlopen
import re
import zipfile
from bs4 import BeautifulSoup

# Initialize scraper
def start_scraper (url):
    html = Request(url)
    html.add_header(
        'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
    html.add_header(
        'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    resp     = urlopen(html)
    raw_html = resp.read()
    soup     = BeautifulSoup(raw_html, 'html.parser')

    return soup

# Get list of countries
def get_countries(soup):
    country_class = soup.find('div', text = 'Argentina').previous_element.previous_element['class'] 
    country_class = ' '.join([str(item) for item in country_class])
    countries     = soup.find_all('div', class_ = country_class)

    return countries

# Get list of cities
def get_cities(soup, country):
    city_class = soup.find('div', text='Buenos Aires')['class'] 
    city_class = ' '.join([item for item in city_class]) 
    cities     = country.find_all('div', class_ = city_class) 

    return cities

# Get list of clean country names
def clean_country_names(country):
    country_name       = country.find('h3').get_text()
    country_name_short = re.sub("\\.", "", country_name)
    country_name_short = re.sub("[^0-9a-zA-Z]+", "_", country_name_short).lower()

    return country_name, country_name_short
    
# Get list of clean city names
def clean_city_names(city):
    city_name       = city.get_text()
    city_name_short = re.sub("\\.", "", city_name)
    city_name_short = re.sub("[^0-9a-zA-Z]+", "_", city_name_short).lower()
    city_link       = city.find('a')['href']

    return city_name, city_name_short, city_link

# Get geojson in text format
def get_lat_lons(html, country_name_short, city_name_short,
                 country_name, city_name):
    text = html[html.index('geoJson'):]
    text = text.replace('geoJson\\u0022:', '')
    text = text[:text.index('},\\u0022defaultMapLat')]

    # Remove the coordinate labels
    text = text.replace('\\u0022lat\\u0022:', '')
    text = text.replace('\\u0022lng\\u0022:', '')
    text = text.split('],[')
    text = [x.replace('{', '[').replace('}', ']') for x in text]
    text = [x.split('],[') for x in text]

    # Swap lats and lons
    for j, val in enumerate(text):
        for i, coord in enumerate(val):
            lat_long   = coord.replace('[', '').replace(']', '')
            lat_long   = lat_long.split(',')
            lat_long[0], lat_long[1] = lat_long[1], lat_long[0]
            text[j][i] = '[' + ','.join(lat_long) + ']'
        text[j] = '[[' + ','.join(text[j]) + ']]'

    # Build geojson
    geojson = '{ "type": "Feature", "properties": { }, "geometry": { "type": "Polygon", "coordinates":'

    properties = f'{{ "name": "{country_name_short}_{city_name_short}", "country": "{country_name}", "city": "{city_name}" }}'

    # Write geojson
    for i, v in enumerate(text):
        text[i] = f'{geojson} {v} }} , "properties":{properties} }}\n'

    text    = ',\n'.join(poly for poly in text)
    geojson = f'{{ "type": "FeatureCollection", "features": [\n{text}]\n}}\n'
    
    return geojson, text
     
def write_geojson(geojson, country_name_short, city_name_short, save_path): 
    file_name = f'{country_name_short}-{city_name_short}.geojson'
    file_name = os.path.join(save_path, file_name)
    file      = open(file_name, 'w')
    file.write(geojson)
    file.close()

def save_dn_download(dn_download, save_path):
    file_name = 'dn_download.txt'
    file_name = os.path.join(save_path, file_name)
    file      = open(file_name, 'w')
    file.write('\n'.join(dn_download))
    file.close()

    print(f'{len(dn_download)} cities couldn\'t be downloaded')

def compile_zip(save_path):
    file_name = 'geojson_files.zip'
    file      = os.path.join(save_path, file_name)
    zipf      = zipfile.ZipFile(file, 'w')

    for root, dirs, files in os.walk(save_path):
        for file in files:
            if file.endswith('.geojson'):
                zipf.write(os.path.join(root, file), file)
    zipf.close()

    print(f'{file_name} created')

def delete_geojsons(save_path):
    for root, dirs, files in os.walk(save_path):
        for file in files:
            if file.endswith('.geojson'):
                os.remove(os.path.join(root, file))
    
    print('Geojson files deleted')
