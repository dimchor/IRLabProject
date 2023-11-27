from bs4 import BeautifulSoup
import requests

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

print(results)
