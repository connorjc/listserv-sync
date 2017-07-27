#!/usr/bin/env python
from splinter import Browser
from dotenv import load_dotenv, find_dotenv
import time, os, sys

def login(site, uri, pswd):
    site.visit(uri)
    site.fill('adminpw',pswd)
    site.find_by_name('admlogin').click()

def logout(site, uri):
    site.visit(URI + '/logout')
    site.quit()

#TODO: Replace with real database commands
def getDB_Content(filename, content):
    ''' Collects the emails from the "database" to be used later
    '''
    with open(filename, 'r') as file:
        for line in file:
            lname, fname, email = line.split()
            content[email] = lname + ' ' + fname
    log("Database data is collected")

def getWeb_Content(site, web, db, uri):
    #navigate to membership management
    site.visit(uri + '/members/list')

    temp=''
    while site.is_text_not_present('0 members total'): #emails found
        log("Grabbing data from webserv...")
        links = site.find_link_by_partial_href('--at--')

        for link in links:
            web.append(link.value)
            entry = ''
            try:
                entry = db[link.value] 
            except:
                entry = ' '
            temp += entry + ' <' + link.value + '>\n'
    
        removeEmails(site, temp, uri, "disable")
        site.visit(uri + '/members/list')
    #else no emails
    addEmails(site, temp, uri, "disable")
    log("Webserv data is collected")

def update(site, webmail, content, removed_emails, added_emails, uri):
    ''' compares email lists and appends data to appropriate add/rm_email data structs.
        * if (email in webserv but not datatbase) remove;
        * if (email in database but not webserv) add;
    '''
    log("Comparing emails found on webserv with emails in database")

    #compares every email from the webserv to those found in the database
    for web_data in webmail:
        if web_data not in content: #if true, then that email must be removed
            removed_emails += web_data + '\n'
    
    #compares every email from the database to those found in the webserv
    for db_data in content:
        if db_data not in webmail: #if true, then that email must be added
            entry = ''
            try:
                entry = content[db_data] 
            except:
                entry = ' '
            added_emails += entry + ' <' + db_data + '>\n'

    removeEmails(site, removed_emails, uri)
    addEmails(site, added_emails, uri)
    log("Webserv and Database are synced")

def removeEmails(site, emails, uri, logging="enable"):
    ''' emails: string of emails newline separated
        logging: is a flag whether or not to log the action, the default is to log
    '''
    site.visit(URI + '/members/remove')
    site.fill('unsubscribees', emails)
    site.find_by_name('setmemberopts_btn').click()

    if logging == "enable":
        for email in emails.split('\n')[:-1]:
            log("removed " + email)

def addEmails(site, emails, uri, logging="enable"):
    ''' emails: string of emails newline separated
        logging: is a flag whether or not to log the action, the default is to log
    '''
    browser.visit(URI + '/members/add')
    browser.fill('subscribees', emails)
    browser.find_by_name('setmemberopts_btn').click()

    if logging == "enable":
        for email in emails.split('\n')[:-1]:
            log("added " + email.split('<')[1][:-1])

def log(message):
    ''' logs in the format of: "timestamp removed/added email"
        time stamp in the format: "YYYY-mm-dd hh:mm:ss"
    '''
    print(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message)

if __name__ == "__main__":        
    browser = Browser('phantomjs') #remove 'phantomjs' to use default firefox

    #collect login data collected from .env
    load_dotenv(find_dotenv())
    PSWD = os.getenv('PASSWORD')
    URI = os.getenv('LISTSERV_URI')

    # Check that data is set in the .env
    assert PSWD, "No password in .env\nAborting"
    assert URI, "No uri in .env\nAborting"

    #lists to be filled with scraped data
    web_emails = [] #format: ["email"]
    db_content = {} #format: key="email" value="lname fname"

    #These strings store newline separated emails to be added to or removed
    #from the webserv depending on the contents of the database and webserv.
    add_emails = "" #"lname fname <email>\n..."
    rm_emails = "" #"email\n..."
    
    login(browser, URI, PSWD)
    
    getDB_Content("oldEmails.txt", db_content)
    
    getWeb_Content(browser, web_emails, db_content, URI)
    
    update(browser, web_emails, db_content, rm_emails, add_emails, URI)
    
    logout(browser, URI)
