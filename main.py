import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime

# Setting paths and constants
_path = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(_path, 'member-data.csv')
JSON_PATH = os.path.join(_path, 'member-data.json')
REFERENCE_DATE = pd.to_datetime('2024-03-01')

# 'True' to output the JSON file, 'False' to use MongoDB
OUTPUT_JSON = False
# Please specify your MongoDB database name and collection name
MongoDB_DB_NAME = 'member_data'
MongoDB_COLLECTION_NAME = 'members'


def read_csv(file_path):
    # Define the column names and types
    column_names = ['FirstName', 'LastName', 'Company', 'BirthDate', 'Salary', 'Address', 'Suburb', 'State', 'Post',
                    'Phone', 'Mobile', 'Email']
    column_types = {'FirstName': str, 'LastName': str, 'Company': str, 'BirthDate': str, 'Salary': float,
                    'Address': str, 'Suburb': str, 'State': str, 'Post': int, 'Phone': str, 'Mobile': str, 'Email': str}

    def date_parser(date_string):
        # Deal with the N/A
        if pd.isna(date_string):
            return None
        try:
            # Remove the ".0" at the end of the string
            date_string = str(int(date_string))
            return datetime.strptime(date_string, '%d%m%Y')
        except ValueError:
            # For the illegal input, such as the case the day is out of range for month, return none.
            print(f"Invalid date input: {date_string}")
            return None

            # Read the CSV file and parse the date column

    df = pd.read_csv(file_path, sep='|', names=column_names, dtype=column_types, parse_dates=['BirthDate'],
                     date_parser=date_parser).dropna()

    return df


def calculate_age(data):
    # Convert 'BirthDate' back to datetime type
    data['BirthDate'] = pd.to_datetime(data['BirthDate'], format='%d/%m/%Y')
    # Calculate age
    data['Age'] = ((REFERENCE_DATE - data['BirthDate']).dt.days // 365.25).astype(int)
    # Convert 'BirthDate' back to 'DD/MM/YYYY' format
    data['BirthDate'] = data['BirthDate'].dt.strftime('%d/%m/%Y')

    return data


def calculate_salary_buckets(data):
    """
    Calculate the salary buckets based on the salary values:
        A for employees earning below 50.000
        B for employees earning between 50.000 and 100.000
        C for employees earning above 100.000
    """
    # Remove the dollar sign and commas from the 'Salary' column and convert it back to float
    data['Salary_temp'] = pd.to_numeric(data['Salary'].replace({'\$': '', ',': ''}, regex=True), errors='coerce')

    conditions = [
        (data['Salary_temp'] < 50000),
        (data['Salary_temp'] >= 50000) & (data['Salary_temp'] <= 100000),
        (data['Salary_temp'] > 100000)
    ]
    # Define the category labels for the salary categories
    labels = ['A', 'B', 'C']

    # Create the 'SalaryBucket' column
    data['SalaryBucket'] = np.select(conditions, labels)
    data.drop('Salary_temp', axis=1, inplace=True)

    return data


def drop_columns(data, *cols):
    data.drop(list(cols), axis=1, inplace=True)
    return data


def create_nested_address(data):
    """
    Build nested column named 'Address' to store the address information, including:
    'Address', 'Suburb', 'State', 'Post'.
    The address information is saved as a dictionary.
    """
    data['Address'] = data[['Address', 'Suburb', 'State', 'Post']].apply(lambda row: row.to_dict(), axis=1)
    data = drop_columns(data, 'Suburb', 'State', 'Post')

    return data


def transform_data(data):
    # Convert 'BirthDate' to 'DD/MM/YYYY' format
    data['BirthDate'] = data['BirthDate'].dt.strftime('%d/%m/%Y')

    # Convert 'Salary' to dollar format with commas
    data['Salary'] = data['Salary'].apply(lambda x: '${:,.2f}'.format(x))

    # Remove the leading/trailing spaces on FirstName and LastName columns
    data['FirstName'] = data['FirstName'].str.strip()
    data['LastName'] = data['LastName'].str.strip()

    # Merge the FirstName and LastName columns into a new column named FullName
    data['FullName'] = data['FirstName'] + " " + data['LastName']
    data = drop_columns(data, 'FirstName', 'LastName')

    # Calculate the age and add it to the new column named 'Age'
    data = calculate_age(data)

    # Add a new column named SalaryBucket to categorize the employees based on their salary
    data = calculate_salary_buckets(data)

    # Build nested entity class to have address as nested class as required
    data = create_nested_address(data)

    # Reorder the columns to make it more user-friendly
    data = data[
        ['FullName', 'Company', 'BirthDate', 'Age', 'Salary', 'SalaryBucket', 'Address', 'Phone', 'Mobile', 'Email']]
    return data


def load_data_MongoDB(data):
    """
    Connects to the MongoDB database and inserts the given data into a predefined collection.
    """

    # Create a connection to the MongoDB instance
    client = MongoClient("mongo", 27017)

    # List all database names
    db_list = client.list_database_names()

    # Create a new database named 'member_data' if it does not exist
    if MongoDB_DB_NAME not in db_list:
        db = client[MongoDB_DB_NAME]
        print("Database created successfully!")
    else:
        db = client[MongoDB_DB_NAME]

    # Create a new collection named 'members' if it does not exist
    collection = db[MongoDB_COLLECTION_NAME]

    # Insert the data into the collection
    data = data.to_dict('records')
    collection.insert_many(data)

    # Close the connection
    client.close()

    print("Data loaded successfully!")

def load_data(data, file_path=JSON_PATH):
    if OUTPUT_JSON:
        data.to_json(file_path, orient='records', indent=4)
        print("Data loaded as a json file successfully!")
    else:
        load_data_MongoDB(data)

def main():
    data = read_csv(CSV_PATH)
    data = transform_data(data)
    load_data(data, JSON_PATH)


if __name__ == "__main__":
    main()
