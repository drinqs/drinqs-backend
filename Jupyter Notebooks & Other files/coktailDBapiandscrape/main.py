import json, csv
import scrape_cocktaildb, filing, api


def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


if __name__ == '__main__':
    dict = api.get_ingredient_tag()
    print(dict)
    with open('ingredient_tags.csv', mode='w') as tag_file:
        tag_writer = csv.writer(tag_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        tag_writer.writerow(['Cocktail', 'Tag', 'Alcoholic'])
        for ele in dict:
            tag_writer.writerow([ele, dict[ele][0], dict[ele][1]])
