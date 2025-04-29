from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import db_connection

# Flask application setup
app = Flask(__name__)

# MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/DBMS_PROJECT" # Adjust as per your setup
mongo = PyMongo(app)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Add Data
@app.route('/add', methods=['GET', 'POST'])
def add_data():
    # Define collection fields
    collection_fields = {
        'waterbodies': ['WaterBodyID', 'Name', 'Type', 'Status'],
        'Location': ['LocationID', 'Latitude', 'Longitude'],
        'LocatedAt': ['WaterBodyID', 'LocationID', 'Area'],
        'Survey': ['SurveyID', 'SurveyorName', 'Date', 'Observations'],
        'conducts': ['SurveyID', 'WaterBodyID', 'ConductedBy']
    }

    collections = collection_fields.keys()  # Extract collection names
    message = None  # Default message

    if request.method == 'POST':
        # Get the selected collection and corresponding fields
        collection_name = request.form['collection']
        fields = collection_fields.get(collection_name, [])
        
        # Construct the data dictionary
        data = {}
        for field in fields:
            value = request.form.get(field)
            
            # Typecast relevant fields to integer
            if field in ['WaterBodyID', 'SurveyID', 'LocationID']:
                try:
                    value = int(value)
                except :
                    message = f"Error: '{field}' must be an integer."
                    return render_template('add.html', collections=collections, collection_name=collection_name, fields=fields, message=message)
            
            data[field] = value

        # Validate unique fields (e.g., WaterBodyID, SurveyID, LocationID)
        unique_field = fields[0]  # Assuming the first field is unique (e.g., WaterBodyID, SurveyID)
        if not data.get(unique_field):
            message = f"Error: '{unique_field}' cannot be empty."
        elif mongo.db[collection_name].find_one({unique_field: data[unique_field]}):
            message = f"Error: '{unique_field}' already exists in {collection_name}."
        else:
            mongo.db[collection_name].insert_one(data)
            message = f"Data added to {collection_name} successfully!"

        # Return updated view
        return render_template('add.html', collections=collections, collection_name=collection_name, fields=fields, message=message)

    # Default view for the Add Data form
    return render_template('add.html', collections=collections, collection_name=None, fields=None, message=None)
# Delete Data
@app.route('/delete', methods=['GET', 'POST'])
def delete_data():
    tables = ['waterbodies', 'conducts', 'Survey', 'LocatedAt', 'Location']
    if request.method == 'POST':
        table_name = request.form['table']
        if 'row_id' in request.form:
            row_id = request.form['row_id']
            mongo.db[table_name].delete_one({"_id": ObjectId(row_id)})
            message = f"Row with ID {row_id} deleted from {table_name} successfully!"
        else:
            message = None
        table_data = list(mongo.db[table_name].find())
        return render_template('delete.html', tables=tables, table_name=table_name, table_data=table_data, message=message)
    return render_template('delete.html', tables=tables, table_name=None, table_data=None, message=None)

# Show Data
@app.route('/show', methods=['GET', 'POST'])
def show_data():
    tables = ['waterbodies', 'conducts', 'Survey', 'LocatedAt', 'Location']  # Your table names
    table_name = None
    table_data = None

    if request.method == 'POST':
        table_name = request.form.get('table')  # Retrieve selected table from the form
        if table_name in tables:  # Ensure the table exists in your database
            table_data = list(mongo.db[table_name].find())
        else:
            table_data = []  # Handle invalid table name

    return render_template('show.html', tables=tables, table_name=table_name, table_data=table_data)
if __name__ == '__main__':
    app.run(debug=True)