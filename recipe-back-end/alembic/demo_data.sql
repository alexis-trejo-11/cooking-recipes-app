-- IMPORTANT: THIS FILE REQUIRES 5 USERS TO BE PRESENT IN THE USERS TABLE

INSERT INTO tags (id, name, description, usage_count, created_at) VALUES
(1, 'vegetarian', 'Suitable for vegetarians', 0, CURRENT_TIMESTAMP),
(2, 'vegan', 'No animal products', 0, CURRENT_TIMESTAMP),
(3, 'gluten-free', 'No gluten ingredients', 0, CURRENT_TIMESTAMP),
(4, 'dairy-free', 'No dairy products', 0, CURRENT_TIMESTAMP),
(5, 'low-carb', 'Low carbohydrate content', 0, CURRENT_TIMESTAMP),
(6, 'high-protein', 'Rich in protein', 0, CURRENT_TIMESTAMP),
(7, 'quick', 'Ready in 30 minutes or less', 0, CURRENT_TIMESTAMP),
(8, 'easy', 'Simple to prepare', 0, CURRENT_TIMESTAMP),
(9, 'family-friendly', 'Great for the whole family', 0, CURRENT_TIMESTAMP),
(10, 'comfort-food', 'Hearty and satisfying', 0, CURRENT_TIMESTAMP),
(11, 'healthy', 'Nutritious and balanced', 0, CURRENT_TIMESTAMP),
(12, 'spicy', 'Contains spicy elements', 0, CURRENT_TIMESTAMP),
(13, 'sweet', 'Sweet treats and desserts', 0, CURRENT_TIMESTAMP);


INSERT INTO recipes (id, name, author_id, difficulty, cuisine, description, servings, prep_time_minutes, cook_time_minutes, rest_time_minutes, calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, version, created_at, view_count) VALUES
-- Classic Spaghetti Carbonara
(1, 'Classic Spaghetti Carbonara', 4, 'Medium', 'Italian', 'Creamy Italian pasta dish with eggs, cheese, and pancetta', 4, 15, 15, 0, 650, 25.0, 75.0, 25.0, 3.0, 800.0, 1, CURRENT_TIMESTAMP, 1250),

-- Vegetarian Buddha Bowl
(2, 'Rainbow Buddha Bowl', 3, 'Easy', 'Fusion', 'Colorful plant-based bowl with quinoa and fresh vegetables', 2, 20, 10, 0, 420, 15.0, 65.0, 12.0, 10.0, 350.0, 1, CURRENT_TIMESTAMP, 890),

-- Chocolate Chip Cookies
(3, 'Perfect Chocolate Chip Cookies', 2, 'Easy', 'American', 'Soft and chewy cookies with melted chocolate chips', 24, 15, 12, 30, 180, 2.0, 25.0, 8.0, 1.0, 150.0, 1, CURRENT_TIMESTAMP, 2100),

-- Chicken Stir Fry
(4, 'Quick Chicken Stir Fry', 5, 'Easy', 'Asian', 'Fast and flavorful chicken with mixed vegetables', 4, 10, 15, 0, 320, 30.0, 20.0, 12.0, 5.0, 600.0, 1, CURRENT_TIMESTAMP, 750),

-- Greek Salad
(5, 'Authentic Greek Salad', 3, 'Easy', 'Greek', 'Fresh Mediterranean salad with feta and olives', 4, 15, 0, 30, 280, 8.0, 15.0, 22.0, 4.0, 850.0, 1, CURRENT_TIMESTAMP, 1100),

-- Beef Tacos
(6, 'Mexican Beef Tacos', 1, 'Medium', 'Mexican', 'Seasoned ground beef in crispy taco shells', 6, 20, 15, 0, 380, 22.0, 28.0, 18.0, 4.0, 720.0, 1, CURRENT_TIMESTAMP, 950),

-- Vegan Lentil Soup
(7, 'Hearty Vegan Lentil Soup', 3, 'Easy', 'Mediterranean', 'Comforting soup packed with protein and vegetables', 6, 15, 35, 10, 210, 12.0, 35.0, 3.0, 8.0, 450.0, 1, CURRENT_TIMESTAMP, 680),

-- Berry Smoothie Bowl
(8, 'Morning Berry Smoothie Bowl', 2, 'Easy', 'Fusion', 'Thick smoothie bowl topped with fresh fruits and nuts', 1, 10, 0, 0, 350, 10.0, 45.0, 15.0, 8.0, 120.0, 1, CURRENT_TIMESTAMP, 520);


INSERT INTO recipe_meal_types (recipe_id, meal_type) VALUES
(1, 'dinner'), (1, 'lunch'),
(2, 'lunch'), (2, 'dinner'),
(3, 'dessert'), (3, 'snack'),
(4, 'dinner'), (4, 'lunch'),
(5, 'lunch'), (5, 'dinner'),
(6, 'dinner'), (6, 'lunch'),
(7, 'lunch'), (7, 'dinner'),
(8, 'breakfast');


INSERT INTO recipe_tags (recipe_id, tag_id) VALUES
-- Spaghetti Carbonara
(1, 8), (1, 10),
-- Buddha Bowl
(2, 1), (2, 2), (2, 3), (2, 11),
-- Chocolate Cookies
(3, 8), (3, 13), (3, 9),
-- Chicken Stir Fry
(4, 7), (4, 8), (4, 6),
-- Greek Salad
(5, 1), (5, 11), (5, 7),
-- Beef Tacos
(6, 9), (6, 10),
-- Lentil Soup
(7, 2), (7, 3), (7, 4), (7, 6), (7, 11),
-- Smoothie Bowl
(8, 2), (8, 3), (8, 4), (8, 11);


INSERT INTO ingredients (id, recipe_id, name, quantity_value, quantity_unit, is_optional, is_vegan, is_vegetarian, is_gluten_free, is_dairy_free, allergens, substitutes) VALUES
-- Spaghetti Carbonara Ingredients
(1, 1, 'spaghetti', 400.000, 'grams', 0, 1, 1, 0, 1, '["gluten"]', '["gluten-free pasta"]'),
(2, 1, 'eggs', 3.000, 'units', 0, 0, 1, 1, 1, '["eggs"]', '[]'),
(3, 1, 'pancetta', 150.000, 'grams', 0, 0, 1, 1, 1, '[]', '["bacon", "guanciale"]'),
(4, 1, 'parmesan cheese', 100.000, 'grams', 0, 0, 1, 1, 0, '["dairy"]', '["nutritional yeast"]'),
(5, 1, 'black pepper', 2.000, 'teaspoons', 0, 1, 1, 1, 1, '[]', '[]'),

-- Buddha Bowl Ingredients
(6, 2, 'quinoa', 200.000, 'grams', 0, 1, 1, 1, 1, '[]', '["rice", "couscous"]'),
(7, 2, 'sweet potato', 1.000, 'large', 0, 1, 1, 1, 1, '[]', '["butternut squash"]'),
(8, 2, 'avocado', 1.000, 'unit', 0, 1, 1, 1, 1, '[]', '["hummus"]'),
(9, 2, 'chickpeas', 400.000, 'grams', 0, 1, 1, 1, 1, '[]', '["black beans"]'),
(10, 2, 'tahini', 3.000, 'tablespoons', 0, 1, 1, 1, 1, '["sesame"]', '["almond butter"]'),

-- Chocolate Chip Cookies Ingredients
(11, 3, 'all-purpose flour', 280.000, 'grams', 0, 1, 1, 0, 1, '["gluten"]', '["gluten-free flour"]'),
(12, 3, 'butter', 225.000, 'grams', 0, 0, 1, 1, 0, '["dairy"]', '["coconut oil"]'),
(13, 3, 'brown sugar', 200.000, 'grams', 0, 1, 1, 1, 1, '[]', '["coconut sugar"]'),
(14, 3, 'chocolate chips', 300.000, 'grams', 0, 1, 1, 1, 1, '[]', '["cacao nibs"]'),
(15, 3, 'vanilla extract', 2.000, 'teaspoons', 0, 1, 1, 1, 1, '[]', '["almond extract"]'),

-- Chicken Stir Fry Ingredients
(16, 4, 'chicken breast', 500.000, 'grams', 0, 0, 1, 1, 1, '[]', '["tofu", "shrimp"]'),
(17, 4, 'bell peppers', 2.000, 'units', 0, 1, 1, 1, 1, '[]', '["zucchini"]'),
(18, 4, 'broccoli', 1.000, 'head', 0, 1, 1, 1, 1, '[]', '["cauliflower"]'),
(19, 4, 'soy sauce', 3.000, 'tablespoons', 0, 1, 1, 1, 1, '["soy"]', '["tamari", "coconut aminos"]'),
(20, 4, 'ginger', 2.000, 'tablespoons', 0, 1, 1, 1, 1, '[]', '["ginger powder"]');

INSERT INTO recipe_steps (id, recipe_id, step_number, description, duration_minutes, technique, temperature, ingredients_used) VALUES
-- Spaghetti Carbonara Steps
(1, 1, 1, 'Bring a large pot of salted water to boil for the spaghetti', 10, 'Boiling', 'High', '[]'),
(2, 1, 2, 'Cook spaghetti according to package instructions until al dente', 8, 'Boiling', 'Medium', '["spaghetti"]'),
(3, 1, 3, 'While pasta cooks, dice pancetta and cook until crispy in a large pan', 6, 'Sautéing', 'Medium', '["pancetta"]'),
(4, 1, 4, 'Whisk eggs with grated parmesan and black pepper in a bowl', 2, 'Whisking', 'Room', '["eggs", "parmesan cheese", "black pepper"]'),
(5, 1, 5, 'Combine hot pasta with pancetta, then quickly mix with egg mixture off heat', 1, 'Tossing', 'Low', '["spaghetti", "pancetta", "egg mixture"]'),

-- Buddha Bowl Steps
(6, 2, 1, 'Cook quinoa according to package instructions', 15, 'Simmering', 'Medium', '["quinoa"]'),
(7, 2, 2, 'Roast diced sweet potato at 200°C until tender', 25, 'Roasting', 'High', '["sweet potato"]'),
(8, 2, 3, 'Prepare tahini dressing by whisking tahini with lemon juice and water', 5, 'Whisking', 'Room', '["tahini"]'),
(9, 2, 4, 'Assemble bowls with quinoa base, roasted vegetables, and fresh toppings', 5, 'Assembling', 'Room', '["quinoa", "sweet potato", "avocado", "chickpeas"]'),

-- Chocolate Chip Cookies Steps
(10, 3, 1, 'Preheat oven to 180°C and line baking sheets with parchment paper', 10, 'Preheating', 'High', '[]'),
(11, 3, 2, 'Cream together softened butter and sugars until light and fluffy', 3, 'Creaming', 'Room', '["butter", "brown sugar"]'),
(12, 3, 3, 'Beat in eggs and vanilla extract until well combined', 2, 'Mixing', 'Room', '["eggs", "vanilla extract"]'),
(13, 3, 4, 'Gradually mix in flour and salt until just combined', 2, 'Folding', 'Room', '["all-purpose flour"]'),
(14, 3, 5, 'Fold in chocolate chips and drop dough onto baking sheets', 3, 'Scooping', 'Room', '["chocolate chips"]'),
(15, 3, 6, 'Bake for 10-12 minutes until edges are golden brown', 12, 'Baking', 'Medium', '[]');

INSERT INTO recipe_reviews (recipe_id, user_id, reviewed_at, rating, comment) VALUES
(1, 2, CURRENT_TIMESTAMP, 5, 'Absolutely delicious! Perfect creamy texture.'),
(1, 3, CURRENT_TIMESTAMP, 4, 'Great recipe, but I used bacon instead of pancetta.'),
(2, 1, CURRENT_TIMESTAMP, 5, 'So healthy and filling! Love the colors.'),
(3, 4, CURRENT_TIMESTAMP, 5, 'Best chocolate chip cookies I have ever made!'),
(3, 5, CURRENT_TIMESTAMP, 4, 'My family loved them! Will make again.'),
(4, 2, CURRENT_TIMESTAMP, 4, 'Quick and tasty weeknight dinner.'),
(5, 1, CURRENT_TIMESTAMP, 5, 'Authentic Greek flavors! Perfect summer salad.'),
(6, 3, CURRENT_TIMESTAMP, 4, 'Kids loved making their own tacos!'),
(7, 4, CURRENT_TIMESTAMP, 5, 'Comforting and healthy. Perfect for cold days.'),
(8, 5, CURRENT_TIMESTAMP, 5, 'My new favorite breakfast! So refreshing.');


UPDATE tags SET usage_count = (
  SELECT COUNT(*) FROM recipe_tags WHERE tag_id = tags.id
);
