"""
Final Project
Software engineering department
Authors:
Sapir Nahum
Shmuel Eliasyan
"""
import logging

"""
===================================================================================================
Imports
===================================================================================================
"""
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections
import calendar
import time

connections.add_connection('default', Elasticsearch)


class elasticsearch():
    """
    ===================================================================================================
    Init
    ===================================================================================================
    """

    def __init__(self):
        self.client = Elasticsearch()
        self.s = Search(using=self.client)

    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """

    def upload_dictionary(self, dictionary, mode):
        """
        upload new books to the books index
        """
        logging.info("Uploading books information to ElasticSearch")

        if mode == "create":
            self.client.indices.create(index="books", ignore=[400, 404])
            for i in range(len(dictionary)):
                res = self.client.exists(index="books", id=dictionary[i][0])
                if res:
                    self.delete_record("books", record_id=dictionary[i][0])
                self.client.index(index="books", id=dictionary[i][0],
                                  body={"title": dictionary[i][1], "original_topics": dictionary[i][2],
                                        "normalized_topics": dictionary[i][3],
                                        "reduced_topics": dictionary[i][4],
                                        "description": dictionary[i][5], "isbn": dictionary[i][6], "synonym": []})

    def delete_record(self, index, record_id):
        """
        delete record from index
        """
        self.client.delete(index=index, id=record_id, ignore=[400, 404])

    def delete_index(self, index):
        """
        delete index
        """
        self.client.indices.delete(index=index, ignore=[400, 404])

    def find_books(self, token):
        """
        find books by token
        """
        books_id = []
        res = self.client.search(index="books", body={"query": {"match": {"reduced_topics": token}}}, size=1000)
        if res['hits']['total']['value'] == 0:
            return -1
        else:
            for hit in res['hits']['hits']:
                books_id.append(hit['_id'])
        return books_id


    def get_synonym_index_by_token(self, token):
        """
          find synonyms list by token
        """
        try:
            synonyms = []
            res = self.client.search(index="synonyms", body={"query": {"match": {"words": token}}}, size=1000)
            for hit in res['hits']['hits']:
                synonyms.append(hit['_id'])
            return synonyms
        except:
            self.client.indices.create(index="synonyms", ignore=400)
            return False

    def add_new_synonyms_list(self, synonyms_list):
        """
        add new synonyms list to synonyms index
        """
        self.client.indices.create(index="synonyms", ignore=400)
        res = self.client.index(index="synonyms", body={"words": synonyms_list})
        return res['_id']

    def update_record_with_indexes(self, mms_id, record_indexes):
        """
        add new synonyms id to a book in books index
        """
        res = self.client.get(index="books", id=mms_id)
        self.client.update(index="books", id=mms_id, body={"doc": {"synonym": record_indexes}})

    def get_book_synonym(self, mms_id):
        """
        get book list of synonyms ids
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['synonym']

    def get_all_synonym(self):
        """
        get all synonyms from synonyms index
        """
        res = self.client.search(index="synonyms", size=10000)
        return res['hits']['hits']

    def get_book_synonym_lists(self, mms_id):
        """
        get book list of synonyms
        """
        res = self.get_book_synonym(mms_id)
        lists = []
        for hit in res:
            lists.append(self.client.get(index="synonyms", id=hit)['_source']['words'])
        return lists

    def get_books_by_common_synonym(self, synonym, lamda):
        """
        get list of books with common synonyms to the synonyms list
        """
        count = {}
        for i in synonym:
            res = self.client.search(index="books", body={"query": {"match": {"synonym": i}}}, size=20)
            for hit in res['hits']['hits']:
                if hit['_id'] in count:
                    count[hit['_id']][1] += 1
                else:
                    count[hit['_id']] = [hit['_source']['title'], 1]

        temp = count.copy()
        for j in count:
            if count[j][1] < lamda:
                del temp[j]

        return temp

    def get_synonym_by_id(self, syn_id):
        """
        get synonyms list by id
        """
        res = self.client.get(index="synonyms", id=syn_id)
        return res['_source']['words']

    def get_book_by_isbn(self, isbn):
        """
        get book mms_id by isbn
        """
        res = self.client.search(index="books", body={"query": {"match": {"isbn": isbn}}}, size=1)
        return res['hits']['hits'][0]['_id']

    def get_book_reduced_topics(self, mms_id):
        """
        get book reduced topics list
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['reduced_topics']

    def get_book_original_topics(self, mms_id):
        """
        get book original topics list
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['original_topics']

    def get_book_normalized_topics(self, mms_id):
        """
        get book reduced normalized list
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['normalized_topics']

    def get_all_books_ids(self):
        """
        get ids of all books in books index
        """
        books = []
        res = self.client.search(index='books', size=10000)
        for hit in res['hits']['hits']:
            books.append(hit['_id'])
        return books

    def get_book_title(self, mms_id):
        """
        get book title
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['title']

    def get_book_description(self, mms_id):
        """
        get book description
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['description']

    def get_book_isbn(self, mms_id):
        """
        get book isbn
        """
        res = self.client.get(index="books", id=mms_id)
        return res['_source']['isbn']

    def get_books_by_tokens(self, tokens):
        """
        get books by list of tokens
        """
        books = []
        for token in tokens:
            res = self.client.search(index="books", body={"query": {"match": {"reduced_topics": token}}}, size=10)
            for book in res['hits']['hits']:
                temp = {}
                temp['mms_id'] = book['_id']
                temp['title'] = book['_source']['title']
                temp['isbn'] = book['_source']['isbn']

                books.append(temp)
        return books

    def get_random_books(self):
        """
        get 30 random books
        """
        gmt = time.gmtime()
        res = self.client.search(index='books', doc_type='_doc', size=30,
                                 body={"query": {
                                     "function_score": {
                                         "functions": [{
                                             "random_score": {
                                                 "seed": calendar.timegm(gmt)
                                             }
                                         }]
                                     }
                                 }})
        rnd_books = []
        for book in res['hits']['hits']:
            temp = {}
            temp['mms_id'] = book['_id']
            temp['title'] = book['_source']['title']
            temp['isbn'] = book['_source']['isbn']
            rnd_books.append(temp)

        return rnd_books

    def add_new_review(self,json):
        self.client.indices.create(index="feedbacks", ignore=[400, 404])
        self.client.index(index="feedbacks", body={"mms_id1": json['mms_id1'], "mms_id2": json['mms_id2'],
                                    "score": json['score'],
                                    "q1": json['q1'], "q2": json['q2'], "q3": json['q3'],
                                    "q4": json['q4'],"q5": json['q5'],})