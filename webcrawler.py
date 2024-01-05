from bs4 import BeautifulSoup
import requests
import enum
import json
import ijson

class InvalidRequestException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
    
    def __str__(self) -> str:
        return f'Invalid request: {self.status_code}'
    
class InvalidResultsNumberException(Exception):
    def __init__(self, results_asked, results_exprected):
        self.results_asked = results_asked
        self.results_limit = results_exprected

    def __str__(self) -> str:
        return f'You asked for {self.results_asked} results but I can only give\
 you up to {self.results_limit} :/'

class InvalidPageNumberException(Exception):
    def __init__(self, error):
        self.error = error
    
    def __str__(self):
        return f'page number error: {self.error}'

class Publication:
    def __init__(self):
        self.pmid = str()
        self.title = str()
        self.authors = []
        self.abstract = str()
        self.date = str()
    
    def __str__(self):
        return f'{self.pmid}, {self.title}, {self.authors}, {self.abstract}, \
{self.date}'
    
    @staticmethod
    def export_publications(filename: str, data: list):
        with open(filename, 'wt') as f:
            f.write('[')
            for i in range(len(data)):
                f.write(json.dumps(data[i].__dict__))
                if i < len(data) - 1:
                    f.write(', ')
            f.write(']')

    @staticmethod
    def import_publications(filename: str) -> list:
        publications = []
        with open(filename, 'rt') as f:
            content = ijson.items(f, 'item')
            for item in content:
                publication = Publication()
                publication.pmid = item['pmid']
                publication.title = item['title']
                publication.authors = item['authors']
                publication.abstract = item['abstract']
                publication.date = item['date']
                publications.append(publication)
        return publications


class PubMed:
    class ResultsPerPage(enum.IntEnum):
        TEN = 10
        TWENTY = 20
        FIFTY = 50
        ONEHUNDRED = 100
        TWOHUNDRED = 200

    @staticmethod
    def parse_field(input: str, field: str, start: int) -> (str, int):
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
            if second_index + NEW_LINE_LEN >= len(input) or \
                input[second_index + NEW_LINE_LEN] != ' ':
                return ret, second_index
            else:
                first_index = second_index + NEW_LINE_LEN + OFFSET

    @staticmethod
    def parse_field_n(input: str, field: str, start: int, end: int):
        whole = []
        inner_start = start
        while True:
            part, inner_start = PubMed.parse_field(input, field, inner_start)
            if inner_start > end or inner_start == -1:
                break
            else:
                start = inner_start
            whole.append(part)
        return whole, start

    @staticmethod
    def find_end(input: str, start: int) -> int:
        end = input.find('\r\n\r\n', start)
        if end == -1: # we've reached the end
            end = len(input) - 1
        return end

    @staticmethod
    def crawl(query: str, pages_n: int = 1, 
              rpp: ResultsPerPage = ResultsPerPage.TEN) -> list[Publication]:
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
            index = 0
            loop = True
            while loop:
                END = PubMed.find_end(results, index)
                if END == len(results) - 1: # we've reached the end
                    loop = False
                
                publication = Publication()

                publication.pmid, index = PubMed.parse_field(
                    results, 'PMID', index)

                publication.date, index = PubMed.parse_field(
                    results, 'DP', index)
                
                publication.title, index = PubMed.parse_field(
                    results, 'TI', index)
                
                publication.abstract, index = PubMed.parse_field(
                    results, 'AB', index)
                
                publication.authors, index = PubMed.parse_field_n(
                    results, 'FAU', index, END)

                publications.append(publication)
                index = END + 1

        return publications
