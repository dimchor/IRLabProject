import webcrawler
from textprocessing import TextProcessing
from index import InvertedIndex
import boolean
import time
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import logic

app = Flask(__name__)
CORS(app)

# temporary functions

def get_sample_data():
    try:
        publications = webcrawler.PubMed.crawl('covid')
        webcrawler.Publication.export_publications(
            f'data/data-{int(time.time())}.json', publications)
    except webcrawler.InvalidRequestException as e:
        print(e)

def process_publications(
        publications: list[webcrawler.Publication]) -> list[list[str]]:
    processed_publications = []
    for publication in publications:
        processed_publication = []
        tokens = TextProcessing.tokenize(str(publication).lower())
        for token in tokens:
            if TextProcessing.is_special(token) or \
                TextProcessing.is_stopword(token):
                continue
            processed_publication.append(TextProcessing.stem(token))
        processed_publications.append(processed_publication)
    return processed_publications

def print_tokens(tokens: list[boolean.Token]) -> None:
    for token in tokens:
        print(token.value, end='')
    print("")

def test():
    
    # TODO: add proper input handling from a web server (flask)

    # get_sample_data()

    # process data

    # TODO: improve JSON parsing 

    
    publications = webcrawler.Publication.import_publications(
        'data/data-1704454765.json')


    processed_publications = process_publications(publications)

    inverted_index = InvertedIndex(processed_publications)

    #print(inverted_index.contains('heart'))
    #print(inverted_index.idf('covid'))
    
    query = '"covid-19" & ! ("heart" | "covid")'
    #test = '!("A" | ("B" & !"C")) & "D" | !("F" & ("H" | !"G"))'
    try:
        print(boolean.search(query, inverted_index))

    except Exception as e:
        print(e)

    pass

@app.route('/get_data/<query>/<filename>', methods=['GET'])
def get_data(query: str, filename: str) -> dict:
    try:
        logic.get_data(query, filename)
        return {"success": filename}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

def main():
    TextProcessing.download_dependencies()
    app.run(debug=True)

if __name__ == "__main__":
    main()

