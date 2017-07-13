#!/usr/bin/env python
from splinter import Browser
from dotenv import load_dotenv, find_dotenv
import time, os, sys

#collect login data collected from .env
load_dotenv(find_dotenv())
PSWD = os.getenv('PASSWORD')
URI = os.getenv('LISTSERV_URI')

# Check that data is set in the .env
assert PSWD, "No password in .env\nAborting"
assert URI, "No uri in .env\nAborting"

#suppress stderr because of ignorable selenium or requests warnings
sys.stderr = open(os.devnull, 'w')

#lists to be filled with scraped data
web_emails = [] #format: ["email"]
db_emails = [] #format: ["email"]
db_content = {} #format: key="email" value="lname fname"

''' These strings store newline separated emails to be added to or removed
    from the webserv depending on the contents of the database and webserv.
'''
add_emails = "" #"lname fname <email>\n..."
rm_emails = "" #"email\n..."

#TODO: Replace with real database commands
def setDB_Content(f):
    ''' Collects the emails from the "database" to be used later
    '''
    global db_content
    global db_emails

    with open(f, 'r') as file:
        for line in file:
            lname, fname, email = line.split()
            db_content[email] = lname + ' ' + fname
    db_emails = db_content.keys()

#TODO: Replace with real database commands
def getDB_Content(email):
    ''' Takes an email known to be in the database and returns a string
        with the associated first and last name
    '''
    global db_content

    try:
        return db_content[email]
    except:
        return ' '
        
def update():
    ''' compares email lists and appends data to appropriate add/rm_email data structs.
        * if (email in webserv but not datatbase) remove;
        * if (email in database but not webserv) add;
    '''
    global web_emails
    global db_emails
    global rm_emails
    global add_emails
    
    log("Comparing emails found on webserv with emails in database")

    #compares every email from the webserv to those found in the database
    for web_data in web_emails:
        if web_data not in db_emails: #if true, then that email must be removed
            rm_emails += web_data + '\n'
    
    #compares every email from the database to those found in the webserv
    for db_data in db_emails:
        if db_data not in web_emails: #if true, then that email must be added
            add_emails += getDB_Content(db_data)  + ' <' + db_data + '>\n'

    removeEmails(rm_emails)

    addEmails(add_emails)

def log(message):
    ''' logs in the format of: "timestamp removed/added email"
        time stamp in the format: "YYYY-mm-dd hh:mm:ss"
    '''
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message)

def removeEmails(e, l="enable"):  #remove all emails on the site
    ''' e: string of emails newline separated
        l: is a flag whether or not to log the action, the default is to log
    '''
    browser.visit(URI + '/members/remove')
    browser.fill('unsubscribees', e)
    browser.find_by_name('setmemberopts_btn').click()

    if l == "enable":
        for email in e.split('\n')[:-1]:
            log("removed " + email)

def addEmails(e, l="enable"):  #remove all emails on the site
    ''' e: string of emails newline separated
        l: is a flag whether or not to log the action, the default is to log
    '''
    browser.visit(URI + '/members/add')
    browser.fill('subscribees', e)
    browser.find_by_name('setmemberopts_btn').click()

    if l == "enable":
        for email in e.split('\n')[:-1]:
            log("added " + email.split('<')[1][:-1])
        
#go to mailserv site and login
browser = Browser('phantomjs') #remove 'phantomjs' to use default firefox
browser.visit(URI)
browser.fill('adminpw',PSWD)
browser.find_by_name('admlogin').click()

#navigate to membership management
browser.visit(URI + '/members/list')

setDB_Content("mixEmails.txt")
log("Database data is collected")

temp=''
while browser.is_text_not_present('0 members total'): #emails found
    log("Grabbing data from webserv...")
    links = browser.find_link_by_partial_href('--at--')

    for a in links:
        web_emails.append(a.value)
        temp += getDB_Content(a.value) + ' <' + a.value + '>\n'
    
    removeEmails(temp, "disable")
    browser.visit(URI + '/members/list')
#else no emails
addEmails(temp, "disable")
log("Webserv data is collected")

update()
log("Webserv and Database are synced")

#logout before exiting
browser.visit(URI + '/logout')
browser.quit()

#reset stderr
sys.stderr = sys.__stderr__
