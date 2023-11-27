from bs4 import BeautifulSoup
import requests

class Publication:
    def __init__(self, title, authors, abstract, date):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.date = date

    def __str__(self):
        return f"{self.title}, {self.authors}, {self.abstract}, {self.date}"

# TODO: add proper input handling from a web server (flask)
# same input
query = 'covid'

# process it so that it can be used with PubMed
query.replace(' ', '+')

# search and get response
response = requests.get('https://pubmed.ncbi.nlm.nih.gov/?term=' + query)

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# get content
results = soup.find_all("div", { "class": "docsum-content" })


publications = []
for result in results:
    title = result.find('a').text.strip()
    print(title)
    # authors =
    # ... 
    
#print(results[0])
