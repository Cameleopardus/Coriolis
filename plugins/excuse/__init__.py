from bs4 import BeautifulSoup
import requests

helptext = "Gives a lazy developer excuse"

def do(args, pipe=None):
    r = requests.get("http://developerexcuses.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find_all('a')[0].get_text()
