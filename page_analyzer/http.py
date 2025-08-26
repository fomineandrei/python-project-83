import requests
from bs4 import BeautifulSoup


class Http():
    def __init__(self, url):
        self.url = url
        self.response = None
        self.parsed_html = None

    def get_response(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.response = response
            return self
        except Exception:
            return None

    def html_parse(self):
        html = self.response.text
        self.parsed_html = BeautifulSoup(html, 'html.parser')

    def get_status_code(self):
        return self.response.status_code

    def get_h1(self):
        h1 = self.parsed_html.find('h1')
        if h1:
            return h1.get_text()
            
    def get_title(self):
        title = self.parsed_html.title
        if title:
            return title.get_text()
        
    def get_description(self):
        all_meta = self.parsed_html.find_all('meta')
        for meta in all_meta:
            if meta.get('name') == 'description':
                return meta.get('content')
        else:
            return None


def get_http_response(url, client=Http):
    http_client = client(url)
    response = http_client.get_response()
    if not response:
        return {'status_code': None}
    response.html_parse()
    return {
        'status_code': response.get_status_code(),
        'h1': response.get_h1(),
        'title': response.get_title(),
        'description': response.get_description()
    }
    

