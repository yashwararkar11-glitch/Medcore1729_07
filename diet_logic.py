from itertools import product


INDIAN_MEAL_DATABASE = [
    {
        "id": "poha",
        "name_key": "poha_name",
        "category": "breakfast",
        "cuisine_key": "cuisine_poha",
        "ingredients": [
            "Flattened rice (poha)",
            "Peanuts",
            "Green peas",
            "Onion",
            "Green chillies",
            "Turmeric",
            "Mustard seeds",
        ],
        "ingredient_aliases": {
            "flattened rice (poha)": ("poha", "flattened rice", "पोहे", "चिवड़ा"),
            "peanuts": ("peanut", "groundnut", "मूंगफली", "शेंगदाणे"),
            "green peas": ("peas", "मटर", "मटार"),
            "onion": ("प्याज़", "कांदा"),
        },
        "cost_min": 30,
        "cost_max": 50,
        "prep_key": "poha_prep",
    },
    {
        "id": "dal_tadka",
        "name_key": "dal_name",
        "category": "lunch",
        "cuisine_key": "cuisine_dal",
        "ingredients": [
            "Toor dal",
            "Cumin seeds",
            "Garlic",
            "Tomatoes",
            "Basmati rice",
            "Ghee",
            "Spices",
            "Salad vegetables",
        ],
        "ingredient_aliases": {
            "toor dal": ("arhar dal", "pigeon pea", "तूर डाळ", "अरहर दाल"),
            "cumin seeds": ("cumin", "jeera", "जीरा", "जिरे"),
            "garlic": ("लहसुन", "लसूण"),
            "tomatoes": ("tomato", "टमाटर", "टोमॅटो"),
            "basmati rice": ("rice", "चावल", "तांदूळ"),
            "ghee": ("घी", "तूप"),
        },
        "cost_min": 60,
        "cost_max": 90,
        "prep_key": "dal_prep",
    },
    {
        "id": "ragi_roti",
        "name_key": "ragi_name",
        "category": "dinner",
        "cuisine_key": "cuisine_ragi",
        "ingredients": [
            "Ragi flour",
            "Carrots",
            "Beans",
            "Cabbage",
            "Onions",
            "Spices",
            "Cooking oil",
        ],
        "ingredient_aliases": {
            "ragi flour": ("ragi", "finger millet", "नाचणी", "रागी"),
            "carrots": ("carrot", "गाजर"),
            "beans": ("green beans", "फली", "शेंगा"),
            "cabbage": ("पत्तागोभी", "कोबी"),
            "onions": ("onion", "प्याज़", "कांदा"),
        },
        "cost_min": 50,
        "cost_max": 80,
        "prep_key": "ragi_prep",
    },
]


def _matched_ingredients(meal: dict, user_ingredients: list[str]) -> list[str]:
    matches = []
    for ingredient in meal["ingredients"]:
        aliases = meal["ingredient_aliases"].get(ingredient.casefold(), ())
        terms = (ingredient.casefold(), *(alias.casefold() for alias in aliases))
        if any(
            term == user_term
            or term in user_term
            or (len(user_term) >= 3 and user_term in term)
            for user_term in user_ingredients
            for term in terms
        ):
            matches.append(ingredient)
    return matches


def get_minimum_daily_budget() -> int:
    lowest_meals = []
    for category in ("breakfast", "lunch", "dinner"):
        options = [m for m in INDIAN_MEAL_DATABASE if m["category"] == category]
        if not options:
            return 0
        lowest_meals.append(min(meal["cost_max"] for meal in options))
    return sum(lowest_meals)


def get_diet_recommendations(
    ingredients_input: str = "", budget: int = 500
) -> list[dict]:
    """Return a full-day plan within budget, prioritizing available ingredients."""
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 0:
        raise ValueError("Budget must be a non-negative integer.")

    user_ingredients = [
        item.strip().casefold()
        for item in ingredients_input.split(",")
        if item.strip()
    ]
    meals_by_category = [
        [meal for meal in INDIAN_MEAL_DATABASE if meal["category"] == category]
        for category in ("breakfast", "lunch", "dinner")
    ]
    plans = []
    for plan in product(*meals_by_category):
        total_max = sum(meal["cost_max"] for meal in plan)
        if total_max > budget:
            continue
        matches = [_matched_ingredients(meal, user_ingredients) for meal in plan]
        match_count = sum(bool(items) for items in matches)
        plans.append((match_count, total_max, plan, matches))

    if not plans:
        return []

    _, _, selected_plan, matches = max(
        plans,
        key=lambda candidate: (candidate[0], -candidate[1]),
    )
    return [
        {**meal, "matched_ingredients": matched}
        for meal, matched in zip(selected_plan, matches)
    ]


def generate_grocery_list(selected_meals: list[dict]) -> list[str]:
    grocery_items = {
        ingredient
        for meal in selected_meals
        for ingredient in meal["ingredients"]
    }
    return sorted(grocery_items, key=str.casefold)
