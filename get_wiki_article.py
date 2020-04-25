from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
# Webpage the image is on
API_URL1 = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles="
API_URL2 = "&formatversion=2&rvprop=content&rvslots=*"
gui_input_string = input("Enter article name: ")
my_page = API_URL1+gui_input_string+API_URL2;
try:
	req = Request(my_page, headers={'User-Agent': 'Mozilla/5.0'})
	html = urlopen(req)
	soup = BeautifulSoup(html.read(), 'html.parser')
	print(soup)
except:
	print("try again")