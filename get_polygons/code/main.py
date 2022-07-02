# Get packages
from custom_funcs import *

def main():
    save_path = '../output/'

    url  = "https://www.uber.com/global/en/cities"
    soup = start_scraper(url)
    countries = get_countries(soup)
    
    dn_download = []

    for jj, country in enumerate(countries):
        countries = get_countries(soup)
        cities    = get_cities(soup, country)
        country_name, country_name_short = clean_country_names(country)

        for ii, city in enumerate(cities):
            city_name, city_name_short, city_link = clean_city_names(city)
            try:
                text = str(start_scraper(city_link))
                geojson, text = get_lat_lons(text, country_name_short,
                                       city_name_short, 
                                       country_name, city_name)
                            
                if len(text) == 1:
                    dn_download.append(f'{country_name}, {city_name}')
                    print(f'{country_name}, {city_name} is not a polygon')
                    continue

                # Write out geojson
                write_geojson(geojson, country_name_short, city_name_short, save_path)
                print(f'{country_name}, {city_name} downloaded')
            except: 
                dn_download.append(f'{country_name}, {city_name}')
                print(f'{country_name}, {city_name} couldn\'t be downloaded')

    save_dn_download(dn_download, save_path)
    compile_zip(save_path)
    delete_geojsons(save_path)
    print('Done!')

if __name__ == '__main__':
    main()
