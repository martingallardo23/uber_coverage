# Visualizing Uber coverage worldwide
 - We scrape [Uber's website](https://www.uber.com/global/en/cities/) to get a unified Uber coverage shapefile, using Python and BeautifulSoup. 
 - We download 1142 out of the 1180 areas available on Uber's page, while 38 areas that appear on the list don't have polygons to be scraped. The 38 areas that appear on Uber's website are detailed in [this list](https://raw.githubusercontent.com/martingallardo23/uber_coverage/main/get_polygons/output/dn_download.txt).

- 📁 Ready to download files are:
  - [Individual geojson files for each city](https://github.com/martingallardo23/uber_coverage/blob/cfdc129b937e236363ccd4c2e150cd3bdf493646/get_polygons/output/geojson_files.zip) (in a .rar file)
  - [Unified shapefile with Uber's coverage worldwide](https://github.com/martingallardo23/uber_coverage/blob/cfdc129b937e236363ccd4c2e150cd3bdf493646/merge_polygons/output/uber_polygons.shp)
- 🗺️ A simple visualization using R Markdown and the `leaflet` package is [available here](https://martingallardo23.github.io/uber_coverage/leaflet/leaflet_uber.html).
