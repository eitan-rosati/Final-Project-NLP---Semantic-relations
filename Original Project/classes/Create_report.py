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
import pandas as pd


class create_report():
    """
    ===================================================================================================
    Init
    ===================================================================================================
    """
    def __init__(self):
        self.es = elasticsearch()

    """
    ===================================================================================================
    Functions
    ===================================================================================================
    """
    def create_report_excel(self,sorted_dict,book_id):
        ids=[]
        scores=[]
        names=[]
        original_topics=[]
        normalised=[]
        topics=[]
        synon = []
        ids.append(book_id)
        scores.append("-")
        names.append(self.es.get_book_title(book_id))
        original_topics.append(self.es.get_book_original_topics(book_id))
        normalised.append(self.es.get_book_normalized_topics(book_id))
        topics.append(self.es.get_book_reduced_topics(book_id))
        synon.append(self.es.get_book_synonym_lists(book_id))
        for book in sorted_dict:
            ids.append(book)
            scores.append(sorted_dict[book])
            names.append(self.es.get_book_title(book))
            original_topics.append(self.es.get_book_original_topics(book))
            normalised.append(self.es.get_book_normalized_topics(book))
            topics.append(self.es.get_book_reduced_topics(book))
            synon.append(self.es.get_book_synonym_lists(book))
        df = pd.DataFrame({'Book ID':ids,
                           'Title':names,
                           'Score':scores,
                           'Original Topics':original_topics,
                           'Normalized Topics':normalised,
                           'Reduced Topics':topics,
                           'Synonyms':synon})

        writer = pd.ExcelWriter("files/report.xlsx", engine='xlsxwriter')
        df.to_excel(writer, sheet_name=book_id, startrow=1, header=False)

        workbook = writer.book
        worksheet = writer.sheets[book_id]

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#000000',
            'font_color': '#FFFFFF',
            'border': 1})
        book_format = workbook.add_format({
            'bold': True,
            'font_color': '#3300FF'})

        # # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num+1, value, header_format)
        worksheet.set_row(1,None,book_format)

        for i, col in enumerate(df.columns):
            # find length of column i
            column_len = df[col].astype(str).str.len().max()
            # Setting the length if the column header is larger
            # than the max column value length
            column_len = max(column_len, len(col)) + 2
            # set the column length
            worksheet.set_column(i+1,i+1, column_len)
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    def create_books_excel(self, records_list):
        ids = []
        titles = []
        original_topics = []
        normalised = []
        topics = []
        descriptions = []
        for book in records_list:
            ids.append(book[0])
            titles.append(book[1])
            original_topics.append(book[2])
            normalised.append(book[3])
            topics.append(book[4])
            descriptions.append(book[5])
        df = pd.DataFrame({'Book ID': ids,
                           'Title': titles,
                           'Original Topics': original_topics,
                           'Normalized Topics': normalised,
                           'Reduced Topics': topics,
                           'Description': descriptions})

        writer = pd.ExcelWriter("files/list.xlsx", engine='xlsxwriter')

        df.to_excel(writer, sheet_name="list of books", startrow=1, header=False)

        workbook = writer.book
        worksheet = writer.sheets["list of books"]

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': False,
            'valign': 'top',
            'fg_color': '#000000',
            'font_color': '#FFFFFF',
            'border': 1})
        book_format = workbook.add_format({
            'bold': True,
            'font_color': '#3300FF'})

        # # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)
        worksheet.set_row(1, None, book_format)

        # for i, col in enumerate(df.columns):
        #     # find length of column i
        #     column_len = df[col].astype(str).str.len().max()
        #     # Setting the length if the column header is larger
        #     # than the max column value length
        #     column_len = max(column_len, len(col)) + 2
        #     # set the column length
        #     worksheet.set_column(i + 1, i + 1, column_len)
        # # Close the Pandas Excel writer and output the Excel file.
        writer.save()