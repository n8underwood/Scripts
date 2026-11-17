import parser
import http
import requests
import sys
import logger                                                                   # Implement

from bs4 import BeautifulSoup

def get_url_status(url: str | None) -> int:
    if url:
        try: 
            return requests.head(url, timeout=5).status_code
        except requests.RequestException:
            raise
    return False

def parse_url(url: str) -> dict[str, int]:
    try:
        response = requests.get(url)                                            # T/E
                                                                                # MissingSchema for invalid URL
                                                                                # Timeout, etc.

        # Soupify the response
        soup = BeautifulSoup(response.content, 'html.parser') 
                # T/E

        # Find all links
        domain = url
        status_codes = {}
        links = soup.find_all('a')
        
        for link in links:
            # Extract the url path from the link                                # T/E
            path = str(link.get('href'))    

            # Check if path is relative or absolute
            if path.startswith('https://'):
                url = path
            else:
                url = domain + path
            print(url)

            # Fetch the status code                                             # Test case: No href inside <a></a>
            status_codes[url] = get_url_status(url)                             # Develop test then modify code (shift left)

        return status_codes 
        
    except Exception as error:
        raise error

def main() -> int: 

    # Gather command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 url_checker.py url --destination")
        sys.exit()
    url = sys.argv[1]
    if len(sys.argv) == 3:
        destination = sys.argv[2]

    status_codes = parse_url(url)                                               # Let work with relative addresses too
                                                                                # Or raw HTML files
    # print(status_codes)
    for url, status in status_codes.items():
        print(f'{url}: {status}')
    
    return 0 

if __name__ == '__main__':
    main()