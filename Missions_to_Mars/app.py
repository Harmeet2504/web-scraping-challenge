from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection to database, mars_app
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# Route to render index.html template using data from Mongo
@app.route("/")
def index():

    # Find one record (collection-mars) of data from the mongo database
    destination_data = mongo.db.mars.find_one()

    # Return template and data
    return render_template("index.html", mars=destination_data)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    # Run the scrape function to fetch data in the form of dictionary
    mars_data = scrape_mars.scrape_all()

    # Update the Mongo database collection (mars) using update and upsert=True
    mars.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")
    


if __name__ == "__main__":
    app.run(debug=True)