# 🍳 Instagram Recipe Extractor
**Turn Instagram’s recipe chaos into a chef’s dream.**

A cutting-edge web application that transforms Instagram recipe posts into beautifully structured, searchable formats. Powered by web scraping, OpenAI’s AI magic, and a sleek interface, this app makes cooking inspiration from Instagram easier than ever!

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Framework: Flask](https://img.shields.io/badge/Framework-Flask-00d9ff)](https://flask.palletsprojects.com/)
[![Language: Python](https://img.shields.io/badge/Python-3.8%2B-3776ab.svg)](https://www.python.org/)

---

## 🌟 Features

✅ **Extract Recipes from Instagram Posts:** Input any Instagram URL, and let the app work its magic.

✅ **Recipe Parsing:** Converts messy captions into well-structured ingredients and instructions.

✅ **Recipe Caching:** Stop wasting time! Revisit previously fetched recipes instantly with built-in caching.

✅ **Database Integration:** All your recipes stored securely in SQLite and searchable by name.

✅ **User-Friendly Interface:** Navigate, submit links, and explore recipes with an intuitive web design.

✅ **Search Functionality:** Quickly find that one amazing chocolate cake recipe by name.

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

Before you start cooking up some recipes, make sure you’ve got:

- 🐍 **Python 3.8+**
- 🌐 **Google Chrome** and **ChromeDriver** (for Instagram scraping).
- 📦 Required Python libraries (installed via `requirements.txt`).

---

### 2️⃣ Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/instagram-recipe-extractor.git
   cd instagram-recipe-extractor
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database:**

   ```bash
   python app.py
   ```

   (The SQLite database `recipes.db` will be created automatically on the first run.)


---

### 3️⃣ Run the App

1. Start the Flask server:

   ```bash
   python app.py
   ```

2. Open your browser and go to:

   ```
   http://127.0.0.1:5000
   ```

3. Use the app to:
   - **Submit Instagram links** and extract recipes.
   - **Browse recipes** in the database.
   - **Search by recipe name** to find your favorites.

---

## 🌍 API Endpoints

- **Submit a Recipe:**

  **POST** `/submit`
  Input an Instagram URL to fetch and parse a recipe.

- **List Recipes:**

  **GET** `/recipes`
  Fetch all stored recipes. Use `?search=<name>` for filtering.

- **View a Recipe:**

  **GET** `/recipes/<recipe_id>`
  Retrieve a single recipe by its ID.
  Add `?format=json` for a JSON response.

---

## 🎉 Why You’ll Love It

✨ **No More Manual Work:** Let AI and automation handle the dirty work of scraping, structuring, and storing recipes for you.

✨ **Everything in One Place:** A single app to explore, save, and organize recipes from Instagram posts.

✨ **Cook Smarter, Not Harder:** Access clear ingredient lists and instructions anytime you want to try something new.

---

## 🤝 Contributing

💡 **Got an idea?** We’d love to hear it! Here’s how to contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a pull request.


---

## 💌 Contact

Got questions or feedback? Reach out at [daniel@alves.com](mailto:daniel@alves.world).
