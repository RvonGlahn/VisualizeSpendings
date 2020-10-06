import os
import sys
import math
import pandas as pd
import csv
import pickle

sys.path.append(os.path.join(sys.path[0], 'moduls'))
sys.path.append(os.path.join(sys.path[0], 'data'))


pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 10)


def load_filter():
    """
    load default categories from pickle file category
    :return: categories
    """
    with open('data/category.pkl', 'rb') as f:
        return pickle.load(f)


class Card:
    def __init__(self):
        """
        path: path to csv file
        type:
        col_list: List of relevant columns for Betrag, Datum, Verwendungszweck und Auftraggeber
            - money_col:  Name of Betrag column
            - date_col: Name of Datum column
            - class_col: Names of Kategorie Columns
        df_card: Dataframe to store all relevant infos for transactions
        skip_row: number of lines to skip in csv file
        """
        self.path = ""
        self.type = ""
        self.col_list = []
        self.money_col = ""
        self.date_col = ""
        self.class_col = []
        self.df_card = None
        self.skip_row = 0
        self.dict_filter = load_filter()
        self.delimiter = ''

    def sniff_delimiter(self):
        with open(self.path, newline="") as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=",")
                self.delimiter = ','
            except:
                self.delimiter = ';'

    def set_path(self, csv_path):
        self.path = csv_path

    def update_dict(self, key, value):
        """ for schleife um boese Zeichen zu entfernen und if key um neue category ins dict zu schreiben """
        black_list = ["+", "*", "^", ".", "@", "?", "(", ")"]
        for char in black_list:
            if char in value:
                max_value = max(value.split(char))
                # value.replace(char, '')
                if len(max_value) < 3:
                    max_value = value.split(char)[0]
                elif len(max_value) < 3:
                    max_value = value.split(char)[1]
                elif len(max_value) < 3:
                    max_value = value.split(char)[2]
                elif len(max_value) < 3:
                    max_value = value.split(char)[3]
                elif len(max_value) < 3:
                    max_value = "qwertzui"
                value = max_value
        if key not in self.dict_filter.keys():
            self.dict_filter.update({key: ["qwertzuik"]})
        self.dict_filter[key].append(value)

    def read_cols(self):
        """
        Read csv file and search for row that contains column headers
        :self:
            skip_row: rows to skip for pandas read_csv function
        """
        self.sniff_delimiter()
        with open(self.path) as csvfile:
            read_csv = csv.reader(csvfile, delimiter=self.delimiter)
            steps_max = 0
            steps = 0
            max = 0
            for row in read_csv:
                x = 0
                for entry in row:
                    x += 1
                if x > max:
                    max = x
                    steps_max = steps
                    self.col_list = row
                if steps >20:
                    return
                steps += 1
                self.skip_row = steps_max

    def read_csv(self):
        """
        CSV auslesen, encoding anpassen, ';' als Trennzeichen und nur bestimmte Spalten auslesen
        """
        for column in self.col_list:
            if 'mail' in column or 'Mail' in column:
                self.col_list.append('Typ')
                break

        self.df_card = pd.read_csv(self.path, skiprows=self.skip_row, delimiter=self.delimiter, encoding='latin1',
                                   usecols=self.col_list)
        indexes = []
        for index, row in self.df_card.iterrows():
            try:
                if math.isnan(row[self.class_col[0]]):
                    indexes.append(index)
            except TypeError:
                pass
        self.df_card = self.df_card.drop(indexes)

        self.df_card[self.money_col] = self.df_card[self.money_col].str.replace(".", "")
        self.df_card[self.money_col] = self.df_card[self.money_col].str.replace(',', '.').astype(float)
        self.df_card.fillna('', inplace=True)
        for column in self.col_list:
            if 'mail' in column or 'Mail' in column:
                self.drop_paypal()
                break
        self.df_card["Ausgabenart"] = 'Undefined'

    def drop_paypal(self):
        self.df_card = self.df_card.drop(self.df_card[self.df_card.Typ == "Bankgutschrift auf PayPal-Konto"].index)
        del self.df_card['Typ']
        self.col_list.pop()
        self.col_list.pop(-1)
        self.col_list.insert(0, "Datum")
        self.df_card = self.df_card[self.col_list]   # Umsortieren der columns

    def set_spendings(self, categories, first_card):
        """
        set all Ausgabenarten to Sonstige
        get index all indexes related to each category_list and add the to Ausgabeart
        :return:
        """
        dict_filter_striped = {}
        cat = []
        if first_card:
            cat = categories
        else:
            cat = self.dict_filter.keys()
        for item in cat:
            if item in self.dict_filter.keys():
                dict_filter_striped.update({item: self.dict_filter[item]})
        for category, cat_liste in dict_filter_striped.items():
            # df_indexes contains indexes that fit categories
            df_indexes = self.df_card[self.df_card[self.class_col[0]].str.contains('|'.join(cat_liste),
                                                                                   case=False)].index
            df_indexes.append(self.df_card[self.df_card[self.class_col[1]].str.contains('|'.join(cat_liste),
                                                                                        case=False)].index)
            df_indexes = set(df_indexes)
            if bool(df_indexes):
                self.df_card.loc[df_indexes, "Ausgabenart"] = category

    def get_sonstige(self):
        """
        filter Column Ausagbenart for Sonstige
        :return: df_sonst: dataframe that contains all spendings "Sonstige"
        """
        indexes = self.df_card[self.df_card['Ausgabenart'].str.match('Undefined')].index
        df_sonst = self.df_card[self.df_card['Ausgabenart'].str.match('Undefined')]
        df_sonst.insert(0, "Keys", indexes, True)
        return df_sonst


def main():
    card_obj = Card()
    card_obj.date_col = "Buchungstag"
    card_obj.money_col = "Betrag (EUR)"
    card_obj.class_col = ["Auftraggeber / Beg?nstigter", "Verwendungszweck"]
    card_obj.col_list = ["Buchungstag", "Verwendungszweck", "Auftraggeber / Beg?nstigter", "Betrag (EUR)"]

    card_obj.set_path(r"C:\Users\rasmu\Desktop\Programmieren\Python\DKB\Daten\dkb.csv")
    card_obj.read_cols()
    card_obj.read_csv()
    card_obj.set_spendings()
    card_obj.get_sonstige()


if __name__ == "__main__":
    main()
