from webcrawler import PubMed, Publication

def get_data(query: str, filename: str, pages_n: int, 
             rpp: PubMed.ResultsPerPage) -> None:
    publications = PubMed.crawl(query, pages_n, rpp)
    Publication.export_publications('data/' + filename + '.json', 
                                               publications)
