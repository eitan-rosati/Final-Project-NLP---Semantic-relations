"""Eitan Rosati, Software Engineering Department - Azrieli College of Engineering"""


class data_processor:
    def extract_data(self):
        import pandas as pd
        # Extract the fields we need from the DB
        ids, records_isbn, titles, topic_by_record, descriptions = self.extract_seeds()
        # normalize the topics to list of phrases.
        normalized_topics = self.normalize_topics(topic_by_record)
        book_dataset = pd.DataFrame({"id": ids,
                                     "title": titles,
                                     "topics": normalized_topics,
                                     "description": descriptions,
                                     "isbn": records_isbn})
        return book_dataset

    def extract_seeds(self):
        import xml.etree.ElementTree as ET
        """
        Extracting from the MARC file the following information:
            001 - book mms id
            020 - book isbn
            245 - book title
            520 - book description
            650 - book topics
        """
        xml_tree = ET.parse(self.file_name)
        xml_root = xml_tree.getroot()
        enter = False
        # lists for the books information
        ids = []
        titles = []
        descriptions = []
        records_isbn = []
        topic_by_record = []

        # local variables to extract the data from file
        description = ''
        isbn = ''
        title = ''
        mms_id = ''
        for record in xml_root:
            for field in record.findall('controlfield'):
                if field.get('tag') == '001':
                    mms_id = field.text
                    break
            record_topics = []
            for field in record.findall('datafield'):
                if not enter:
                    enter = True
                if field.get('tag') == '650':
                    for subfield in field.findall('subfield'):
                        if subfield.get('code') == 'a':
                            record_topics.append(subfield.text)
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

            # add the information we extract to our lists
            topic_by_record.append(record_topics)
            titles.append(title)
            ids.append(mms_id)
            descriptions.append(description)
            records_isbn.append(isbn)

        return ids, records_isbn, titles, topic_by_record, descriptions

    def normalize_topics(self, topic_by_record):
        normalized_topics = []
        for record_topics in topic_by_record:
            rec_topics = list(set(record_topics))
            normalized_topic_record = []
            for topic in rec_topics:
                if '/' in topic:
                    topic = topic.replace("/", ",")
                elif "--" in topic:
                    topic = topic.replace("--", ",")
                elif "—" in topic:
                    topic = topic.replace("—", ",")
                normalized_topic_record = normalized_topic_record + (topic.split(", "))
            normalized_topics.append(normalized_topic_record)

        for i in range(len(normalized_topics)):
            if "" in normalized_topics[i]:
                normalized_topics[i].remove("")
            for j in range(len(normalized_topics[i])):
                if len(normalized_topics[i][j]) != 0 and normalized_topics[i][j][-1] in [".", " "]:
                    normalized_topics[i][j] = normalized_topics[i][j][:-1]

        return normalized_topics

    def __init__(self, file_name):
        self.file_name = file_name
        self.books_dataset = self.extract_data()
