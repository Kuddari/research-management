import os
import pandas as pd
from sqlalchemy import create_engine

# Optionally load environment variables
from dotenv import load_dotenv
load_dotenv()

# Construct the DATABASE_URL using environment variables
DATABASE_URL = f"postgresql://{os.environ['DATABASE_USER']}:{os.environ['DATABASE_PASSWORD']}@{os.environ['DATABASE_HOST']}:{os.environ['DATABASE_PORT']}/{os.environ['DATABASE_NAME']}"

# Create a database engine
engine = create_engine(DATABASE_URL)

def load_excel(file_name, table_name):
    # Read the Excel file
    df = pd.read_excel(file_name)
    # Insert the data into the PostgreSQL database
    df.to_sql(table_name, engine, if_exists='append', index=False)

if __name__ == "__main__":
    # Map your Excel files to the respective PostgreSQL table names
    files_to_tables = {
        "Zone.xlsx":"researchapp_zone",
        "Province.xlsx": "researchapp_province",
        "District.xlsx": "researchapp_district",
        "SubDistrict.xlsx": "researchapp_subdistrict",
    }

    for file, table in files_to_tables.items():
        # Use 'append' to add data to the existing table
        load_excel(file, table)
        print(f"Loaded {file} into {table} table.")
