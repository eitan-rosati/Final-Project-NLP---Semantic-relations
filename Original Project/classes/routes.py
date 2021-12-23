"""
Final Project
Software engineering department
Authors:
Sapir Nahum
Shmuel Eliasyan
"""

"""
===================================================================================================
Imports
===================================================================================================
"""
from BackEnd.classes.Find_books import find_books
from BackEnd.classes.Word_list_reduction import Word_list_reduction
from BackEnd.classes.Normalize_marc_file import normalizeMarc
from BackEnd.classes.Elastic_search import elasticsearch
from BackEnd.classes.Expend_synonym_index import expend_synonym_index
from BackEnd.classes.Rate_books import rate_books
import os
from flask import Flask, flash, request, redirect, url_for, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from BackEnd.classes.Create_report import create_report
import json

UPLOAD_FOLDER = 'files/marc_files/'
ALLOWED_EXTENSIONS = {'xml', 'txt'}

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
rb = rate_books()
es = elasticsearch()
fb = find_books()
cr = create_report()
cors=CORS(app)

"""
===================================================================================================
Functions
===================================================================================================
"""


def allowed_file(filename):
    """
    the function receive a file and check if the type is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_file', methods=['POST', 'OPTIONS'])
def upload_file():
    """
    the function receive a file and insert it to the files directory
    """
    if request.method == 'OPTIONS':
        resp = Response(json.dumps("{ ok }"))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        return resp
    else:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    the function receive a file name from the files directory and normalize the file
    and upload the data to elasticsearch
    """
    data = normalizeMarc(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    record_list = data.records_list
    es.upload_dictionary(record_list, "create")
    expend_synonym_index(record_list)
    resp = Response(recordListToJson(record_list))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/mms_id")
def mms_id():
    """
    the function receive a book mms id and return the information about the book and a list of similar books
    """
    id = request.args.get('id', default="*", type=int)
    res, books_names = fb.find_books_by_book_id(id)
    names, rated = rb.get_books_by_rate(id, res, books_names)
    cr.create_report_excel(rated, str(id))

    resp = Response(mmsToJson(names, rated, id))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
    # except:
    #     return "id is invalid"


@app.route("/isbn")
def isbn():
    """
    the function receive a book isbn and return the information about the book and a list of similar books
    """
    try:
        isbn = request.args.get('id', default="*", type=str)
        id = es.get_book_by_isbn(isbn)
        res, books_names = fb.find_books_by_book_id(id)
        names, rated = rb.get_books_by_rate(id, res, books_names)
        cr.create_excel(rated, str(id))

        resp = Response(mmsToJson(names, rated, id))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except:
        return "id is invalid"


@app.route("/by_token")
def search_by_token():
    """
    the function receive a token and return a list of books with the token or other synonyms of the token
    """
    try:
        token = request.args.get('token', default="*", type=str)
        books = es.get_books_by_tokens(token)
        resp = Response(json.dumps(books))
        resp.headers['Access-Control-Allow-Origin'] = '*'

        return resp
    except:
        return "token is invalid"


@app.route("/reduce", methods=['POST'])
def reduce():
    """
    the function receive a list of words and return the list without synonyms in the list
    """
    new_list = {}
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        f = open(app.config['UPLOAD_FOLDER'] + file.filename, "r")
        list = f.read().split(",")
        temp_list = list.copy()
        reduce = Word_list_reduction()
        reduce.normalize_words_list_wordnet(list)
        new_list['original_list'] = temp_list
        new_list['reduced_list'] = list
        resp = Response(json.dumps(new_list))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    return "file not allowed"


@app.route("/expand")
def expand():
    """
    the function receive a token and return a list of synonyms of this token
    """
    new_list = {}
    token = request.args.get('token', default="*", type=str)
    fs = expend_synonym_index()
    list = fs.get_synonyms_list(token)
    new_list['original_token'] = token
    new_list['expended_list'] = list
    return json.dumps(new_list)


@app.route("/rnd_books")
def rnd_books():
    """
    the function return a list of 30 random books
    """
    new_list = es.get_random_books()
    resp = Response(json.dumps(new_list))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/review", methods=['OPTIONS'])
def check_review():

    resp = Response(json.dumps("{ ok }"))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp


@app.route("/review", methods=['POST'])
def add_review():
    content = request.json
    es.add_new_review(content)
    resp = Response(json.dumps("{ status: 200 }"))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.errorhandler(404)
def not_found(e):
    return "{}"


def recordListToJson(recordList):
    """
    the function receive books record and return it in json format
    """
    new_list = []
    for i in range(len(recordList)):
        item = {}
        item['mms_id'] = recordList[i][0]
        item['title'] = recordList[i][1]
        item['original_topics'] = recordList[i][2]
        item['reduced_topics'] = recordList[i][3]
        item['description'] = recordList[i][4]
        item['isbn'] = recordList[i][5]
        new_list.append(item)
    return json.dumps(new_list)


def mmsToJson(names, rated, id):
    """
        the function receive books record and the similar books and return it in json format
    """
    new_list = {}
    new_list['mms_id'] = id
    new_list['title'] = es.get_book_title(id)
    new_list['description'] = es.get_book_description(id)
    new_list['original_topics'] = es.get_book_original_topics(id)
    new_list['reduced_topics'] = es.get_book_reduced_topics(id)
    new_list['similar_books_by_rate'] = rated
    new_list['similar_books_by_name'] = names
    new_list['isbn'] = es.get_book_isbn(id)

    return json.dumps(new_list)


app.run()
#host='192.168.56.99', port=8080