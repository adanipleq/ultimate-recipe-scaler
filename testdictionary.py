# this is just for practice right now but i'll treat it as a V1
recipe = {
    "name": "Pancakes", #yes, I like pancakes this much
    "servings": 4,
    "ingredients": [
        {"name": "flour",  "amount": 200, "unit": "g",  "pkg_price": 3.50, "pkg_size": 2000},
        {"name": "milk",   "amount": 300, "unit": "ml", "pkg_price": 2.80, "pkg_size": 1000},
        {"name": "eggs",   "amount": 2,   "unit": "",   "pkg_price": 4.00, "pkg_size": 12},
    ],
}
def scale_recipe(recipe, new_servings):
    factor = new_servings / recipe["servings"]
    scaled = {
        "name": recipe["name"],
        "servings": new_servings,
        "ingredients": [],
    }
    for ing in recipe["ingredients"]:
        new_ing = ing.copy()          # copy so we don't change the original
        new_ing["amount"] = ing["amount"] * factor
        scaled["ingredients"].append(new_ing)
    return scaled
def ingredient_cost(ing):
    return ing["amount"] / ing["pkg_size"] * ing["pkg_price"]

def total_cost(recipe):
    return sum(ingredient_cost(ing) for ing in recipe["ingredients"])
def print_recipe(recipe):
    print(f"\n{recipe['name']} (serves {recipe['servings']})")
    print("-" * 40)
    for ing in recipe["ingredients"]:
        cost = ingredient_cost(ing)
        print(f"{ing['amount']:.1f} {ing['unit']} {ing['name']:<10} ${cost:.2f}")
    total = total_cost(recipe)
    print("-" * 40)
    print(f"Total: ${total:.2f}  (${total / recipe['servings']:.2f} per serving)")
def main():
    print_recipe(recipe)
    new_servings = int(input("\nScale to how many servings? "))
    print_recipe(scale_recipe(recipe, new_servings))

if __name__ == "__main__":
    main()