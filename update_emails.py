#!/usr/bin/env python
from splinter import Browser
from dotenv import load_dotenv, find_dotenv
import time, os, sys, re, argparse

def login_webserv(site, uri, pswd):
    site.visit(uri)
    site.fill('adminpw',pswd)
    site.find_by_name('admlogin').click()

def logout_webserv(site, uri):
    site.visit(URI + '/logout')
    site.quit()

#TODO: Replace with real database commands
def get_db_content(filename):
    ''' Collects the emails from the "database" to be used later'''
    content = dict()
    with open(filename, 'r') as file:
        for line in file:
            lname, fname, email = line.split()
            content[email] = lname + ' ' + fname
    log("Database data is collected")
    return content

def get_web_emails(site, db, uri):
    #navigate to membership management
    site.visit(uri + '/members/list')
    letters = map(str, re.findall('/members\?letter=[a-z]', site.html))
    if letters != []:
        letters = list(set(letters))
    web = list()
    maxUsers = int(re.search('<em>([0-9]*) members total',site.html).group(1))
    if letters != []: #found letters
        for letter in letters:
            site.visit(uri + letter)
            chunks = len(site.find_link_by_partial_href('&chunk='))
            for chunk in xrange(chunks+1):
                site.visit(uri + letter + '&chunk=' + str(chunk))
                links = site.find_link_by_partial_href('--at--')
                for link in links:
                    web.append(link.value)
                log("Scraping data from webserv. \033[93m" + \
                    str(round(float(len(web))/maxUsers *100))\
                    +"% complete\033[0m")
    else: #all on on page
        site.visit(uri + '/members/list')
        links = site.find_link_by_partial_href('--at--')
        for link in links:
            web.append(link.value)
    log("Webserv data is collected")
    return web

def compare_datasets(webmail, content):
    ''' Compares email lists and appends data to appropriate add/rm_email data 
        structs.
        * if (email in database but not webserv) add;
        * if (email in webserv but not datatbase) remove;

        Returns a tuple containing the emails to add and remove from the webserv
    '''
    #These strings store newline separated emails to be added to or removed
    #from the webserv depending on the contents of the database and webserv.
    add_emails = "" #"lname fname <email>\n..."
    rm_emails = "" #"email\n..."

    log("Comparing emails found on webserv with emails in database")

    #compares every email from the webserv to those found in the database
    for web_data in webmail:
        if web_data not in content: #if true, then that email must be removed
            rm_emails += web_data + '\n'
    
    #compares every email from the database to those found in the webserv
    for db_data in content:
        if db_data not in webmail: #if true, then that email must be added
            entry = ''
            try:
                entry = content[db_data] 
            except:
                entry = ' '
            add_emails += entry + ' <' + db_data + '>\n'
    return tuple([add_emails, rm_emails])

def update_webserv(site, data, uri):
    ''' Updates the webserv by adding and removing emails based on descrepencies
        between the webser and database
    '''
    log("Synchronizing data on the webserv")
    added_emails, removed_emails = data
    add_webserv_emails(site, added_emails, uri)
    remove_webserv_emails(site, removed_emails, uri)
    log("Webserv and database are synced")

def remove_webserv_emails(site, emails, uri, logging="enable"):
    ''' emails: string of emails newline separated
        logging: is a flag whether or not to log the action, the default is to log
    '''
    total = emails.split('\n') 
    size = len(total)
    site.visit(URI + '/members/remove')
    site.fill('unsubscribees', emails)
    site.find_by_name('setmemberopts_btn').click()
    emails = emails.split('\n')
    if emails[-1] == '':
        emails.pop()
    for email in emails:
        log("\033[34mremoved\033[0m " + email)

def add_webserv_emails(site, emails, uri, logging="enable"):
    ''' emails: string of emails newline separated
        logging: is a flag whether or not to log the action, the default is to log
    '''
    total = emails.split('\n')
    size = len(total)
    site.visit(URI + '/members/add')
    site.fill('subscribees', emails)
    site.find_by_name('setmemberopts_btn').click()
    emails = emails.split('\n')
    if emails[-1] == "":
        emails.pop()
    for email in emails:
        log("\033[32madded\033[0m " + email)

def log(message):
    ''' logs in the format of: "timestamp removed/added email"
        time stamp in the format: "YYYY-mm-dd hh:mm:ss"
    '''
    if not args.quiet:
        print(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A headless opensource tool for\
            synchronizing user's contact information from a database to a\
            webserver utilizing scraping",epilog="Author: Connor Christian")
    parser.add_argument("-q", "--quiet", help="suppress output", action="store_true")
    parser.add_argument("-d", "--debug", help="use the firefox browser", action="store_true")
    args = parser.parse_args()

    if args.debug:
        browser = Browser()
    else:
        browser = Browser('phantomjs')

    #collect login data collected from .env
    load_dotenv(find_dotenv())
    PSWD = os.getenv('PASSWORD')
    URI = os.getenv('LISTSERV_URI')

    # Check that data is set in the .env
    assert PSWD, "No password in .env\nAborting"
    assert URI, "No uri in .env\nAborting"
    
    login_webserv(browser, URI, PSWD)

    #data structures to be filled with scraped data
    #dictionary format: key="email" value="lname fname"
    db_content = get_db_content("mostEmails.txt")
    #list format: ["email"]
    web_emails = get_web_emails(browser, db_content, URI)
        
    update_webserv(browser, compare_datasets(web_emails, db_content), URI)
    
    logout_webserv(browser, URI)
