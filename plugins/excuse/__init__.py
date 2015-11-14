from bs4 import BeautifulSoup
import requests

helptext = "Gives a lazy developer excuse"

def do(args, coriolis=None):
    r = requests.get("http://developerexcuses.com")
    soup = BeautifulSoup(r.text, 'html.parser')
    return str(soup.find_all('a')[0].get_text())
