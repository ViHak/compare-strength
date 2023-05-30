from flask import Flask, request, jsonify, render_template, url_for
import sqlite3 as sql
from percentile import *

app = Flask(__name__)

@app.route('/', methods =["GET", "POST"])
def index():
    return render_template('index.html')

@app.route('/get_percentile')
def get_percentile():
    bw = int(request.args.get('val1'))
    bench = int(request.args.get('val2'))
    
    name = (request.args.get('name'))
    score = percentile_of_score(bw, bench, name)
    
    return jsonify({"result":score})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    


