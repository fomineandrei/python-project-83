class FakeHttp:
    def __init__(self, url_test_data):
        self.status_code = url_test_data.status_code
        self.h1 = url_test_data.h1
        self.title = url_test_data.title
        self.description = url_test_data.description

    def get_response(self):
        if self.status_code:
            return self
        return None
    
    def html_parse(self):
        pass

    def get_status_code(self):
        return self.status_code

    def get_h1(self):
        return self.h1
            
    def get_title(self):
        return self.title
        
    def get_description(self):
        return self.description
