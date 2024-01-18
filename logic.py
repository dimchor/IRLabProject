import webcrawler

def get_data(query: str, filename: str) -> None:
    publications = webcrawler.PubMed.crawl(query)
    webcrawler.Publication.export_publications('data/' + filename + '.json', 
                                               publications)
