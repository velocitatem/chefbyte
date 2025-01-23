import os
import time
import json
import re
from datetime import datetime
from typing import List

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()


# SQLAlchemy Imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime

# ------------------------------------------------------------------------------
# FLASK SETUP
# ------------------------------------------------------------------------------
app = Flask(__name__)

# Configure a local SQLite database for demonstration
# (You can configure Postgres, MySQL, etc. in production)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recipes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------------------------------------------------------------------
# DATABASE MODEL
# ------------------------------------------------------------------------------
class RecipeDB(db.Model):
    """
    Stores the recipe in the database
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    recipe_name = Column(String(200), nullable=False)
    recipe_data = Column(Text, nullable=False)  # We'll store entire JSON as text
    date_added = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RecipeDB {self.recipe_name}>"


# ------------------------------------------------------------------------------
# Pydantic MODELS (for typed data structures)
# ------------------------------------------------------------------------------
class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str
    optional: bool

class RecipeSchema(BaseModel):
    name: str
    ingredients: List[Ingredient]
    instructions: List[str]


# decorator for the get recipe function in a json file cache
def cache_recipe(func):
    def wrapper(url):
        # check if the recipe is in the cache
        if os.path.exists("recipe_cache.json"):
            with open("recipe_cache.json", "r") as f:
                cache = json.load(f)
                if url in cache:
                    return cache[url]
        # if not in cache, get the recipe
        recipe = func(url)
        # save the recipe in the cache
        with open("recipe_cache.json", "rw") as f:
            cache = json.load(f)
            cache[url] = recipe
            json.dump(cache, f)
        return recipe
    return wrapper

# decorator for the extraction cache
def cache_extraction(func):
    def wrapper(description):
        # check if the recipe is in the cache
        if os.path.exists("extraction_cache.json"):
            with open("extraction_cache.json", "r") as f:
                cache = json.load(f)
                if description in cache:
                    return cache[description]
        # if not in cache, get the recipe
        recipe = func(description)
        # save the recipe in the cache
        with open("extraction_cache.json", "rw") as f:
            cache = json.load(f)
            cache[description] = recipe
            json.dump(cache, f)
        return recipe
    return wrapper





# ------------------------------------------------------------------------------
# HELPER FUNCTIONS (Core logic from your original code)
# ------------------------------------------------------------------------------
def get_recipe(url: str):
    """
    Get the description of an Instagram post and turn it into a structured recipe
    """
    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")  # Run browser in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Launch the browser
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # Instagram caption is often in the og:description meta tag
        try:
            description = driver.find_element(
                By.XPATH, "//meta[@property='og:description']"
            ).get_attribute("content")
        except Exception as e:
            print("Error fetching description:", e)
            description = ""
    finally:
        driver.quit()

    # Parse the description into a structured recipe
    try:
        recipe = extract_recipe(description)
        return recipe
    except Exception as e:
        print("Error extracting recipe:", e)
        return {"error": str(e), "description": description}


def extract_recipe(description: str):
    """
    Extract ingredients from a recipe description using OpenAI
    """
    # If you wanted to do a real call:
    # FUTURE TODO: small model and local
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Extract the recipe information."},
            {"role": "user", "content": description}
        ],
        response_format=RecipeSchema
    )
    return completion.choices[0].message.parsed


# ------------------------------------------------------------------------------
# VIEWS & ROUTES
# ------------------------------------------------------------------------------

# Simple HTML templates with inline strings for demonstration purposes
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Recipe Extractor</title>
</head>
<body>
    <h1>Instagram Recipe Extractor</h1>
    <p>Use the links to navigate:</p>
    <ul>
      <li><a href="{{ url_for('submit_recipe') }}">Submit a new Recipe</a></li>
      <li><a href="{{ url_for('list_recipes') }}">View all Recipes</a></li>
    </ul>
</body>
</html>
"""

SUBMIT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Instagram Link</title>
</head>
<body>
    <h1>Submit an Instagram Link</h1>
    <form method="POST" action="{{ url_for('submit_recipe') }}">
        <label for="url">Instagram URL:</label>
        <input type="text" name="url" id="url" placeholder="https://www.instagram.com/reel/XYZ..." required>
        <button type="submit">Fetch & Save Recipe</button>
    </form>
    <br>
    <a href="{{ url_for('home') }}">Back to Home</a>
</body>
</html>
"""

LIST_RECIPES_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>All Recipes</title>
</head>
<body>
    <h1>Stored Recipes</h1>
    <p>Below is a list of all the recipes in the database:</p>
    <ul>
    {% for recipe in recipes %}
      <li>
        <a href="{{ url_for('view_recipe', recipe_id=recipe.id) }}">
            {{ recipe.recipe_name }}
        </a>
      </li>
    {% endfor %}
    </ul>

    <hr>
    <p>Search by Recipe Name:</p>
    <form method="GET" action="{{ url_for('list_recipes') }}">
        <input type="text" name="search" placeholder="Recipe name...">
        <button type="submit">Search</button>
    </form>
    <br>
    <a href="{{ url_for('home') }}">Back to Home</a>
</body>
</html>
"""

VIEW_RECIPE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Recipe Detail</title>
</head>
<body>
    <h1>{{ recipe_name }}</h1>
    <p><strong>Added on:</strong> {{ date_added }}</p>
    <p><strong>Ingredients:</strong></p>
    <ul>
      {% for ing in recipe_data.ingredients %}
        <li>
          {{ ing.quantity }} {{ ing.unit }} of {{ ing.name }}
          {% if ing.optional %}(optional){% endif %}
        </li>
      {% endfor %}
    </ul>
    <p><strong>Instructions:</strong></p>
    <ol>
      {% for step in recipe_data.instructions %}
        <li>{{ step }}</li>
      {% endfor %}
    </ol>

    <br>
    <a href="{{ url_for('list_recipes') }}">Back to List</a> |
    <a href="{{ url_for('home') }}">Home</a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/submit", methods=["GET", "POST"])
def submit_recipe():
    """
    Page to submit an Instagram link.
    On POST, scrape and parse the recipe, then store in the database.
    """
    if request.method == "GET":
        return render_template_string(SUBMIT_HTML)
    else:
        # Handle form submission
        url = request.form.get("url")
        if not url:
            return "Please provide a URL.", 400

        # Extract recipe
        recipe = get_recipe(url)  # returns a dict with the pydantic structure
        # If there's an error, recipe_dict might not have the expected keys
        # pydantic to json
        recipe_dict = recipe.dict()


        # Save to DB
        recipe_name = recipe_dict.get("name", "Unknown Recipe")
        # Convert to a string to store in DB, you could also store individual fields
        import json
        recipe_json = json.dumps(recipe_dict, ensure_ascii=False)

        new_record = RecipeDB(
            recipe_name=recipe_name,
            recipe_data=recipe_json
        )
        db.session.add(new_record)
        db.session.commit()

        return redirect(url_for('list_recipes'))

@app.route("/recipes", methods=["GET"])
def list_recipes():
    """
    List all recipes in the database or filtered by a 'search' query param.
    """
    search_query = request.args.get("search", "")
    if search_query:
        # Basic case-insensitive name filter
        results = RecipeDB.query.filter(
            RecipeDB.recipe_name.ilike(f"%{search_query}%")
        ).all()
    else:
        results = RecipeDB.query.order_by(RecipeDB.date_added.desc()).all()

    return render_template_string(LIST_RECIPES_HTML, recipes=results)


# add options to do ?format=json
@app.route("/recipes/<int:recipe_id>", methods=["GET"])
def view_recipe(recipe_id):
    """
    Display the details of a single recipe.
    """
    record = RecipeDB.query.get_or_404(recipe_id)

    # Parse the stored JSON
    import json
    recipe_data = json.loads(record.recipe_data)

    if request.args.get("format") == "json":
        return jsonify(recipe_data)

    return render_template_string(
        VIEW_RECIPE_HTML,
        recipe_name=record.recipe_name,
        date_added=record.date_added,
        recipe_data=recipe_data
    )


# ------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create the DB if it doesn't exist
    with app.app_context():
        db.create_all()

    # Start the Flask server
    app.run(debug=True, host="0.0.0.0", port=5000)
