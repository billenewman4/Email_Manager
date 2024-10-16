import os
import logging
from flask import Flask, request, jsonify
from url_finder import url_finder
from web_scrapper import web_scrapper

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    query = data.get('query')
    app.logger.info(f"Received query: {query}")
    
    try:
        links = url_finder(query)
        app.logger.info(f"Found links: {links}")
        
        if links:
            # Process only the first link
            first_link = links[0]
            app.logger.info(f"Processing first link: {first_link}")
            result = web_scrapper(first_link)
            app.logger.info(f"Scraping result: {result}")
        else:
            result = None
            app.logger.warning("No links found to scrape")
        
        return jsonify({'links': links, 'result': result})
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
