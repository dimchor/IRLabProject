from bs4 import BeautifulSoup
import requests
import enum

class InvalidRequestException(Exception):
    status_code = str()

    def __init__(self, status_code):
        self.status_code = status_code
    
    def __str__(self) -> str:
        return f'Invalid request: {self.status_code}'
    
class InvalidPageNumberException(Exception):
    pass

class Publication:
    pmid = str()
    title = str()
    authors = str()
    abstract = str()
    date = str()
    
    def __str__(self):
        return f'{self.pmid}, {self.title}, {self.authors}, {self.abstract}, \
{self.date}'

class PubMed:
    class ResultsPerPage(enum.Enum):
        ten = 10
        twenty = 20
        fifty = 50
        onehundred = 100
        twohundred = 200

    @staticmethod
    def crawl(query: str, pages_n: int = 1) -> list[Publication]:
        # check if the page number is valid, because pubmed may display up to 
        # 10'000 results

        # process it so that it can be used with PubMed
        query.replace(' ', '+')

        base = 'https://pubmed.ncbi.nlm.nih.gov/'
        search = '?term='
        page = '&page='
        size = '&size='

        publications = []
        for i in range(1, pages_n + 1):
        # search and get response
            response = requests.get(base + search + query + page + str(i))
            if response.status_code != 200:
                raise InvalidRequestException(response.status_code)
            
            # parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # get content
            results = soup.find_all('div', { 'class': 'docsum-content' })

            for result in results:
                publication = Publication()
                a_tag = result.find('a')
                publication.pmid = a_tag['href'].replace('/','')
                publication.title = a_tag.text.strip()
                publication.authors = result.find_all(
                    'span', { 'class': 'docsum-authors full-authors' }
                )[0].text.strip()
                citation = result.find_all(
                    'span', { 'class': 
                            'docsum-journal-citation full-journal-citation' }
                )[0].text.strip()
                publication.date = citation[citation.find('.') + 2:
                                            citation.find(';')]

                paper_response = requests.get(base + publication.pmid)
                if paper_response.status_code != 200:
                    raise InvalidRequestException(paper_response.status_code)

                paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
                publication.abstract = paper_soup.find_all(
                    'div', { 'class': 'abstract-content selected' }
                )[0].find('p').text.strip()

                publications.append(publication) 
        
        return publications
