# server.py

import threading
import webbrowser
import http.server
import http.server
from model import * # from ./model.py
import urllib.parse as urlparse
import urllib
import http.client
import requests
import ssl

# Globals
FILE = './frontend.html'
PORT = 8080

server_classifier = Model()

def test_model(params):
    """ Handle /testModel """

    print("Testing model accuracy!")

    accuracy = server_classifier.test()
    return accuracy

def classify_post(params):
    """ Handle /classifyPost """

    print("Classifying post!")

    title = urllib.parse.unquote(params["title"][0])
    domain = urllib.parse.unquote(params["domain"][0])
    url = unshorten_url(urllib.parse.unquote(params["url"][0]))

    print("title = '" + title + "'")
    print("domain = '" + domain + "'")
    print("url = '" + url + "'")

    credibility = server_classifier.classify(title, url, domain)

    return credibility

def feed_post(params):
    """ Handle /feedPost """

    print("Feeding post to model!")

    title = urllib.parse.unquote(params["title"][0])
    domain = urllib.parse.unquote(params["domain"][0])
    url = unshorten_url(urllib.parse.unquote(params["url"][0]))
    y = params["y"][0]
    user_id = params["user_id"][0];

    # Debug output
    print("title = '" + title + "'")
    print("domain = '" + domain + "'")
    print("url = '" + url + "'")
    print("y = '" + y + "'")
    print("user_id = '" + user_id + "'")

    # Add data to server
    # TODO: Incorporate user_id into classifier somehow
    server_classifier.add_data(title, y, url, domain, user_id)

    return "Success!";

# TODO account for redirect page
def unshorten_url(url):

    # Parse URL from Facebook URL
    params = urlparse.parse_qs(urlparse.urlparse(url).query)
    orig_url = urllib.parse.unquote(params["u"][0])

    # Get redirected URL
    r = requests.head(orig_url, allow_redirects=True)
    return r.url

    parsed = urlparse.urlparse(url)
    h = http.client.HTTPConnection(parsed.netloc)
    h.request('HEAD', parsed.path)
    response = h.getresponse()

    if response.status/100 == 3 and response.getheader('Location'):
        return response.getheader('Location')
    else:
        return url

def serve_root():
    """ Return frontend interface (HTML) to user """

    with open(FILE, 'r') as f:
        file_string = f.read()
    return file_string

class APIHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP Handler for all API users, which is currently just the Google Chrome
    extension for Facebook
    """

    def strip_extra(self, arr):
        redux_arr = []
        for el in arr:
            if el == "0" or el == "1":
                redux_arr.append(el)

        return redux_arr

    def do_POST(self):
        """
        Handle a POST request by parsing training example and feeding
        into model
        """

        path = self.path
        api = path.split("?")[0];
        print("API = " + str(api))

        # Get params
        params = urlparse.parse_qs(urlparse.urlparse(path).query)

        # Call API: classifyPost, feedPost, testModel
        response = None
        if api == "/":
            response = serve_root()
        elif api == "/classifyPost":
            response = classify_post(params)
        elif api == "/feedPost":
            response = feed_post(params)
        elif api == "/testModel":
            response = test_model(params)
        else:
            response = "error" # Done fucked up

        # Train on data data
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()

        # Write response to client
        response_bytes = str.encode(response) # bytes
        self.wfile.write(response_bytes)
        print("Response = '" + str(response) + "'")
        print();

def open_browser():
    """ Start a browser after waiting for half a second. """

    def _open_browser():
        webbrowser.open('http://localhost:%s/%s' % (PORT, FILE))
    thread = threading.Timer(0.5, _open_browser)
    thread.start()

def start_server():
    """ Start the server. """

    server_address = ("", PORT)
    server = http.server.HTTPServer(server_address, APIHandler)
    # Add HTTPS certificate
    #server.socket = ssl.wrap_socket(server.socket, certfile="./server.pem", server_side=True)
    server.serve_forever()

if __name__ == "__main__":
    #open_browser()
    start_server()
