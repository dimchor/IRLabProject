from bs4 import BeautifulSoup
import requests

class Publication:
    title = str()
    authors = str()
    abstract = str()
    date = str()
    
    def __str__(self):
        return f"{self.title}, {self.authors}, {self.abstract}, {self.date}"

def pubmed_crawl(query: str) -> list[Publication]:
    #query = 'covid'

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
        publication = Publication()
        publication.title = result.find('a').text.strip()
        
        print(publication)
        # authors =
        # ...
        publications.append(publication) 
    
    return publications
