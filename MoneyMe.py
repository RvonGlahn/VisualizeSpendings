"""
Popup um Liste sehen und loeschen zu koennen

monate links nach rechts beim plot
Statistiken zu Ausgaben erstellen
-> eigene Datenseite, die in einer Excel Tabelle exportiert werden kann
"""
import os
import sys
import pandas as pd
import pickle
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser
from moduls import money_data
from moduls import GlobalVar
from moduls import visualize

Window.size = (600, 500)
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class Start_Window(Screen):
    def set_desktop(self):
        """
        filechooser path set to desktop
        :return:
        """
        fc = self.manager.get_screen('my_filechooser')
        fc.ids.filechooser.path = os.path.expanduser("~/Desktop")


class My_Filechooser(Screen):
    def open(self, path, selection):
        """
        :param path: Path to csv file
        :param selection: name of csv file
        :return: PopUp if Error
        """
        try:
            GlobalVar.card.path = os.path.join(path, selection[0])
            GlobalVar.card.read_cols()
        except IndexError:
            popup = Popup(title='Reminder', content=Label(text='Bitte w?hle eine csv Datei aus. ',
                                                          font_size="16sp"), size_hint=(None, None), size=(300, 300))
            popup.open()
            sm.current = "start"


class Select_Cols(Screen):
    def select_col(self, typ):
        """
        select Columns from Dropdown Menu
        :param typ: type of Column Datum, Auftraggeber, Verwendungszweck and Betrag
        :return:
        """
        button = None
        if typ == "date":
            button = self.ids.date_button
        if typ == "auf":
            button = self.ids.auf_button
        if typ == "verw":
            button = self.ids.verw_button
        if typ == "betrag":
            button = self.ids.betrag_button

        dropdown = DropDown()
        for index in GlobalVar.card.col_list:
            btn = Button(text=index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        dropdown.open(button)
        dropdown.bind(on_select=lambda instance, x: setattr(button, 'text', x))

    def save(self):
        """
        Save names of Selected Columns to card obejct list
        :return:
        col_list: List of the 4 selected Columns
        class_col: list of Auftraggeber and Verwendungszweck
        """
        GlobalVar.card.col_list = [self.ids.auf_button.text, self.ids.verw_button.text, self.ids.betrag_button.text,
                                   self.ids.date_button.text]
        GlobalVar.card.class_col = [self.ids.auf_button.text, self.ids.verw_button.text]
        GlobalVar.card.money_col = self.ids.betrag_button.text
        GlobalVar.card.date_col = self.ids.date_button.text

    def reset(self):
        self.ids.date_button.text = "click me"
        self.ids.auf_button.text = "click me"
        self.ids.verw_button.text = "click me"
        self.ids.betrag_button.text = "click me"
        GlobalVar.card.col_list = []
        GlobalVar.card.class_col = []
        GlobalVar.card.money_col = ""
        GlobalVar.card.date_col = ""
        GlobalVar.card.skip_row = 0

    def call_cat(self):
        """ Call function load_categories() on next Screen Add_Categories"""
        if "click me" in GlobalVar.card.col_list:
            sm.current = "start"
            popup = Popup(title='Reminder', content=Label(text='Waehle fuer jede Kategorie ein Label aus',
                                                          font_size="16sp"), size_hint=(None, None), size=(300, 300))
            popup.open()
            self.reset()
            return
        ac = self.manager.get_screen('add_category')
        ac.decide()


class Add_Category(Screen):

    def decide(self):
        if GlobalVar.first_card:
            self.load_categories()
            GlobalVar.first_card = False
            return
        if not GlobalVar.first_card:
            sm.current = "configure_category"
            self.call_config()
            self.filter_spendings()

    def load_categories(self):
        """
        Create Buttons dynamically for each entry in saved dict category_dict
        :return:
        """
        GlobalVar.category_dict = money_data.load_filter()
        layout = self.ids.category_buttons
        for category in GlobalVar.category_dict.keys():
            btn = Button(id=category, text=category, size_hint_y=None, height=30, background_normal='',
                         background_color=[83 / 255, 96 / 255, 110 / 255, 1])
            btn.bind(on_press=self.callback)
            layout.add_widget(btn)

    def callback(self, value):
        """on bind function to set Button color and change status if category selected or not"""
        if value.id not in GlobalVar.categories:
            value.background_color = (0.157, 0.455, 0.753, 1.0)
            GlobalVar.categories.append(value.id)
        else:
            value.background_color = (83 / 255, 96 / 255, 110 / 255, 1.0)
            GlobalVar.categories.remove(value.id)

    def add_name(self, name):
        """add new category to dict and create button for it"""
        if name not in GlobalVar.categories:
            GlobalVar.category_dict.update({name: ["qwertzui"]})
            GlobalVar.categories.append(name)
            layout = self.ids.category_buttons
            btn = Button(id=name, text=name, size_hint_y=None, height=30, background_normal='',
                         background_color=[0.157, 0.455, 0.753, 1.0])
            btn.bind(on_press=self.callback)
            layout.add_widget(btn)

    def call_config(self):
        """call load_selected in next Screen Configure Category to set buttons"""
        cc = self.manager.get_screen('configure_category')
        cc.load_selected()

    def filter_spendings(self):
        """call load_unknown in next Screen Configure Category and read.csv to pandas dataframe"""
        GlobalVar.card.read_csv()
        cc = self.manager.get_screen('configure_category')
        cc.load_unknown()
        cc.load_text()

    def choose_category(self):
        button = self.ids.choose_cat
        dropdown = DropDown()
        for index in GlobalVar.card.dict_filter.keys():
            btn = Button(text=index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        dropdown.open(button)
        dropdown.bind(on_select=lambda instance, x: setattr(button, 'text', x))

    def show_category(self, category):
        help_list = GlobalVar.card.dict_filter[category]
        for key, entry in enumerate(help_list):
            if key % 2 == 0:
                help_list[key] = "\n" + help_list[key]
        separator = ' , '
        cat_string = separator.join(help_list)
        popup = Popup(title='Category', content=Label(text=cat_string,
                                                      font_size="12sp"), size_hint=(None, None), size=(300, 300))
        popup.open()

    def reset_category(self, category):
        GlobalVar.card.dict_filter[category] = ['qwertzui']


class Configure_Category(Screen):
    df_sonst = None
    key = ""
    text = ""

    def load_unknown(self):
        """
        reset visited indexes
        call set_spending to filter spendings by lists from category_dict
        :return:
        """
        GlobalVar.card.set_spendings(GlobalVar.categories, GlobalVar.first_card)
        self.df_sonst = GlobalVar.card.get_sonstige()
        if "Undefined" not in self.df_sonst["Ausgabenart"]:
            self.ids.label_zahlung.text = "Alle Zahlungen wurden zugewiesen."

    def load_text(self):
        """
        load text in Configure Screen for Sonstige Ausgaben
        :return: Verwendungszeck, Index
        """
        for index, row in self.df_sonst.iterrows():
            text = row.to_string(header=False, index=False).split('\n')
            self.ids.label_zahlung.text = text[1] + '\n' + text[2] + '\n' + text[3] + '\n' + text[4]
            '''
            if int(text[4]) < 0:
                self.ids.label_zahlung.color = [1, 95 / 255, 80 / 255, 0.95]
            else:
                self.ids.label_zahlung.color = [128 / 255, 171 / 255, 102 / 255, 1]
            '''
            self.text = text[2].lstrip()  # text[2] ist der Empf?nger
            return

    def add_to_dict(self, value):
        """
        Add entry to dict and df
        :param value: self from Button
        :return:
        """
        GlobalVar.card.update_dict(value.text, self.text)
        self.load_unknown()
        self.load_text()

    def load_selected(self):
        """
        load buttons for selected categories
        :return:
        """
        layout = self.ids.button_zahlung

        for name in GlobalVar.categories:
            b_color = [83 / 255, 96 / 255, 110 / 255, 1]
            if name == "Ignorieren":
                b_color = [1, 87 / 255, 80 / 255, 0.95]
            if name == "Einkommen":
                b_color = [128 / 255, 171 / 255, 102 / 255, 1]
            btn = Button(id=name, text=name, size_hint_y=None, height=30, background_normal='',
                         background_color=b_color)
            btn.bind(on_press=self.add_to_dict)
            layout.add_widget(btn)

    def delete_cat(self):
        GlobalVar.categories = []

    def save_category(self):
        """
        Save card to dataframe visual_df that contains all data for visualization
        rename columns (date, money, category)
        reset old data -> refactor later
        :return:
        """
        if GlobalVar.first_card:
            GlobalVar.visual_df = GlobalVar.card.df_card[[GlobalVar.card.date_col, GlobalVar.card.money_col,
                                                          "Ausgabenart"]].copy()
            GlobalVar.visual_df = GlobalVar.visual_df.rename(columns={GlobalVar.visual_df.columns[0]: 'date',
                                                                      GlobalVar.visual_df.columns[1]: 'money',
                                                                      'Ausgabenart': 'category'})
        else:
            df_temp = GlobalVar.card.df_card[[GlobalVar.card.date_col, GlobalVar.card.money_col, 'Ausgabenart']].copy()
            df_temp = df_temp.rename(columns={df_temp.columns[0]: 'date', df_temp.columns[1]: 'money',
                                              'Ausgabenart': 'category'})
            GlobalVar.visual_df = pd.concat([GlobalVar.visual_df, df_temp])
            del df_temp

        sc = self.manager.get_screen('select_cols')
        sc.ids.date_button.text = "click me"
        sc.ids.auf_button.text = "click me"
        sc.ids.verw_button.text = "click me"
        sc.ids.betrag_button.text = "click me"
        with open(r'data/category.pkl', 'wb') as f:
            pickle.dump(GlobalVar.card.dict_filter, f, pickle.HIGHEST_PROTOCOL)
        GlobalVar.card = money_data.Card()
        GlobalVar.categories = []


class Middle_Menue(Screen):
    def call_visualize(self):
        vis = self.manager.get_screen('visual')
        vis.init_visual()


class Visual(Screen):
    plot = None

    def init_visual(self):
        self.plot = visualize.visual(GlobalVar.visual_df)

    def drop(self, button, item_liste):
        drop = DropDown()
        for index in item_liste:
            index = str(index)
            btn = Button(text=index, size_hint=[None, None], height=44, width=120)
            btn.bind(on_release=lambda btn: drop.select(btn.text))
            drop.add_widget(btn)
        drop.open(button)
        drop.bind(on_select=lambda instance, x: setattr(button, 'text', x))

    def load_dropdown(self, typ):
        button = None
        if typ == "cat":
            button = self.ids.cat_button
            self.drop(button, self.plot.cat_set)
        if typ == "year":
            button = self.ids.year_button
            self.drop(button, self.plot.year_set)
        if typ == "month":
            button = self.ids.month_button
            self.drop(button, self.plot.month_set)

    def load_diagramm(self):
        self.plot.get_plot(self.ids.year_button.text, self.ids.month_button.text, self.ids.cat_button.text)


class WindowManager(ScreenManager):
    pass


class MoneyMe(App):
    def build(self):
        return sm


def resourcePath():
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)

    return os.path.join(os.path.abspath("."))


if __name__ == '__main__':
    kivy.resources.resource_add_path(resourcePath())
    kv = Builder.load_file("moduls\layout.kv")
    sm = WindowManager()
    screens = [Start_Window(name="start"), My_Filechooser(name="my_filechooser"), Select_Cols(name="select_cols"),
               Add_Category(name="add_category"), Configure_Category(name="configure_category"),
               Middle_Menue(name="middle_menue"), Visual(name="visual")]
    for screen in screens:
        sm.add_widget(screen)

    sm.current = "start"
    MoneyMe().run()
