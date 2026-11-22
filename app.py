"""
Red Brick Community Kitchen - Recipe Scaler
Milestones 1 and 2: store recipes, scale them to any number of servings,
and answer plain-language questions.

Run it:         python recipe_tool.py
Run the tests:  python recipe_tool.py --test
"""

import re
import sys
from fractions import Fraction
from math import ceil

MIN_GUESTS = 1
MAX_GUESTS = 150

# Replace the amounts with your own real recipes when needed.
# Keep ingredient names lowercase and use only these units:
# tsp, tbsp, cup, lb, oz, can, each

recipes = [
    {
        "name": "Cornbread",
        "base_servings": 12,
        "ingredients": [
            {"name": "cornmeal", "amount": 1.5, "unit": "cup"},
            {"name": "flour", "amount": 1.0, "unit": "cup"},
            {"name": "sugar", "amount": 0.25, "unit": "cup"},
            {"name": "baking powder", "amount": 1.0, "unit": "tbsp"},
            {"name": "salt", "amount": 0.5, "unit": "tsp"},
            {"name": "milk", "amount": 1.0, "unit": "cup"},
            {"name": "egg", "amount": 2, "unit": "each"},
            {"name": "vegetable oil", "amount": 0.25, "unit": "cup"},
        ],
    },
    {
        "name": "Chili",
        "base_servings": 10,
        "ingredients": [
            {"name": "ground beef", "amount": 2.0, "unit": "lb"},
            {"name": "onion", "amount": 2, "unit": "each"},
            {"name": "kidney beans", "amount": 2, "unit": "can"},
            {"name": "diced tomatoes", "amount": 2, "unit": "can"},
            {"name": "tomato sauce", "amount": 1, "unit": "can"},
            {"name": "chili powder", "amount": 3.0, "unit": "tbsp"},
            {"name": "cumin", "amount": 1.0, "unit": "tbsp"},
            {"name": "garlic powder", "amount": 2.0, "unit": "tsp"},
            {"name": "salt", "amount": 2.0, "unit": "tsp"},
            {"name": "water", "amount": 2.0, "unit": "cup"},
        ],
    },
    {
        "name": "Vegetable Soup",
        "base_servings": 8,
        "ingredients": [
            {"name": "carrots", "amount": 1.0, "unit": "lb"},
            {"name": "potatoes", "amount": 1.5, "unit": "lb"},
            {"name": "onion", "amount": 1, "unit": "each"},
            {"name": "diced tomatoes", "amount": 1, "unit": "can"},
            {"name": "green beans", "amount": 2.0, "unit": "cup"},
            {"name": "vegetable broth", "amount": 8.0, "unit": "cup"},
            {"name": "thyme", "amount": 1.0, "unit": "tsp"},
            {"name": "salt", "amount": 1.5, "unit": "tsp"},
            {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Mac and Cheese",
        "base_servings": 12,
        "ingredients": [
            {"name": "elbow macaroni", "amount": 1.0, "unit": "lb"},
            {"name": "cheddar cheese", "amount": 1.0, "unit": "lb"},
            {"name": "milk", "amount": 3.0, "unit": "cup"},
            {"name": "butter", "amount": 4.0, "unit": "tbsp"},
            {"name": "flour", "amount": 4.0, "unit": "tbsp"},
            {"name": "breadcrumbs", "amount": 1.0, "unit": "cup"},
            {"name": "salt", "amount": 1.0, "unit": "tsp"},
            {"name": "black pepper", "amount": 0.5, "unit": "tsp"},
        ],
    },
    {
        "name": "Rice and Beans",
        "base_servings": 10,
        "ingredients": [
            {"name": "rice", "amount": 2.0, "unit": "cup"},
            {"name": "black beans", "amount": 2, "unit": "can"},
            {"name": "onion", "amount": 1, "unit": "each"},
            {"name": "vegetable oil", "amount": 2.0, "unit": "tbsp"},
            {"name": "cumin", "amount": 2.0, "unit": "tsp"},
            {"name": "garlic powder", "amount": 1.0, "unit": "tsp"},
            {"name": "salt", "amount": 1.0, "unit": "tsp"},
            {"name": "water", "amount": 4.0, "unit": "cup"},
        ],
    },
]

# Volunteers can't measure 3.3333 cups, so amounts are rounded UP to a
# measurable step. Rounding up means the kitchen never runs short.
ROUNDING_STEP = {
    "tsp": 0.25,
    "tbsp": 0.5,
    "cup": 0.25,
    "lb": 0.25,
    "oz": 1,
    "can": 1,
    "each": 1,
}


def find_recipe(name):
    """Return the recipe dict that matches `name`, or None if there isn't one."""
    name = name.strip().lower()
    if name.endswith(" recipe"):
        name = name[: -len(" recipe")]
    for recipe in recipes:                      # exact match first
        if recipe["name"].lower() == name:
            return recipe
    for recipe in recipes:                      # then a partial match ("mac")
        if name and name in recipe["name"].lower():
            return recipe
    return None


def find_ingredients(recipe, term):
    """Return the ingredients in `recipe` that match `term` ('beef' -> ground beef)."""
    term = term.strip().lower()
    exact = [i for i in recipe["ingredients"] if i["name"] == term]
    if exact:
        return exact
    return [i for i in recipe["ingredients"] if term in i["name"]]


def scale_recipe(recipe, servings):
    """Return a NEW recipe scaled to `servings`. The original is not changed."""
    factor = servings / recipe["base_servings"]
    return {
        "name": recipe["name"],
        "base_servings": servings,
        "ingredients": [
            {**ing, "amount": ing["amount"] * factor}   # copy, then replace amount
            for ing in recipe["ingredients"]
        ],
    }


# turn 3.3333 cups into "3 1/2 cups"

def round_up(amount, unit):
    step = ROUNDING_STEP.get(unit, 0.25)
    # round(..., 6) removes tiny floating-point fuzz before we take the ceiling
    return ceil(round(amount / step, 6)) * step


def format_number(x):
    """3.5 -> '3 1/2', 0.25 -> '1/4', 6.0 -> '6'."""
    frac = Fraction(x).limit_denominator(8)
    whole, remainder = divmod(frac.numerator, frac.denominator)
    if remainder == 0:
        return str(whole)
    if whole == 0:
        return f"{remainder}/{frac.denominator}"
    return f"{whole} {remainder}/{frac.denominator}"


def describe(ingredient):
    """One ingredient as a friendly line, e.g. '3 1/2 cups flour'."""
    amount = round_up(ingredient["amount"], ingredient["unit"])
    number = format_number(amount)
    name, unit = ingredient["name"], ingredient["unit"]
    if unit == "each":
        return f"{number} {name}{'s' if amount > 1 else ''}"
    if unit in ("cup", "can") and amount > 1:
        unit += "s"
    return f"{number} {unit} {name}"


def recipe_text(recipe):
    lines = [f"{recipe['name']} (serves {recipe['base_servings']})"]
    for ing in recipe["ingredients"]:
        lines.append(f"  - {describe(ing)}")
    return "\n".join(lines)


def unknown_recipe_message(name):
    known = ", ".join(r["name"] for r in recipes)
    return f"I don't have a recipe called '{name}'. I know: {known}."


def servings_warning(servings):
    if MIN_GUESTS <= servings <= MAX_GUESTS:
        return ""
    return (f"\n(Heads up: Red Brick usually cooks for {MIN_GUESTS} to "
            f"{MAX_GUESTS} guests, so double-check {servings}.)")


def answer_list():
    lines = ["Recipes I know:"]
    for r in recipes:
        lines.append(f"  - {r['name']} (base: {r['base_servings']} servings)")
    return "\n".join(lines)


def answer_what_is_in(recipe_name):
    recipe = find_recipe(recipe_name)
    if recipe is None:
        return unknown_recipe_message(recipe_name)
    return recipe_text(recipe)


def answer_scale(recipe_name, servings):
    recipe = find_recipe(recipe_name)
    if recipe is None:
        return unknown_recipe_message(recipe_name)
    if servings < 1:
        return "Servings must be at least 1."
    return recipe_text(scale_recipe(recipe, servings)) + servings_warning(servings)


def answer_how_much(ingredient_term, recipe_name, servings):
    recipe = find_recipe(recipe_name)
    if recipe is None:
        return unknown_recipe_message(recipe_name)
    if servings < 1:
        return "Servings must be at least 1."
    matches = find_ingredients(scale_recipe(recipe, servings), ingredient_term)
    if not matches:
        have = ", ".join(i["name"] for i in recipe["ingredients"])
        return f"{recipe['name']} doesn't use '{ingredient_term}'. It uses: {have}."
    lines = []
    for ing in matches:
        rounded = round_up(ing["amount"], ing["unit"])
        line = f"For {servings} servings of {recipe['name']} you need {describe(ing)}"
        if abs(rounded - ing["amount"]) > 0.005:   # show the exact math if we rounded
            line += f" (exact math: {ing['amount']:.2f} {ing['unit']})"
        lines.append(line + ".")
    return "\n".join(lines) + servings_warning(servings)


HELP_TEXT = """You can ask things like:
  how much flour for 40 servings of cornbread
  what is in the chili recipe
  scale chili to 100
  list recipes
  quit"""

# Patterns for the questions. (?:...) groups are optional filler words.
HOW_MUCH = re.compile(
    r"^how much (.+?) (?:do i need |do we need )?for (\d+)"
    r"(?: servings?| guests?| people)?(?: of)? (.+)$")
WHAT_IS_IN = re.compile(
    r"^(?:what(?:'s|s| is| are) in|ingredients (?:in|for)|show me|show) "
    r"(?:the )?(.+?)(?: recipe)?$")
SCALE = re.compile(
    r"^scale (?:the )?(.+?)(?: recipe)? (?:to|for) (\d+)"
    r"(?: servings?| guests?| people)?$")


def handle_question(text):
    """Turn a typed question into an answer string."""
    text = text.lower().strip().rstrip("?.! ")

    m = HOW_MUCH.match(text)
    if m:
        return answer_how_much(m.group(1), m.group(3), int(m.group(2)))

    m = SCALE.match(text)
    if m:
        return answer_scale(m.group(1), int(m.group(2)))

    if text in ("list", "recipes", "list recipes", "show recipes"):
        return answer_list()

    m = WHAT_IS_IN.match(text)
    if m:
        return answer_what_is_in(m.group(1))

    if text in ("help", "?"):
        return HELP_TEXT
    return "Sorry, I didn't understand that. Type 'help' to see example questions."


# I really hope this is polished enough lol

def main():
    print("Red Brick Community Kitchen - Recipe Scaler")
    print(HELP_TEXT)
    while True:
        try:
            text = input("\nAsk a question> ")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip().lower() in ("quit", "exit", "q"):
            break
        if text.strip():
            print(handle_question(text))
    print("Goodbye!")

#yayy tests

def run_tests():
    # formatting
    assert format_number(3.5) == "3 1/2"
    assert format_number(0.25) == "1/4"
    assert format_number(6.0) == "6"

    # data and lookup
    assert len(recipes) >= 5
    cornbread = find_recipe("cornbread")
    assert find_recipe("Cornbread recipe") is cornbread
    assert find_recipe("pizza") is None

    # scaling: doubling 12 servings, 24 should double the flour (1 cup -> 2)
    scaled = scale_recipe(cornbread, 24)
    flour = find_ingredients(scaled, "flour")[0]
    assert abs(flour["amount"] - 2.0) < 1e-9
    assert find_ingredients(cornbread, "flour")[0]["amount"] == 1.0   # original untouched

    # plain-language questions
    answer = handle_question("How much flour for 40 servings of cornbread?")
    assert "3 1/2 cups flour" in answer and "3.33" in answer
    assert "7 eggs" in handle_question("how much egg for 40 servings of cornbread")
    assert "ground beef" in handle_question("What is in the chili recipe?")
    assert "20 lb ground beef" in handle_question("scale chili to 100")
    assert "Cornbread" in handle_question("list recipes")
    assert "don't have" in handle_question("what is in the pizza recipe")
    assert "doesn't use" in handle_question("how much sugar for 40 servings of chili")
    assert "at least 1" in handle_question("scale chili to 0")
    assert "Heads up" in handle_question("scale chili to 500")
    print("All tests passed.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        main()
