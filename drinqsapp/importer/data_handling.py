from drinqsapp.importer.adapter import MrBostonAdapter
from drinqsapp.importer.csv import CsvImport

class DataHandler:
    def getMrBostonData(self):
        mrboston = MrBostonAdapter()
        response = mrboston.get_data()
        jsonCocktailList = mrboston.get_json_cocktail_list(response)
        mrboston.get_cocktails(jsonCocktailList)

    def getCsvData(self):
        df1, df2, df3 = CsvImport().import_datasets('data/all_drinks.csv', 'data/hotaling_cocktails.csv', 'data/hotaling_cocktails2.csv')
        CsvImport().clean_datasets(df1 = df1, df2 = df2, df3 = df3)
        df23 = CsvImport().join_datasets(df2 = df2, df3 = df3)
        CsvImport().populate_database(df1 = df1, df23 = df23)
