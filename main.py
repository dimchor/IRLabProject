import webcrawler

def main():
    
    # TODO: add proper input handling from a web server (flask)

    try:
        publications = webcrawler.PubMed.crawl('covid')
        for publication in publications:
            print(publication)
        print(f'Number of results: {len(publications)}')
    except webcrawler.InvalidRequestException as e:
        print(e)


if __name__ == "__main__":
    main()

