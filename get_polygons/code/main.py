"""
Main script
"""

# Get packages
from custom_funcs import (start_scraper, get_countries,
    get_cities, clean_country_names,
    clean_city_names, get_lat_lons, write_geojson,
    save_dn_download, compile_zip, delete_geojsons)

def main():
    """ Main function """

    save_path = '../output/'
    url       = "https://www.uber.com/global/en/cities"

    soup      = start_scraper(url)
    countries = get_countries(soup)

    dn_download = []

    for country in countries:
        countries = get_countries(soup)
        cities    = get_cities(soup, country)
        country_name, country_name_short = clean_country_names(country)

        for city in cities:
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
                write_geojson(geojson, country_name_short, 
                                city_name_short, save_path)
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
