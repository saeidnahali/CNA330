# This script pulls from a job website and stores positions into a database. If there is a new posting it notifies the user.
# Mohammad Pakizeh Jam
# CNA330 11/12/2020
import mysql.connector
import sys
import json
import urllib.request
import os
import time
from datetime import datetime

# Connect to database
# You may need to edit the connect function based on your local settings.
def connect_to_sql():
    conn = mysql.connector.connect(user='pythoneverything', password='python123',
                                  host='18.216.19.4',
                                  database='cna330')
    return conn
# Create the table structure
def create_tables(cursor, table):
    ## Add your code here. Starter code below
    cursor.execute('''CREATE TABLE IF NOT EXISTS Jobs (ID INT PRIMARY KEY auto_increment, 
    Type varchar(10), 
    Title varchar(100), 
    Description text CHARSET utf8,
    Job_id varchar(36), 
    Created_at DATE, 
    Company varchar(100), 
    Location varchar(100), 
    How_to_apply varchar(1000)); ''')
    return
# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor
# Add a new job
def add_new_job(cursor, jobdetails):
    ## Add your code here
    query = "INSERT INTO"
    type = jobdetails['type']
    created_at = time.strptime(jobdetails['created_at'], "%a %b %d %H:%M:%S %Z %Y")
    company = jobdetails['company']
    location = jobdetails['location']
    title = jobdetails['title']
    description = jobdetails['description']
    how_to_apply = jobdetails['how_to_apply']
    job_id = jobdetails['id']
    query = cursor.execute("INSERT INTO Jobs(Type, "
                              "Title, Description, "
                              "Job_id, Created_at, "
                              "Company, Location, "
                              "How_to_apply" ") "
               "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (type, title, description, job_id,
                                                   created_at, company, location, how_to_apply))
    return query_sql(cursor, query)
# Check if new job
def check_if_job_exists(cursor, jobdetails):
    ## Add your code here
    query = "SELECT"
    job_id = jobdetails['id']
    query = "SELECT * FROM Jobs WHERE Job_id = \"%s\"" % job_id
    return query_sql(cursor, query)
def delete_job(cursor, jobdetails):
    ## Add your code here
    query = "UPDATE"
    job_id = jobdetails['id']
    query = "DELETE FROM Jobs WHERE Job_id = \"%s\"" % job_id
    return query_sql(cursor, query)
# Grab new jobs from a website
def fetch_new_jobs(arg_dict):
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/Sql.py
    query = "https://jobs.github.com/positions.json?" + "location=seattle" ## Add arguments here
    query = "https://jobs.github.com/positions.json?search=SQL&location=Remote"
    jsonpage = 0
    try:
        contents = urllib.request.urlopen(query)
        response = contents.read()
        jsonpage = json.loads(response)
    except:
        pass
    return jsonpage
# Load a text-based configuration file
def load_config_file(filename):
    argument_dictionary = 0
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/FileIO.py
    rel_path = os.path.abspath(os.path.dirname(__file__))
    file = 0
    file_contents = 0
    try:
        file = open(filename, "r")
        file_contents = file.read()
    except FileNotFoundError:
        print("File not found, it will be created.")
        file = open(filename, "w")
        file.write("")
        file.close()
    ## Add in information for argument dictionary
    return argument_dictionary
# Main area of the code.
def jobhunt(cursor, arg_dict):
    # Fetch jobs from website
    jobpage = fetch_new_jobs(arg_dict)
    # print (jobpage)
    add_or_delete_job(cursor, jobpage)
def add_or_delete_job(cursor, jobpage):
    ## Add your code here to parse the job page
    for jobdetails in jobpage:
    ## Add in your code here to check if the job already exists in the DB
        check_if_job_exists(cursor, jobdetails)
        is_job_found = len(cursor.fetchall()) > 0
        if is_job_found:
        ## EXTRA CREDIT: Add your code to delete old entries
            now = datetime.now()
            job_date = datetime.strptime(jobdetails['created_at'], "%a %b %d %H:%M:%S %Z %Y")
            if (now - job_date).days > 30:
                print("Delete job: " +
                      jobdetails["title"] +
                      " from " + jobdetails["company"] +
                      ", Created at: " + jobdetails["created_at"] +
                      ", JobID: " + jobdetails['id'])
                delete_job(cursor, jobdetails)
        else:
            ## Add in your code here to notify the user of a new posting
            print("New job is found: " +
                  jobdetails["title"] +
                  " from " + jobdetails["company"] +
                  ", Created at: " + jobdetails["created_at"] +
                  ", JobID: " + jobdetails['id'])
            add_new_job(cursor, jobdetails)
# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor, "table")
    # Load text file and store arguments into dictionary
    arg_dict = 0
    while(1):
        jobhunt(cursor, arg_dict)
        conn.commit()
        time.sleep(3600)  # Sleep for 1h
if __name__ == '__main__':
    main()
