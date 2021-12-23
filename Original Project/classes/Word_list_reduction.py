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
from nltk.corpus import wordnet
import requests


class Word_list_reduction:
    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """

    def normalize_words_list_wordnet(self, words_list):
        """
        the function receive a list of words and reduce the synonyms from the list using wordnet
        """
        expanded_words_list = []
        words_list_copy = words_list.copy()
        for word in words_list_copy:
            if word in expanded_words_list:
                words_list.remove(word)
                continue
            syn_sets = wordnet.synsets(word)
            for syn_set in syn_sets:
                for name in syn_set._lemma_names:
                    if name not in expanded_words_list:
                        expanded_words_list.append(name)
        return words_list

    def normalize_words_list_conceptnet(self, words_list):
        """
        the function receive a list of words and reduce the synonyms from the list using conceptnet
        """

        words_list_copy = words_list.copy()
        for first_word_index in range(0, len(words_list_copy)):
            for second_word_index in range(first_word_index + 1, len(words_list_copy)):
                try:
                    url = self.parse_conceptnet_url(words_list_copy[first_word_index],
                                                    words_list_copy[second_word_index])
                except:
                    return "ConceptNet API if unreachable"
                synonyms_json_obj = requests.get(url).json()
                if len(synonyms_json_obj['edges']):
                    words_list.remove(words_list_copy[first_word_index])
                    break
        return words_list

    def parse_conceptnet_url(self, first_word, second_word):
        """
        the function receive two words and send an api to conceptnet anf return the response
        """
        return "http://api.conceptnet.io/query?node=/c/en/" + first_word + \
               "&other=/c/en/" + second_word + "&rel=/r/Synonym&limit=1";
