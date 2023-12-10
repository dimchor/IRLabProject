import webcrawler
import json
import datetime

def main():
    
    # TODO: add proper input handling from a web server (flask)

    try:
        publications = webcrawler.PubMed.crawl('covid')
        json_str = json.dumps([p.__dict__ for p in publications])
        f = open(f'/data/data-{datetime.datetime.now()}.json', 'wt')
        f.write(json_str)
        f.close()
    except webcrawler.InvalidRequestException as e:
        print(e)


if __name__ == "__main__":
    main()

