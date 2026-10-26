import unittest

import diet_logic


class DietLogicTests(unittest.TestCase):
    def test_recommendations_return_full_day_within_budget(self):
        plan = diet_logic.get_diet_recommendations(budget=220)

        self.assertEqual(
            [meal["category"] for meal in plan],
            ["breakfast", "lunch", "dinner"],
        )
        self.assertLessEqual(
            sum(meal["cost_max"] for meal in plan),
            220,
        )

    def test_budget_below_minimum_returns_no_plan(self):
        plan = diet_logic.get_diet_recommendations(budget=100)

        self.assertEqual(plan, [])
        self.assertEqual(diet_logic.get_minimum_daily_budget(), 220)

    def test_ingredient_matching_accepts_common_alias(self):
        plan = diet_logic.get_diet_recommendations(
            ingredients_input="rice", budget=220
        )

        lunch = next(meal for meal in plan if meal["category"] == "lunch")
        self.assertIn("Basmati rice", lunch["matched_ingredients"])

    def test_grocery_list_is_unique_and_sorted(self):
        plan = diet_logic.get_diet_recommendations(budget=220)

        grocery_list = diet_logic.generate_grocery_list(plan)

        self.assertEqual(grocery_list, sorted(set(grocery_list), key=str.casefold))


if __name__ == "__main__":
    unittest.main()
