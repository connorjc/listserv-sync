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
    web = list()
    temp=''
    #TODO: find another algorithm to scrape faster
    maxUsers = total = int(re.search('<em>([0-9]*) members total',site.html).group(1))
    while(total > 0): #emails found
        links = site.find_link_by_partial_href('--at--')
        for link in links:
            web.append(link.value)
            entry = ''
            try:
                entry = db[link.value] 
            except:
                entry = ' '
            temp += entry + ' <' + link.value + '>\n'
        remove_webserv_emails(site, temp, uri, "disable")
        site.visit(uri + '/members/list')
        total = int(re.search('<em>([0-9]*) members total',site.html).group(1))
        log("Scraping data from webserv. \033[93m" + \
            str(round(100 - float(total)/maxUsers *100))\
            +"% complete\033[0m")

    #else no emails
    add_webserv_emails(site, temp, uri, "disable")
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
    while len(total) != 0:
        sublist = ''
        try:
            for _ in range(30):
                sublist += total.pop() + '\n'
        except IndexError:
            pass
        finally:
            site.fill('unsubscribees', emails)
            site.find_by_name('setmemberopts_btn').click()
        if logging == "enable":
            if sublist == '\n':
                log("Nothing to remove.")
            else:
                log("Removing data. \033[93m" + \
                    str(round(100 - float(len(total))/size *100))\
                    +"% complete\033[0m")
                for email in sublist.strip().split('\n'):
                    log("\033[34mremoved\033[0m " + email)

def add_webserv_emails(site, emails, uri, logging="enable"):
    ''' emails: string of emails newline separated
        logging: is a flag whether or not to log the action, the default is to log
    '''
    total = emails.split('\n')
    size = len(total)
    site.visit(URI + '/members/add')
    while len(total) != 0:
        sublist = ''
        try:
            for _ in range(30):
                sublist += total.pop() + '\n'
        except IndexError:
            pass
        finally:
            site.fill('subscribees', emails)#emails
            site.find_by_name('setmemberopts_btn').click()
        if logging == "enable":
            if sublist == '\n':
                log("Nothing to add.")
            else:
                log("Adding data. \033[93m" + \
                    str(round(100 - float(len(total))/size *100))\
                    +"% complete\033[0m")
                for email in sublist.strip().split('\n'):
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
    db_content = get_db_content("newEmails.txt")
    #list format: ["email"]
    web_emails = get_web_emails(browser, db_content, URI)
        
    update_webserv(browser, compare_datasets(web_emails, db_content), URI)
    
    logout_webserv(browser, URI)
