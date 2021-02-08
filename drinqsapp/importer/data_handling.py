from drinqsapp.importer.adapter import MrBostonAdapter
from drinqsapp.importer.csv import CsvImport

class DataHandler:
    def getMrBostonData(self):
        mrboston = MrBostonAdapter()
        response = mrboston.getData()
        jsonCocktailList = mrboston.getJsonCocktailList(response)
        mrboston.getCocktails(jsonCocktailList)

    def getCsvData(self):
        df1, df2, df3 = CsvImport().importDatasets('data/all_drinks.csv', 'data/hotaling_cocktails.csv', 'data/hotaling_cocktails2.csv')
        CsvImport().cleanDatasets(df1 = df1, df2 = df2, df3 = df3)
        df23 = CsvImport().joinDatasets(df2 = df2, df3 = df3)
        CsvImport().populateDatabase(df1 = df1, df23 = df23)
