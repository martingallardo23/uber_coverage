# Get packages

import os
from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import zipfile

save_path = '../output/'

# Set main link

url = "https://www.uber.com/global/en/cities/"
html = Request(url)
html.add_header(
    'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
html.add_header(
    'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
resp = urlopen(html)
raw_html = resp.read()
soup = BeautifulSoup(raw_html, 'html.parser')

# Get countries

country_class = soup.find('div', text = 'Argentina').previous_element.previous_element['class'] 
country_class = ' '.join([str(item) for item in country_class])
countries = soup.find_all('div', class_ = country_class)

# Get all city polygons

dn_download = []

for jj in range(len(countries)):
    # Set country page and name
        
    # Both the country and the city class could be found outside of the loop,
    # but Uber changes the class names frequently, so there is a small risk of
    # the code to break if the class names change mid-way through the loop.
    
    country_class = soup.find('div', text = 'Argentina').previous_element.previous_element['class']
    country_class = ' '.join([str(item) for item in country_class])
    countries = soup.find_all('div', class_ = country_class)
    country = countries[jj]
    country_name = country.find('h3').get_text()
    country_name_short = re.sub("\\.", "", country_name)
    country_name_short = re.sub("[^0-9a-zA-Z]+", "_", country_name_short).lower()

    # Set cities page
    city_class = soup.find('div', text='Buenos Aires')['class'] 
    city_class = ' '.join([item for item in city_class]) 
    cities = country.find_all('div', class_ = city_class) 
    
    for ii in range(len(cities)):

        # Set city page and name
        city = cities[ii]
        city_name = city.get_text()
        city_name_short = re.sub("\\.", "", city_name)
        city_name_short = re.sub("[^0-9a-zA-Z]+", "_", city_name_short).lower()
        city_link = city.find('a')['href']

        # Set city polygons page
        uber_html = Request(city_link)
        uber_html.add_header(
            'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
        uber_html.add_header(
            'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')

        try:
            uber_resp = urlopen(uber_html)
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
            for j in range(len(text)):
                for i in range(len(text[j])):
                    text[j][i] = text[j][i].replace('[', '').replace(']', '')
                    text[j][i] = text[j][i].split(',')
                    text[j][i][0], text[j][i][1] = text[j][i][1], text[j][i][0]
                    text[j][i] = '[' + ','.join(text[j][i]) + ']'
                text[j] = '[[' + ','.join(text[j]) + ']]'

            # Build geojson
            geojson = '{ "type": "Feature", "properties": { }, "geometry": { "type": "Polygon", "coordinates":'

            properties = '{ "name": "' + country_name_short + '_' + city_name_short + '", "country": "' + country_name + '", "city": "' + city_name + '" }'

            # Write geojson
            for i in range(len(text)):
                text[i] = geojson + text[i] + '}' + ', "properties":' + properties +'}\n'
            
            text = ',\n'.join(poly for poly in text)
            geojson = '{ "type": "FeatureCollection", "features": [\n' + text + ']\n}\n'
            
            if len(text) == 1:
                print(country_name + city_name + ' is not a polygon')
                continue

            # Write out geojson
            file_name = country_name_short + '-' + city_name_short + '.geojson'
            file = os.path.join(save_path, file_name)
            file1 = open(file, 'w')
            file1.write(geojson)
            file1.close()
            print(country_name + ', ' + city_name)

        except:
            dn_download.append(country_name + ', ' + city_name)
            print(country_name + ', ' + city_name + " couldn't be downloaded")

# Save list of cities that couldn't be downloaded
file_name = 'dn_download.txt'
file = os.path.join(save_path, file_name)
file1 = open(file, 'w')
file1.write('\n'.join(dn_download))
file1.close()

# Put all geojsons in one zip file

file_name = 'geojson_files.zip'
file = os.path.join(save_path, file_name)
zipf = zipfile.ZipFile(file, 'w')

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
