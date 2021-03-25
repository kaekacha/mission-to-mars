from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")#this name at the end doesn't matter

# Route to render index.html template using data from Mongo
@app.route("/", methods=("POST", "GET"))
def home():

    # Find one record of data from the mongo database; if it does not exist, this creates a new collection
    mars = mongo.db.collection.find_one()

    #run function to create table
    df = scrape_mars.scrape_table()

    # Return template and data; utilized this documentation for the table: https://stackoverflow.com/questions/52644035/how-to-show-a-pandas-dataframe-into-a-existing-flask-html-table
    return render_template("index.html", mars=mars,tables = [df.to_html(classes='data', header=True)])

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    mars = mongo.db.collection

    # Run the scrape function
    mars_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    mars.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)