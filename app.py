import math

recipes = [
    {
        "name": "Cornbread",
        "base_servings": 12,
        "ingredients": [
            {"name": "cornmeal", "amount": 1.5, "unit": "cup"},
            {"name": "flour", "amount": 1, "unit": "cup"},
            {"name": "sugar", "amount": 0.25, "unit": "cup"},
            {"name": "baking powder", "amount": 1, "unit": "tbsp"},
            {"name": "salt", "amount": 0.5, "unit": "tsp"},
            {"name": "milk", "amount": 1, "unit": "cup"},
            {"name": "eggs", "amount": 2, "unit": "each"},
            {"name": "vegetable oil", "amount": 0.25, "unit": "cup"},
        ],
    },
    {
        "name": "Chili",
        "base_servings": 10,
        "ingredients": [
            {"name": "ground beef", "amount": 2, "unit": "lb"},
            {"name": "onions", "amount": 2, "unit": "each"},
            {"name": "kidney beans", "amount": 2, "unit": "can"},
            {"name": "diced tomatoes", "amount": 2, "unit": "can"},
            {"name": "tomato sauce", "amount": 1, "unit": "can"},
            {"name": "chili powder", "amount": 3, "unit": "tbsp"},
            {"name": "cumin", "amount": 1, "unit": "tbsp"},
            {"name": "garlic powder", "amount": 2, "unit": "tsp"},
            {"name": "salt", "amount": 2, "unit": "tsp"},
            {"name": "water", "amount": 2, "unit": "cup"},
        ],
    },
    {
        "name": "Vegetable Soup",
        "base_servings": 8,
        "ingredients": [
            {"name": "carrots", "amount": 1, "unit": "lb"},
            {"name": "potatoes", "amount": 1.5, "unit": "lb"},
            {"name": "onions", "amount": 1, "unit": "each"},
            {"name": "diced tomatoes", "amount": 1, "unit": "can"},
            {"name": "green beans", "amount": 2, "unit": "cup"},
            {"name": "vegetable broth", "amount": 8, "unit": "cup"},
            {"name": "thyme", "amount": 1, "unit": "tsp"},
            {"name": "salt", "amount": 1.5, "unit": "tsp"},
            {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Mac and Cheese",
        "base_servings": 12,
        "ingredients": [
            {"name": "elbow macaroni", "amount": 1, "unit": "lb"},
            {"name": "cheddar cheese", "amount": 1, "unit": "lb"},
            {"name": "milk", "amount": 3, "unit": "cup"},
            {"name": "butter", "amount": 4, "unit": "tbsp"},
            {"name": "flour", "amount": 4, "unit": "tbsp"},
            {"name": "breadcrumbs", "amount": 1, "unit": "cup"},
            {"name": "salt", "amount": 1, "unit": "tsp"},
            {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Rice and Beans",
        "base_servings": 10,
        "ingredients": [
            {"name": "rice", "amount": 2, "unit": "cup"},
            {"name": "black beans", "amount": 2, "unit": "can"},
            {"name": "onions", "amount": 1, "unit": "each"},
            {"name": "vegetable oil", "amount": 2, "unit": "tbsp"},
            {"name": "cumin", "amount": 2, "unit": "tsp"},
            {"name": "garlic powder", "amount": 1, "unit": "tsp"},
            {"name": "salt", "amount": 1, "unit": "tsp"},
            {"name": "water", "amount": 4, "unit": "cup"},
        ],
    },
]


def find_recipe(name):
    name = name.strip().lower()
    if name == "":
        return None
    for recipe in recipes:
        if recipe["name"].lower() == name:
            return recipe
    for recipe in recipes:
        if name in recipe["name"].lower():
            return recipe
    return None


def scale_recipe(recipe, servings):
    factor = servings / recipe["base_servings"]
    new_ingredients = []
    for ing in recipe["ingredients"]:
        new_ing = ing.copy()
        new_ing["amount"] = ing["amount"] * factor
        new_ingredients.append(new_ing)
    return {
        "name": recipe["name"],
        "base_servings": servings,
        "ingredients": new_ingredients,
    }


def round_amount(amount, unit):
    if unit == "each" or unit == "can":
        return math.ceil(round(amount, 6))
    return math.ceil(round(amount * 4, 6)) / 4


def ingredient_line(ing):
    amount = round_amount(ing["amount"], ing["unit"])
    if ing["unit"] == "each":
        return f"{amount:g} {ing['name']}"
    return f"{amount:g} {ing['unit']} {ing['name']}"


def show_recipe(recipe):
    print(f"{recipe['name']} (serves {recipe['base_servings']})")
    for ing in recipe["ingredients"]:
        print("  " + ingredient_line(ing))


def recipe_not_found(name):
    print(f"I don't have a recipe called '{name}'.")
    names = [r["name"] for r in recipes]
    print("Recipes I have: " + ", ".join(names))


def check_servings(servings):
    if servings < 1:
        print("Servings must be at least 1.")
        return False
    if servings < 20 or servings > 150:
        print("Note: Red Brick usually cooks for 20 to 150 guests.")
    return True


def how_much(ingredient, recipe_name, servings):
    recipe = find_recipe(recipe_name)
    if recipe is None:
        recipe_not_found(recipe_name)
        return
    if not check_servings(servings):
        return
    scaled = scale_recipe(recipe, servings)
    found = False
    for ing in scaled["ingredients"]:
        if ingredient in ing["name"]:
            print(f"For {servings} servings of {scaled['name']} you need {ingredient_line(ing)}.")
            found = True
    if not found:
        print(f"{recipe['name']} doesn't use {ingredient}.")


def answer(question):
    question = question.lower().strip().rstrip("?.!")

    if question in ("list", "list recipes", "recipes"):
        for recipe in recipes:
            print(f"{recipe['name']} (base: {recipe['base_servings']} servings)")

    elif question.startswith("how much "):
        try:
            rest = question[len("how much "):]
            ingredient, rest = rest.split(" for ")
            words = rest.split()
            servings = int(words[0])
            recipe_name = " ".join(words[words.index("of") + 1:])
        except (ValueError, IndexError):
            print("I didn't get that. Try: how much flour for 40 servings of cornbread")
            return
        how_much(ingredient, recipe_name, servings)

    elif question.startswith("what is in "):
        name = question[len("what is in "):]
        if name.startswith("the "):
            name = name[4:]
        if name.endswith(" recipe"):
            name = name[:-7]
        recipe = find_recipe(name)
        if recipe is None:
            recipe_not_found(name)
        else:
            show_recipe(recipe)

    elif question.startswith("scale "):
        try:
            name, servings_text = question[len("scale "):].split(" to ")
            servings = int(servings_text.split()[0])
        except (ValueError, IndexError):
            print("I didn't get that. Try: scale chili to 100")
            return
        recipe = find_recipe(name)
        if recipe is None:
            recipe_not_found(name)
        elif check_servings(servings):
            show_recipe(scale_recipe(recipe, servings))

    else:
        print("Sorry, I didn't understand that.")

def main():
    print("Red Brick Community Kitchen - Recipe Scaler")
    print("Try: how much flour for 40 servings of cornbread")
    print("     what is in the chili recipe")
    print("     scale chili to 100")
    print("     list recipes")
    print("     quit")
    while True:
        question = input("\nAsk a question: ")
        if question.strip().lower() == "quit":
            break
        if question.strip() != "":
            answer(question)
    print("Goodbye!")


if __name__ == "__main__":
    main()
