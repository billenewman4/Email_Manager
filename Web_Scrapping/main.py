from url_finder import url_finder
from web_scrapper import web_scrapper

links = url_finder("Architectural Aluminum Techniques")
print(links)
print(web_scrapper(links[0]))