#!/usr/bin/env python3

import urllib.parse
import urllib.request
import re
import logging
import signal
import sys

visited_urls = set()  # Keep track of visited URLs to avoid revisiting

def crawl(url, path=None, domain_check=False, initial_domain=None):
    # Check if the URL has already been visited
    if url in visited_urls:
        return

    # Add the URL to the set of visited URLs
    visited_urls.add(url)

    # Create a new path list if it's not provided
    if path is None:
        path = []

    # Add the current URL to the path
    path.append(url)

    try:
        # Make a GET request to the URL
        response = urllib.request.urlopen(url)

        # Check if the request was successful
        if response.status == 200:
            # Read the HTML content
            html_content = response.read().decode('utf-8')

            # Find all anchor tags (links) in the HTML
            pattern = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"'
            urls = re.findall(pattern, html_content)

            # Print the found URLs and their paths
            for new_url in urls:
                log_message = f'[INFO] URL: {new_url} | Path: {path}'

                # Check if domain_check is enabled and compare domains
                if domain_check and initial_domain:
                    parsed_url = urllib.parse.urlparse(new_url)
                    if parsed_url.netloc != initial_domain:
                        continue

                logging.info(log_message)
                # Visit the new URL recursively
                crawl(new_url, path.copy(), domain_check, initial_domain)
        else:
            log_message = f'[ERROR] Failed to retrieve the webpage: {url}'
            logging.error(log_message)
    except urllib.error.HTTPError as e:
        log_message = f'[ERROR] HTTP Error {e.code}: {e.reason} - URL: {url}'
        logging.error(log_message)
    except urllib.error.URLError as e:
        log_message = f'[ERROR] URL Error: {e.reason} - URL: {url}'
        logging.error(log_message)
    except Exception as e:
        log_message = f'[ERROR] An error occurred: {str(e)} - URL: {url}'
        logging.error(log_message)

def signal_handler(signal, frame):
    # Close the log file when Ctrl+C is pressed
    logging.shutdown()
    sys.exit(0)

# Set up logging to both stdout and a log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crawler.log')
    ]
)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Example usage
url = input('Enter a URL: ')
domain_check = input('Enable same domain check? (y/n): ').lower() == 'y'

if domain_check:
    parsed_url = urllib.parse.urlparse(url)
    initial_domain = parsed_url.netloc
else:
    initial_domain = None

crawl(url, domain_check=domain_check, initial_domain=initial_domain)

