from abc import ABC, abstractmethod
from drinqsapp.importer.request import Request
from drinqsapp.models import Cocktail, CocktailIngredient, Ingredient, Glass

class ImporterAdapter(ABC):
    def getJsonCocktailList(self, json):
        pass

    def getCocktails(self, jsonCocktailList):
        pass

    def getCocktailIngridients(self, jsonCocktailIngridientList):
        pass

    def getIngridients(self, jsonIngridientList):
        pass

    def getGlasses(self, jsonGlassList):
        pass

class MrBostonAdapter(ImporterAdapter):
    name_treshhold = 30

    def getData(self):
        params = dict(
            query='',
            limit=2500
        )
        return Request.get_json("https://api.mrboston.recipes", "/recipes", params)

    def getJsonCocktailList(self, json):
        return json["data"]

    def getCocktails(self, jsonCocktailList):
      for jsonCocktail in jsonCocktailList:
        cocktail = self.getCocktail(jsonCocktail)
        ingridients = self.getCocktailIngredients(jsonCocktail["recipe_ingredient"], cocktail)
        if ingridients != None:
          if not self.cocktailNameAlreadyExisting(cocktail.name):
            cocktail.save()
            for ingridient in ingridients:
              ingridient.save()

    @staticmethod
    def cocktailNameAlreadyExisting(name):
      try:
          cocktail = Cocktail.objects.get(name=name)
          return True
      except Cocktail.DoesNotExist:
          return False

    def getCocktail(self, jsonCocktail):
      name = jsonCocktail["name"]
      preparation = jsonCocktail["instructions"]
      thumbnail_url = self.getThumbnailUrl(jsonCocktail["images"])
      category = jsonCocktail["recipe_category"]["name"]
      glass = self.getGlass(jsonCocktail["glass"])

      cocktail = Cocktail(name=name, category=category, preparation=preparation, thumbnail_url=thumbnail_url, glass=glass)
      return cocktail

    def getCocktailIngredients(self, jsonCocktailIngridientList, cocktail):
      result = []
      too_long = False
      for cocktailIngredient in jsonCocktailIngridientList:
        cocktailIngredient, ingridient_too_long = self.createCocktailIngredient(cocktailIngredient, cocktail)
        if ingridient_too_long:
          too_long = True
          break
        else:
          result.append(cocktailIngredient)

      if too_long:
        return None
      else:
       return result

    def createCocktailIngredient(self, jsonCocktailIngridient, cocktail):
      ingredient, too_long = self.getIngridient(jsonCocktailIngridient["ingredient"])
      measurement = jsonCocktailIngridient["amount"] + " " + self.__mapMeasurementId(jsonCocktailIngridient["measurement_id"])

      if not too_long:
        cocktailIngredient = CocktailIngredient(ingredient=ingredient, measurement=measurement, cocktail=cocktail)
        return cocktailIngredient, False
      else:
        return None, True


    def getIngridient(self, jsonIngridient):
      ingridient_name = jsonIngridient["name"]
      if len(ingridient_name) < self.name_treshhold:
        ingr, _created = Ingredient.objects.get_or_create(name=jsonIngridient["name"])
        return ingr, False
      else:
        return None, True

    def getGlass(self, jsonGlass):
        if isinstance(jsonGlass,dict):
          glass, _created = Glass.objects.get_or_create(name=jsonGlass["name"])
          return glass
        else:
          return None

    def getThumbnailUrl(self, jsonImageList):
        if isinstance(jsonImageList, list):
            image_list = jsonImageList[0]["image_sizes"]
            if isinstance(image_list, list):
                return image_list[0]["url"]
            else:
                return ""

    @staticmethod
    def __mapMeasurementId(measurement_id):
        dict = {
          0 : "",
          2 : "Dash(es)",
          3 : "Piece",
          4 : "Ounce(s)",
          8 : "Lump(s)",
          9 : "Drop(s)",
          10: "Teaspoon(s)",
          11: "Splash",
          12: "Small scoop",
          13: "Slice(s)",
          18: "Glass",
          19: "Pinch(es)",
          21: "Inch-thick",
          24: "Long",
          30: "Scoop",
          34: "Tablespoon(s)",
          40: "Cup",
          44: "Quarts(s)",
          47: "Liter",
          53: "Pint(s)",
          54: "750-ml Bottle(s)",
          64: "Sprig(s)",
          69: "1/2 Cube(s)",
          78: "Twist",
          83: "Dozen",
          87: "Part(s)",
        }

        return dict.get(measurement_id,0)
