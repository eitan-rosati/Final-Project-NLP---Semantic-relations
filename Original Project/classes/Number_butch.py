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
from gensim.models import KeyedVectors


class number_batch():
    """
    ===================================================================================================
    Init
    ===================================================================================================
    """

    def __init__(self):
        """
        the class create a word embedding model using numberbatch file
        """
        self.number_batch_path = "../files/number_batch/numberbatch-en.txt"
        self.number_batch_model = ""
        self.load_model()

    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """

    def load_model(self):
        """
        the function tries to load existing model
        if model doesnt exist it will create a new model using KeyedVectors.load_word2vec_format by gensim
        """
        try:
            self.number_batch_model = KeyedVectors.load("files/number_batch/numberbatch.model")
        except:
            print("model file not exist, creating a new model file")
            self.number_batch_model = KeyedVectors.load_word2vec_format(
                self.number_batch_path,
                binary=False,
                unicode_errors='ignore'
            )
            self.number_batch_model.save("files/number_batch/numberbatch.model")


    def similarity_score(self,term1,term2):
        """
        the function receive two words and return their similarity score
        """
        try:
            return self.number_batch_model.similarity(term1, term2)
        except:
            return 0