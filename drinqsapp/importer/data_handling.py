from drinqsapp.importer.adapter import MrBostonAdapter

class DataHandler:
  def getMrBostonData(self):
      mrboston = MrBostonAdapter()
      response = mrboston.getData()
      jsonCocktailList = mrboston.getJsonCocktailList(response)
      mrboston.getCocktails(jsonCocktailList)
