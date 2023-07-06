from recipe_scrapers import scrape_me
from nltk.stem.lancaster import LancasterStemmer
import json
st = LancasterStemmer()

f = open('Food_DataBase.json')
database = json.load(f)
f.close()
categories = {}
for cat in database:
    categories.update({cat:[]})
    
f = open('Ignored_Ingredients.json')
ignoredList = json.load(f)
f.close()
ignoredItems = ignoredList["ignore"]

f = open('Recipes.json')
recipes = json.load(f)
f.close()

for recipe in recipes["urls"]:
    scraper = scrape_me(recipe, wild_mode=True)
    ingredients = scraper.ingredients()
    
    for index, word in enumerate(ingredients):
        ingredients[index] = st.stem(word)

    for cat in database:
        for item in database[cat]:
            for ingredient in ingredients:
                if any(ignoredItem in ingredient for ignoredItem in ignoredItems):
                    ingredients.remove(ingredient)
                    break
                if item.upper() in ingredient.upper():
                    categories[cat].append(ingredient)
                    ingredients.remove(ingredient)

    for item in ingredients:
        categories["Other"].append(item)
        print(item)

with open('ShoppingList.txt', 'w') as f:
    for cat in categories:
        print(cat, ":", file=f)
        for item in categories[cat]:
            print(item, file=f)
        print("\n", file=f)