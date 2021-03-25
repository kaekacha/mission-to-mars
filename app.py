from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")#this name at the end doesn't matter

# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Find one record of data from the mongo database
    mars = mongo.db.mars.find_one() #collection is called mars; variable on the left can be called anything

    # Return template and data
    return render_template("index.html", mars=mars)

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    mars = mongo.db.mars

    # Run the scrape function
    mars_scraped_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    mongo.db.mars.update({}, mars_scraped_data, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)