# Get packages

import os
from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import zipfile

save_path = '../output/'

# Set main link

url  = "https://www.uber.com/global/en/cities/"
html = Request(url)
html.add_header(
    'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
html.add_header(
    'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
resp     = urlopen(html)
raw_html = resp.read()
soup     = BeautifulSoup(raw_html, 'html.parser')

# Get countries

country_class = soup.find('div', text = 'Argentina').previous_element.previous_element['class'] 
country_class = ' '.join([str(item) for item in country_class])
countries     = soup.find_all('div', class_ = country_class)

# Get all city polygons

dn_download = []

for jj, country in enumerate(countries):
    # Set country page and name
        
    # Both the country and the city class could be defined outside of the loop,
    # but Uber changes the class names frequently, so there is a small risk of
    # the code breaking if the class names change mid-way through the loop.
    
    country_class      = soup.find('div', text = 'Argentina').previous_element.previous_element['class']
    country_class      = ' '.join([str(item) for item in country_class])
    countries          = soup.find_all('div', class_ = country_class)
    country_name       = country.find('h3').get_text()
    country_name_short = re.sub("\\.", "", country_name)
    country_name_short = re.sub("[^0-9a-zA-Z]+", "_", country_name_short).lower()

    # Set cities page
    city_class = soup.find('div', text='Buenos Aires')['class'] 
    city_class = ' '.join([item for item in city_class]) 
    cities     = country.find_all('div', class_ = city_class) 
    
    for ii, city in enumerate(cities):

        # Set city page and name
        city_name       = city.get_text()
        city_name_short = re.sub("\\.", "", city_name)
        city_name_short = re.sub("[^0-9a-zA-Z]+", "_", city_name_short).lower()
        city_link       = city.find('a')['href']

        # Set city polygons page
        uber_html = Request(city_link)
        uber_html.add_header(
            'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
        uber_html.add_header(
            'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')

        try:
            uber_resp     = urlopen(uber_html)
            uber_raw_html = uber_resp.read()

            text = str(BeautifulSoup(uber_raw_html))
            text = text[text.index('geoJson'):]
            text = text.replace('geoJson\\u0022:', '')
            text = text[:text.index('},\\u0022defaultMapLat')]

            # Remove the coordinate labels
            text = text.replace('\\u0022lat\\u0022:', '')
            text = text.replace('\\u0022lng\\u0022:', '')
            text = text.split('],[')
            text = [x.replace('{', '[').replace('}', ']') for x in text]
            text = [x.split('],[') for x in text]

            # Swap lats and lons
            for j, v in enumerate(text):
                for i, c in enumerate(v):
                    lat_long = c.replace('[', '').replace(']', '')
                    lat_long = lat_long.split(',')
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
            
            if len(text) == 1:
                print(f'{country_name} {city_name}  is not a polygon')
                continue

            # Write out geojson
            file_name = f'{country_name_short}-{city_name_short}.geojson'
            file_name = os.path.join(save_path, file_name)
            file      = open(file_name, 'w')
            file.write(geojson)
            file.close()
            print(f'{country_name}, {city_name}')

        except:
            dn_download.append(f'{country_name}, {city_name}')
            print(f'{country_name}, {city_name} couldn\'t be downloaded\n')

# Save list of cities that couldn't be downloaded
file_name = 'dn_download.txt'
file      = os.path.join(save_path, file_name)
file1     = open(file, 'w')
file1.write(''.join(dn_download))
file1.close()

# Put all geojsons in one zip file

file_name = 'geojson_files.zip'
file      = os.path.join(save_path, file_name)
zipf      = zipfile.ZipFile(file, 'w')

for root, dirs, files in os.walk(save_path):
    for file in files:
        if file.endswith('.geojson'):
            zipf.write(os.path.join(root, file), file)

zipf.close()

# Delete all geojson files in the save path
for root, dirs, files in os.walk(save_path):
    for file in files:
        if file.endswith('.geojson'):
            os.remove(os.path.join(root, file))
