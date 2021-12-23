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
from classes.Normalize_marc_file import normalizeMarc
from classes.Elastic_search import elasticsearch
from classes.Expend_synonym_index import expend_synonym_index
from classes.Create_report import create_report
from flask import Flask
app = Flask(__name__)
es = elasticsearch()
cr = create_report()
import logging
from datetime import date

"""
===================================================================================================
Main
===================================================================================================
"""
if __name__ == '__main__':
    """
    Start flask app and impost routes functions
    """
    today = date.today()
    logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO, filename='files/logs/'+today.strftime("%d-%m-%Y")+'.log')
    data = normalizeMarc("files/marc_files/BIBLIOGRAPHIC.xml")
    record_list = data.records_list
    cr.create_books_excel(record_list)
    es.upload_dictionary(record_list, "create")
    expend_synonym_index(record_list)
    # import BackEnd.classes.routes as routes
