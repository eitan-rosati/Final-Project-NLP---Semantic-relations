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
import xml.etree.ElementTree as ET
import re
import nltk
import logging
from nltk.corpus import stopwords
from BackEnd.classes.Word_list_reduction import Word_list_reduction
stop_words = set(stopwords.words('english'))
nltk.download('stopwords')


class normalizeMarc:
    """
    ===================================================================================================
    Init
    ===================================================================================================
    """

    def __init__(self, file):

        self.dictionary = []
        self.records_list = self.parse_xml(file)

    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """

    def parse_xml(self, xml_name):
        """
        xml should be in shape of a collection with some records
        the function receive MARC file (xml file) and go over every record and save the information we need
        the tags we save are:
        001 - book mms id
        020 - book isbn
        245 - book title
        520 - book description
        650 - book topics
        """
        logging.info("Extracting data from the MARC file..")
        xml_tree = ET.parse(xml_name)
        xml_root = xml_tree.getroot()
        fields_and_ids = []
        for record in xml_root:
            mms_id = ''
            orig_topics = []
            fields_and_id = []
            description = ''
            isbn = ''
            title = ''
            for field in record.findall('controlfield'):
                if field.get('tag') == '001':
                    mms_id = field.text
                    break
            for field in record.findall('datafield'):
                if field.get('tag') == '650':
                    for subfield in field.findall('subfield'):
                        if subfield.get('code') == 'a':
                            orig_topics.append(subfield.text)
                elif field.get('tag') == '245':
                    for subfield in field.findall('subfield'):
                        if subfield.get('code') == 'a':
                            title = subfield.text
                            if not title[-1].isalpha():
                                title = title[:-1]
                elif field.get('tag') == '020' and isbn == "":
                    for subfield in field.findall('subfield'):
                        if subfield.get('code') == 'a':
                            isbn = subfield.text.split(" ")[0]
                elif field.get('tag') == '520':
                    for subfield in field.findall('subfield'):
                        if subfield.get('code') == 'a':
                            description = subfield.text

            if orig_topics and len(orig_topics) > 5:
                fields_and_id.append(mms_id)
                fields_and_id.append(title)
                fields_and_id.append(orig_topics)
                normalized = self.normalize_650_fields(orig_topics)
                fields_and_id.append(normalized)
                reduced = self.reduceListOfTopics(normalized)
                fields_and_id.append(reduced)
                fields_and_id.append(description)
                fields_and_id.append(isbn)
                fields_and_ids.append(fields_and_id)
        logging.info("Finished extracting data from the MARC file successfully!!!")
        return fields_and_ids


    def reduceListOfTopics(self, list):
        """
        the function receive a list and return reduced of synonyms list using Vector_reduction class
        """
        reduce = Word_list_reduction()
        newList = reduce.normalize_words_list_wordnet(list)
        return newList


    def normalize_650_fields(self, list):
        """
        the function receive a list of book topic and normalize it
        the function separate the word, remove numbers and remove stop words
        """
        final_words_array = []
        for i in range(len(list)):
            list[i] = re.sub(r'\[[0-9]*\]', '', list[i])
            cell_value = self.normalize_single_array_cell(list[i])
            index_i_words_array = cell_value.split()
            for word in index_i_words_array:
                if word not in final_words_array:
                    if word not in stop_words:
                        final_words_array.append(word)
        self.dictionary = self.dictionary + final_words_array
        return final_words_array


    def normalize_single_array_cell(self, cell_value):
        """
        the function receive a word topic and lower the letters and remove any char that is not a letter
        """
        cell_value = cell_value.lower()
        cell_value = re.sub(r'\d', ' ', cell_value)
        cell_value = re.sub(r'\s', ' ', cell_value)
        cell_value = re.sub(r'\W', ' ', cell_value)
        return cell_value