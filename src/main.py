from recipe_scrapers import scrape_me
#from nltk.stem.lancaster import LancasterStemmer
import json
from util_funcs import *

# NOTES: The way the code is designed, some food categories
#        need to be placed before others. For Example: 
#        "Canned" goods before "Meats" - So that things like
#        "Chicken Broth" don't get caught by Meat::Chicken
#        and the broth is properly categorized as "Canned"

SetupSugarCube()

f = open('Food_DataBase.json')
database = json.load(f)
f.close()
categories = {}
for cat in database:
    categories.update({cat:[]})
    for idx, item in enumerate(database[cat]):
        database[cat][idx] = item.upper()
    
f = open('Ignored_Ingredients.json')
ignoredList = json.load(f)
f.close()
ignoredItems = ignoredList["ignore"]
for idx, item in enumerate(ignoredItems):
    ignoredItems[idx] = item.upper()

f = open('Recipes.json')
recipes = json.load(f)
f.close()

for recipe in recipes["urls"]:
    scraper = scrape_me(recipe, wild_mode=True)
    ingredients = scraper.ingredients()
    for idx, ingredient in enumerate(ingredients):
        ingredients[idx] = ingredient.upper()

    for cat in database:
        for item in database[cat]:
            for ingredient in ingredients:
                # ignore common household items
                if any(ignoredItem in ingredient.upper() for ignoredItem in ignoredItems):
                    ingredients.remove(ingredient)
                    break
                # If an item in the database matches with something in the ingredient, add to respected category
                if item in ingredient:
                    # If item already present in the category, add
                    if any(item in addedItem for addedItem in categories[cat]):
                        ret = AddSameIngredients(item, ingredient, categories[cat])
                        if (ret == False):
                            # Failed to combine!
                            categories[cat].append(ingredient)
                    else:
                        categories[cat].append(ingredient)
                    ingredients.remove(ingredient)

    for item in ingredients:
        categories["Other"].append(item)

with open('ShoppingList.txt', 'w') as f:
    for cat in categories:
        print(cat, ":", file=f)
        for item in categories[cat]:
            print(item, file=f)
        print("\n", file=f)