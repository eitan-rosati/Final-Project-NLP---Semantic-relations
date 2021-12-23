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

from BackEnd.classes.Elastic_search import elasticsearch
from nltk.corpus import wordnet as wn


class expend_synonym_index:
    """
    ===================================================================================================
    Init
    ===================================================================================================
    """

    def __init__(self, records_list):
        self.find_indexed_records(records_list)

    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """

    def find_indexed_records(self, records_list):
        """
        the function receive a books records list
        for every book we will go over the topics and expand the synonyms using wordnet
        and save the synonyms list un elasticsearch in Synonyms index
        """
        elastic = elasticsearch()
        for record in records_list:
            words_indexes = []
            for word in record[3]:
                token_index = elastic.get_synonym_index_by_token(word)
                if not token_index:
                    synonyms = self.get_synonyms_list(word)
                    token_index = elastic.add_new_synonyms_list(synonyms)
                words_indexes.append(token_index)

            elastic.update_record_with_indexes(record[0], words_indexes)

    def get_synonyms_list(self, word):
        """
        the function receive a word and expand the word to a synonyms list using wordnet
        """
        synonyms = [word]
        for syn in wn.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
        return list(dict.fromkeys(synonyms))
