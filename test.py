#!/usr/bin/env python
from splinter import Browser
import requests, re, time

#login data
pswd = 'Ht3stPC16'

'''
lists to be filled with scraped data
format: [("lastName","firstName","<email>"), (...)]
'''
web_emails = []
db_emails = []

'''
the following two data types contain email info based on
the relationship between the above two lists
string of strings: "last first <email>\n..."
'''
add_emails = "" 
rm_emails = ""

#used to store the exact time each email was added or removed
log = "\n"

def setEmails(f):
    # temporary: will be replaced when acutally getting data from a database and
    # not a textfile   global db_emails
    with open(f, 'r') as file:
        for line in file:
            lname, fname, email = line.split()
            db_emails.append((lname, fname, email[1:-1]))


def update():
    ''' compares email lists and appends data to appropriate add/rm_email data structs.
        * if (email in webserv but not datatbase) remove;
        * if (email in database but not webserv) add;
    '''
    global web_emails
    global db_emails
    global rm_emails
    global add_emails

    #compares every email from the webserv to those found in the database
    for web_data in web_emails:
        if web_data not in db_emails: #if true, then that email must be removed
            rm_emails += web_data[0] + ' ' + web_data[1] + " <" + web_data[2] + ">\n"
    
    #compares every email from the database to those found in the webserv
    for db_data in db_emails:
        if db_data not in web_emails: #if true, then that email must be added
            add_emails += db_data[0] + ' ' + db_data[1] + " <" + db_data[2] + ">\n"

    removeEmails(rm_emails)
    logging("removed", rm_emails)

    addEmails(add_emails)
    logging("added", add_emails)

def logging(status, emails):
    ''' logs in the format of: "timestamp removed/added email"
        time stamp in the format: "YYYY-mm-dd hh:mm:ss"
        status: "added" or "removed"
    '''
    global log
    for email in emails.split('\n')[:-1]:
        email = email.split('<')[1][:-1]
        log += time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + status + ' ' + email + '\n'

def removeEmails(e):  #remove all emails on the site
    browser.visit('https://lists.fsu.edu/mailman/admin/hpc-test/members/remove')
    browser.fill('unsubscribees', e)
    browser.find_by_name('setmemberopts_btn').click()
    browser.back()
    browser.reload()

def addEmails(e):  #remove all emails on the site
    browser.visit('https://lists.fsu.edu/mailman/admin/hpc-test/members/add')
    browser.fill('subscribees', e)
    browser.find_by_name('setmemberopts_btn').click()
    browser.back()
    browser.reload()

#go to mailserv site and login
browser = Browser('phantomjs')
browser.visit('https://lists.fsu.edu/mailman/admin/hpc-test')
browser.fill('adminpw',pswd)
browser.find_by_name('admlogin').click()

#login with requests session so I can pull html to parse
session = requests.session()
login_data = dict(adminpw=pswd)
r = session.post('https://lists.fsu.edu/mailman/admin/hpc-test', data=login_data)

#navigate to membership management
browser.click_link_by_href('../admin/hpc-test/members')

#get membership list html and check if empty or not
req = session.get('https://lists.fsu.edu/mailman/admin/hpc-test/members/list')
info = re.search(r'<em>0 members total</em>',req.text)

temp = ''
while info is None: #emails found
    #addresses grabs every email from the html page
    addresses = map(str,re.findall(r'[a-zA-Z0-9!\#\$\%\&\'\*\+\-\/\=\?\^\_\`\{\|\}\~\.]+?@[a-zA-Z0-9\-\.]+?</a>',req.text))
    #names grabs every name from the html page
    names = map(str,re.findall(r'value="\w* \w*"',req.text))
    #data associates the two above such that each name is linked with an email
    data = zip(names, addresses)  
    
    for d in data:
        lname, fname = d[0][7:-1].split()
        email = d[1][:-4]
        web_emails.append((lname, fname, email))

    for t in web_emails:
        temp += t[0] + ' ' + t[1] + " <" + t[2] + ">\n"
    removeEmails(temp)

    req = session.get('https://lists.fsu.edu/mailman/admin/hpc-test/members/list')
    info = re.search(r'<em>0 members total</em>',req.text)
#else no emails
addEmails(temp)

#At this point, webserv data is collected: names and emails

#Collect all the emails of current users somehow from the servers
#add emails from RCC database
#temp vvv
setEmails('newEmails.txt')
#temp ^^^

#At this point, db data is collected: names and emails

update()
print(log)
print("Webserv and Database are up to date.\n")

#logout before exiting
browser.visit('https://lists.fsu.edu/mailman/admin/hpc-test/logout')
browser.quit()
