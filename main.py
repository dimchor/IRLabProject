import webcrawler

def main():
    
    # TODO: add proper input handling from a web server (flask)

    try:
        publications = webcrawler.pubmed_crawl('covid')
        for publication in publications:
            print(publication)
    except webcrawler.InvalidRequestException as e:
        print(e)


if __name__ == "__main__":
    main()

