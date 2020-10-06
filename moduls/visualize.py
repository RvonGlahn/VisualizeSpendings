import pandas as pd
import numpy
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import datetime


# einkommen - ausgaben -> gruen wenn positiv rot wenn negativ
# statisitken in datei und filtern screen schreiben

class visual:
    def __init__(self, visual_df):
        self.dataframe = visual_df  # cols 0:date, 1: money, 2: category
        self.filtered_df = None
        self.df_income = None
        self.date = datetime.datetime.today()
        self.this_month = self.date.month
        self.this_year = self.date.year
        # self.month_set = ["Alle", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.year_set, self.month_set = self.__get_relevant_years__()
        self.cat_set = numpy.append(numpy.array(["Alle"]), self.dataframe['category'].unique())
        self.plot_type = "bar"

    def __get_relevant_years__(self):
        year_set = []
        month_set = ["Alle"]
        for index, row in self.dataframe.iterrows():
            if row['date'][6:10] not in year_set:
                year_set.append(row['date'][6:10])
            if row['date'][3:5] not in month_set:
                month_set.append(row['date'][3:5])
        return year_set, month_set

    def __filter_year__(self, year, month):
        self.filtered_df = self.dataframe[self.dataframe["date"].str.contains(str(year))]
        if month is not "Alle":
            self.__filter_month__(month)

    def __filter_month__(self, month):
        self.filtered_df = self.filtered_df[self.filtered_df["date"].str.contains('\d\d.0' + str(month), regex=True)]

    def __filter_cat__(self, category):
        if category == "Alle":
            return
        self.filtered_df = self.filtered_df[self.filtered_df["category"].str.contains(category)]

    def __group_df__(self):
        self.filtered_df = self.filtered_df.groupby(['category']).sum()

    def __transform_date__(self):
        self.filtered_df['date'] = pd.to_datetime(self.filtered_df['date'], format='%d.%m.%Y')
        self.filtered_df['month'] = self.filtered_df['date'].dt.strftime('%B')
        self.filtered_df["date"] = self.filtered_df.loc[:, 'date'].dt.date

    def __set_plot_type__(self, month, cat):
        self.dataframe.money = self.dataframe.money.abs()
        if month is not "Alle" and cat == "Alle":
            self.plot_type = "pie"
        else:
            self.plot_type = "bar"

    def __drop_df__(self):
        """ Einkommen von AUsgaben trennen und Irrelevante Eintr?ge aus dem Df schmeissen"""
        self.df_income = self.filtered_df.loc[self.filtered_df['category'] == 'Einkommen']
        self.filtered_df = self.filtered_df.drop(self.filtered_df[self.filtered_df.category == 'Einkommen'].index)
        self.filtered_df = self.filtered_df.drop(self.filtered_df[self.filtered_df.category == 'Ignorieren'].index)

    def calc_statistics(self):
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                  'September', 'October', 'November', 'December']

        income = self.df_income.groupby(['month']).sum()
        # income = income[months]  -> gilt fuer columns brauche aber rows

        spendings_month = self.filtered_df.groupby(["month"]).sum()
        # spendings_month = spendings_month[months]

        spendings_cat = self.filtered_df.groupby(["category"]).sum()
        # difference = income - spendings_month

    def get_plot(self, year, month, cat):
        """
        :param year: selected year
        :param month: selected month all or specified
        :param cat: category of spendings. all or one selected
        :return: nothing
        Filters dfs and sends them to the diagramm class where they get plotted
        """
        self.__set_plot_type__(month, cat)
        self.__filter_year__(year, month)
        self.__filter_cat__(cat)
        self.__transform_date__()
        self.__drop_df__()
        plot = diagramm(self.plot_type, self.filtered_df)
        self.calc_statistics()
        plot.load_diagramm()


class diagramm:
    def __init__(self, typ, df):
        self.diag_type = typ
        self.dataframe = df

    def __bar__(self, column):
        plt.figure()
        sns.set(style="darkgrid")
        sns.set_context("paper")
        sns_plot = sns.barplot(data=self.dataframe, x=column, y="money", hue='category', palette="deep", estimator=sum,
                               ci=None)
        plt.setp(sns_plot.get_xticklabels(), rotation=45)
        plt.tight_layout()
        # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        image = sns_plot.get_figure()
        image.savefig('temp/tmp.png')

    def __pie__(self):
        img = self.dataframe.groupby(['category']).sum().plot(kind="pie", autopct='%.2f', subplots=True,
                                                              colormap='RdYlBu')
        image = img[0].get_figure()
        image.savefig('temp/tmp1.png')
        img = Image.open('temp/tmp1.png')
        img.show()

    def load_diagramm(self):
        if self.diag_type == "bar":
            self.__pie__()
            self.__bar__("month")
        if self.diag_type == "pie":
            self.__pie__()
            self.__bar__("date")
        img = Image.open('temp/tmp.png')
        img.show()

