import logic
from flask import Flask, request

app = Flask(__name__)

@app.route('/get_data/<query>/<filename>', methods=['GET'])
def get_data(query: str, filename: str):
    try:
        logic.get_data(query, filename)
        return filename
    except Exception as e:
        return str(e)

