import webcrawler
from textprocessing import TextProcessing
from index import InvertedIndex
import boolean
import time
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import logic
import os
import json

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
        'data/d1705744190618.json')


    processed_publications = process_publications(publications, 'stem')

    inverted_index = InvertedIndex(processed_publications)

    #print(inverted_index.contains('heart'))
    #print(inverted_index.idf('covid'))
    
    #query = '"covid-19" & ! ("heart" | "covid")'
    #query = '!"," | !"!" & (!"syndrome," & "and" | !"or" | (!"seven" | "#"))'
    #query = '!((("ey" & "yu")))'
    query = '!"multiple words" & "also here"'
    #query = '!"multiple words" & "also here2"'
    #query = '!("A" | ("B" & !"C")) & "D" | !("F" & ("H" | !"G"))'
    #try:
    #print(boolean.search(query, inverted_index, TextProcessing.lemmatize))
    tokens = boolean.Lexer(query).tokenize()
    boolean.check_syntax(tokens)

    tokens = boolean.DeMorgan(tokens).convert()

    tokens = boolean.Normalizer(tokens).apply(TextProcessing.stem)

    print_tokens(tokens)
    #except Exception as e:
        #print(e)

    pass


def process_publications(
        publications: list[webcrawler.Publication], 
        method: str) -> list[list[str]]:
    processed_publications = []
    for publication in publications:
        processed_publication = []
        tokens = TextProcessing.tokenize(str(publication).lower())
        for token in tokens:
            if TextProcessing.is_special(token) or \
                TextProcessing.is_stopword(token):
                continue

            processed_token = None
            if method == 'stem':
                processed_token = TextProcessing.stem(token)
            elif method == 'lem':
                processed_token = TextProcessing.lemmatize(token)
            processed_publication.append(processed_token)
        processed_publications.append(processed_publication)
    return processed_publications

@app.route('/get_data/<query>/<filename>/<pages>/<rpp>', methods=['GET'])
def get_data(query: str, filename: str, pages: str, rpp: str) -> dict:
    rpp_enum = None
    match rpp:
        case '10':
            rpp_enum = webcrawler.PubMed.ResultsPerPage.TEN
        case '20':
            rpp_enum = webcrawler.PubMed.ResultsPerPage.TWENTY
        case '50':
            rpp_enum = webcrawler.PubMed.ResultsPerPage.FIFTY
        case '100':
            rpp_enum = webcrawler.PubMed.ResultsPerPage.ONEHUNDRED
        case '200':
            rpp_enum = webcrawler.PubMed.ResultsPerPage.TWOHUNDRED
        case _:
            pass
    try:
        pages_n = int(pages)
        if pages_n < 1:
            raise Exception('Invalid page number (it must be >= 1)')
                
        logic.get_data(query, filename, int(pages), rpp_enum)
        return {"success": filename + '.json'}
    except Exception as e:
        return {"error": str(e)}

@app.route('/get_files', methods=['GET'])
def get_files():
    PATH = 'data/'
    files = [file for file in os.listdir(PATH) if os.path.isfile(PATH + file)]
    return jsonify(files)

@app.route('/search/<dataset>/<algorithm>/<textproc>/<where>/<query>')
def search(dataset: str, algorithm: str, textproc: str, where: str, query: str):
    publications = webcrawler.Publication.import_publications('data/' + dataset)
    
    process_token = None
    if textproc == 'stem':
        process_token = TextProcessing.stem
    elif textproc == 'lem':
        process_token = TextProcessing.lemmatize

    get_content = None
    match where:
        case'all':
            get_content = lambda publication: str(publication)
        case 'title':
            get_content = lambda publication: publication.title
        case 'authors':
            get_content = lambda publication: "".join(
                author + ' ' for author in publication.authors)
        case 'abstract':
            get_content = lambda publication: publication.abstract
        case 'date':
            get_content = lambda publication: publication.date
        case _:
            pass

    processed_publications = []
    for publication in publications:
        processed_publication = []
        tokens = TextProcessing.tokenize(get_content(publication).lower())
        for token in tokens:
            if TextProcessing.is_special(token) or \
                TextProcessing.is_stopword(token):
                continue
            processed_publication.append(process_token(token))
        processed_publications.append(processed_publication)

    inverted_index = InvertedIndex(processed_publications)

    publication_set = None
    match algorithm:
        case 'boolean':
            try:
                publication_set = boolean.search(query, inverted_index, 
                                                 process_token)
            except Exception as e:
                return {"error": str(e)}
        case _:
            pass

    selected_publications = []
    for i in range(len(publications)):
        if i in publication_set:
            publications[i].abstract = publications[i].abstract[0:240] + ' [...]'
            selected_publications.append(publications[i])
    
    json_str = '['
    for i in range(len(selected_publications)):
        json_str += json.dumps(selected_publications[i].__dict__)
        if i < len(selected_publications) - 1:
            json_str += ','
    json_str += ']'
    return json_str

@app.route('/')
def index():
    return render_template('index.html')

def main():
    TextProcessing.download_dependencies()
    app.run(debug=True)
    #test()

if __name__ == "__main__":
    main()

