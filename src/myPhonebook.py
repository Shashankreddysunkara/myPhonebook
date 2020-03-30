#!/usr/bin/env python

from prometheus_client import generate_latest, REGISTRY, Counter, Summary
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-dbh', '--dbhost', default='mysql.service.consul', type=str)
parser.add_argument('-u', '--username', default='phoneapp', type=str)
parser.add_argument('-psw', '--password', default='123456', type=str)
parser.add_argument('-p', '--port', default='3306', type=str)
parser.add_argument('-db', '--database', default='phonebook', type=str)
parser.add_argument('-l', '--log', default='info', choices=['debug', 'info', 'warning'])

args = parser.parse_args()

# log config
logging.basicConfig(format='%(asctime)s: %(message)s')
logger = logging.getLogger("ExtractDeviceMetrics")
if args.log == "info":
    logger.setLevel(logging.INFO)
elif args.log == "debug":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)

# A counter to count the total number of HTTP requests
REQUESTS = Counter('http_requests_total', 'Total HTTP Requests (count)', 
        ['method', 'endpoint', 'status_code'])
TIME_METRIC = Summary('http_request_processing_seconds', 
        'Time spent processing request', ['method'])

#define connection
app = Flask("MyApp")

conn = mysql.connector.connect(
         user=args.username,
         password=args.password,
         host=args.dbhost,
         port=args.port,
         database=args.database)

#opens connection
cur = conn.cursor()
activeTab = {"home":"", "addEntries":"", "updateEntry":""}

#Grab all db entries, cast tuples to a list, then for each.
listings_timer = TIME_METRIC.labels(method="listings")
@app.route("/")
@listings_timer.time()
def listings():
    REQUESTS.labels(method='GET', endpoint="/", status_code=200).inc() 
    query = ("SELECT id,name,email,phone FROM phonebook")
    try:
        cur.execute(query)
        logger.info("Listing all database info")
        l = []
        for each in cur.fetchall():
            l.append(list(each))
        setActiveTab("home")
        return render_template("listings.html", contact_list=l, title="My Phonebook", activeTab=activeTab)
    except mysql.connector.Error as err:
        logging.error(err)

updateEntry_timer = TIME_METRIC.labels(method="updateEntry")
@app.route("/update_entry")
@updateEntry_timer.time()
def updateEntry(methods=['GET']):
    REQUESTS.labels(method='GET', endpoint="/update_entry", status_code=200).inc()
    id = request.args.get('id')
    query = ("SELECT id,name,email,phone FROM phonebook WHERE id = '%s'" % id)
    try:
        cur.execute(query)
        list = cur.fetchone()
        setActiveTab("updateEntry")
        logger.info("Selecting data to update")
        return render_template("update_entry.html", phonebook=list, title="My Phonebook", activeTab=activeTab)
    except mysql.connector.Error as err:
        logging.error(err)

# set all active tab dictionaries value to "" then make the indicated tab from the flask route function active. 
# This make class="active" for css styling dynamically.
def setActiveTab(tabName):
    global activeTab
    for tab in activeTab:
        activeTab[tab] = ""
    if tabName in activeTab:
        activeTab[tabName] = "active"
    logger.debug("Active tab is: {}".format(activeTab))
    print(activeTab)

new_entry_timer = TIME_METRIC.labels(method="new_entry")
@app.route("/new_entry")
@new_entry_timer.time()
def new_entry():
    REQUESTS.labels(method='GET', endpoint="/new_entry", status_code=200).inc() 
    setActiveTab("addEntries")
    return render_template("new_entry.html", title="My Phonebook",activeTab=activeTab)

# check if this page is being reached from a POST. If not, ignore functions. Otherwise check filename is safe,
#  grab the ext of the image file for storage in the db and insert new entry.
# After entry is stored, get the new id from db and use it plus '.' plus ext to save the image to the server.
submit_new_entry_timer = TIME_METRIC.labels(method="submit_new_entry")
@app.route("/submit_new_entry", methods=['POST'])
@submit_new_entry_timer.time()
def submit_new_student():
    REQUESTS.labels(method='GET', endpoint="/submit_new_entry", status_code=200).inc() 
    setActiveTab("addEntries")
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        query = ("SELECT MAX(id) FROM phonebook")
        try:
            cur.execute(query)
            records = cur.fetchone()
            newid = int(records[0]) + 1
            logger.debug("New id is: {}".format(str(newid)))
            query = "insert into phonebook (id, name, email, phone) values ({},'{}','{}','{}')".format(newid, name, email, phone)
            try:
                cur.execute(query)
                conn.commit()
                lastId = cur.lastrowid
                logger.info("Created a new student - id: {}, name: {}, email: {}, phone: {}".format(newid, name, email, phone))
            except mysql.connector.Error as err:
                logging.error(err)    
        except mysql.connector.Error as err:
            logging.error(err)
    # return render_template("submit_new_entry.html", name=name,email=email,phone=phone, activeTab=activeTab)
    return redirect("/")

#Need to add ability to update images. Have to move on for now. To do: Extract image upload with overwrite to an outsidefunction either new_contact or update_contact can make use of.
submit_update_contact_timer = TIME_METRIC.labels(method="submit_update_contact")
@app.route("/submit_update_contact", methods=['POST'])
@submit_update_contact_timer.time()
def submit_update_contact():
    REQUESTS.labels(method='GET', endpoint="/submit_update_contact", status_code=200).inc() 
    id = request.form.get('id')
    setActiveTab("updateEntry")
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    if request.form['submit'] == 'update':
        query = "UPDATE phonebook SET name = '%s', email = '%s', phone = '%s' WHERE id = '%s'" % (name,email,phone, id)
        try:
            cur.execute(query)
            conn.commit()
            logger.info("Update a student - id: {}, name: {}, email: {}, phone: {}".format(id, name, email, phone))
        except mysql.connector.Error as err:
            logging.error(err)
    if request.form['submit'] == 'delete':
        query = "DELETE FROM phonebook WHERE id = '%s'" % id
        logger.info("Deleting student - id: {}".format(id))
        try:
            cur.execute(query)
            conn.commit()
        except mysql.connector.Error as err:
            logging.error(err)
    return redirect("/")

@app.route('/metrics')
def metrics():
    REQUESTS.labels(method='GET', endpoint="/metrics", status_code=200).inc()
    return generate_latest(REGISTRY)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)

cur.close()
conn.close()
