from abc import ABC
from drinqsapp.importer.request import Request
from drinqsapp.models import Cocktail, CocktailIngredient, Ingredient, Glass

class ImporterAdapter(ABC):
    def get_json_cocktail_list(self, json):
        pass

    def get_cocktails(self, json_cocktaillist):
        pass

    def get_cocktail_ingridients(self, json_cocktail_ingridientlist):
        pass

    def get_ingridients(self, json_ingridientlist):
        pass

    def get_glasses(self, json_glasslist):
        pass

class MrBostonAdapter(ImporterAdapter):
    name_treshhold = 30

    def get_data(self):
        params = dict(
            query='',
            limit=2500
        )
        return Request.get_json("https://api.mrboston.recipes", "/recipes", params)

    def get_json_cocktail_list(self, json):
        return json["data"]

    def get_cocktails(self, json_cocktaillist):
        for json_cocktail in json_cocktaillist:
            cocktail = self.get_cocktail(json_cocktail)
            ingridients = self.get_cocktail_ingredients(
                json_cocktail["recipe_ingredient"], cocktail)
            if ingridients is not None:
                if not self.cocktail_name_already_existing(cocktail.name):
                    cocktail.save()
                    for ingridient in ingridients:
                        ingridient.save()

    @staticmethod
    def cocktail_name_already_existing(name):
        try:
            cocktail = Cocktail.objects.get(name=name)
            return True
        except Cocktail.DoesNotExist:
            return False

    def get_cocktail(self, json_cocktail):
        name = json_cocktail["name"]
        preparation = json_cocktail["instructions"]
        thumbnail_url = self.get_thumbnail_url(json_cocktail["images"])
        category = json_cocktail["recipe_category"]["name"]
        glass = self.get_glass(json_cocktail["glass"])

        cocktail = Cocktail(name=name, category=category, preparation=preparation,\
                            thumbnail_url=thumbnail_url, glass=glass)
        return cocktail

    def get_cocktail_ingredients(self, json_cocktail_ingridient_list, cocktail):
        result = []
        too_long = False
        for cocktail_ingredient in json_cocktail_ingridient_list:
            cocktail_ingredient, ingridient_too_long = self.create_cocktail_ingredient(\
                cocktail_ingredient, cocktail)
            if ingridient_too_long:
                too_long = True
                break
            result.append(cocktail_ingredient)

        if too_long:
            return None
        return result

    def create_cocktail_ingredient(self, json_cocktail_ingridient, cocktail):
        ingredient, too_long = self.get_ingridient(json_cocktail_ingridient["ingredient"])
        measurement = json_cocktail_ingridient["amount"] + " " + self.__map_measurement_id(\
            json_cocktail_ingridient["measurement_id"])

        if not too_long:
            cocktail_ingredient = CocktailIngredient(ingredient=ingredient,\
                                                measurement=measurement, cocktail=cocktail)
            return cocktail_ingredient, False
        return None, True


    def get_ingridient(self, json_ingridient):
        ingridient_name = json_ingridient["name"]
        if len(ingridient_name) < self.name_treshhold:
            ingr, _created = Ingredient.objects.get_or_create(name=json_ingridient["name"])
            return ingr, False
        return None, True

    def get_glass(self, json_glass):
        if isinstance(json_glass, dict):
            glass, _created = Glass.objects.get_or_create(name=json_glass["name"])
            return glass
        return None

    def get_thumbnail_url(self, json_image_list):
        if isinstance(json_image_list, list):
            image_list = json_image_list[0]["image_sizes"]
            if isinstance(image_list, list):
                return image_list[0]["url"]
            return ""

    @staticmethod
    def __map_measurement_id(measurement_id):
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

        return dict.get(measurement_id, 0)
