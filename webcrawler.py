from bs4 import BeautifulSoup
import requests

class InvalidRequestException(Exception):
    status_code = str()

    def __init__(self, status_code):
        self.status_code = status_code
    
    def __str__(self) -> str:
        return f'Invalid request: {self.status_code}'

class Publication:
    pmid = str()
    title = str()
    authors = str()
    abstract = str()
    date = str()
    
    def __str__(self):
        return f'{self.pmid}, {self.title}, {self.authors}, {self.abstract}, \
{self.date}'

def pubmed_crawl(query: str) -> list[Publication]:
    # process it so that it can be used with PubMed
    query.replace(' ', '+')

    base = 'https://pubmed.ncbi.nlm.nih.gov/'
    search = '?term='

    # TODO: Add ability to collect papers from multiple pages

    # search and get response
    response = requests.get(base + search + query)
    if response.status_code != 200:
        raise InvalidRequestException(response.status_code)
    
    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # get content
    results = soup.find_all('div', { 'class': 'docsum-content' })

    publications = []
    for result in results:
        publication = Publication()
        a_tag = result.find('a')
        publication.pmid = a_tag['href'].replace('/','')
        publication.title = a_tag.text.strip()
        publication.authors = result.find_all(
            'span', { 'class': 'docsum-authors full-authors' }
        )[0].text.strip()
        citation = result.find_all(
            'span', { 'class': 'docsum-journal-citation full-journal-citation' }
        )[0].text.strip()
        publication.date = citation[citation.find('.') + 2:citation.find(';')]

        paper_response = requests.get(base + publication.pmid)
        if paper_response.status_code != 200:
            raise InvalidRequestException(paper_response.status_code)

        paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
        publication.abstract = paper_soup.find_all(
            'div', { 'class': 'abstract-content selected' }
        )[0].find('p').text.strip()

        publications.append(publication) 
    
    return publications
