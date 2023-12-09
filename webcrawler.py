from bs4 import BeautifulSoup
import requests
import enum

class InvalidRequestException(Exception):
    status_code: str

    def __init__(self, status_code):
        self.status_code = status_code
    
    @classmethod
    def __str__(self) -> str:
        return f'Invalid request: {self.status_code}'
    
class InvalidResultsNumberException(Exception):
    results_asked: int
    results_limit: int

    def __init__(self, results_asked, results_exprected):
        self.results_asked = results_asked
        self.results_limit = results_exprected

    @classmethod
    def __str__(self) -> str:
        return f'You asked for {self.results_asked} results but I can only give\
 you up to {self.results_limit} :/'

class InvalidPageNumberException(Exception):
    error: str

    def __init__(self, error):
        self.error = error
    
    def __str__(self):
        return f'page number error: {self.error}'

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
    class ResultsPerPage(enum.IntEnum):
        ten = 10
        twenty = 20
        fifty = 50
        onehundred = 100
        twohundred = 200

    @staticmethod
    def parse_field(input:str, field: str, start: int) -> (str, int):
        OFFSET = 6
        NEW_LINE = '\r\n'
        NEW_LINE_LEN = 2

        ret = str()
        first_index = input.find(field, start)
        if first_index == -1:
            return '', first_index
        else:
            first_index += OFFSET
        while True:
            second_index = input.find(NEW_LINE, first_index)
            ret += input[first_index:second_index]
            if input[second_index + NEW_LINE_LEN] != ' ':
                return ret, second_index + NEW_LINE_LEN
            else:
                first_index = second_index + NEW_LINE_LEN + OFFSET

    @staticmethod
    def crawl(query: str, pages_n: int = 1, 
              rpp: ResultsPerPage = ResultsPerPage.ten) -> list[Publication]:
        # check if the page number is valid, because pubmed may display up to 
        # 10'000 results
        LIMIT = 10000
        if (pages_n < 0):
            raise InvalidPageNumberException(
                'Negative numbers are not accepted!')
        elif (pages_n * rpp > LIMIT):
            raise InvalidResultsNumberException(pages_n * rpp, LIMIT)

        # process it so that it can be used with PubMed
        query.replace(' ', '+')

        BASE = 'https://pubmed.ncbi.nlm.nih.gov/'
        SEARCH = '?term='
        PAGE = '&page='
        SIZE = '&size='
        FORMAT = '&format=pubmed'

        publications = []

        for page in range(1, pages_n + 1):
            response = requests.get(BASE + SEARCH + query + PAGE + str(page) + 
                                    SIZE + str(rpp) + FORMAT)
            if response.status_code != 200:
                raise InvalidRequestException(response.status_code)
            
            # parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # get content
            results: str = soup.find('pre').text
            
            results = results.split('\r\n\r\n') # why pubmed, why

            for r in results:
                last_index = 0

                publication = Publication()

                publication.pmid, last_index = PubMed.parse_field(
                    r, 'PMID', last_index)

                publication.date, last_index = PubMed.parse_field(
                    r, 'DP', last_index)
                
                publication.title, last_index = PubMed.parse_field(
                    r, 'TI', last_index)
                
                publication.abstract, last_index = PubMed.parse_field(
                    r, 'AB', last_index)
                
                while True:
                    authors_part, last_index = PubMed.parse_field(
                        r, 'FAU', last_index)
                    publication.authors += authors_part
                    if last_index == -1:
                        break
                
                publications.append(publication)

        return publications
