#!/usr/bin/env python

"""
This script syncronizes user name and emails between a mysql database and
mailman server. Correct login credientials for the databse and mailman server
must be provided in a '.env' file.

Python2 & Python3 compatible.

Author: Connor Christian
"""

from __future__ import print_function, division, unicode_literals
import argparse
import os
import re
import sys
import time
from builtins import range
import dotenv
import splinter
import pymysql

def login_webserv(site, uri, pswd):
    """
    Logs into the webserv by navigating to the URL, inputting credentials, and
        clicking the login button.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.
        pswd (str): Password required to login to the webserv.
    """
    site.visit(uri)
    assert site.is_text_present(VERSION_NUMBER), "Incorrect version number\nAborting"
    site.fill('adminpw', pswd)
    site.find_by_name('admlogin').click()
    assert site.is_text_not_present('Authorization failed.'), "Login failed\nAborting"

def logout_webserv(site, uri):
    """
    Logs out of the webserv.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.
    """
    site.visit(uri + '/logout')
    site.quit()

def get_db_content(HOST, UNAME, DBPSWD, NAME):
    """
    Collects the emails from the "database" to be used later.

    Args:
        HOST (str): Uri for mysql database
        UNAME (str): Username for mysql database
        DBPSWD (str): Password for mysql database
        NAME (str): Name of table in mysql database

    Attributes:
        db (pymysql.connections.Connection): Database connection
        cursor (pymysql.cursors.Cursor): Used to interact with database
        data (tuple): All users returned from fetching from database
        content (dict): Data in the expected form of a database

    Returns:
        dict: Content attribute that contains all of the users on the database.
    """
    # Open database connection
    db = pymysql.connect(HOST, UNAME, DBPSWD, NAME)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    cursor.execute("SELECT CONCAT(p.lname, ' ', p.fname) AS name, p.email FROM \
        ac_person p\
        WHERE p.deleted IS NULL AND p.onnoticelist = 't'\
        ORDER BY p.lname ASC, p.fname ASC")
    # Fetch a single row using fetchone() method.
    data = cursor.fetchall() # data = (("lname fname", "email"))
    content = dict()
    try: #python2 version
        for user in data:
            content[unicode(user[1], "utf-8")] = unicode(user[0], "utf-8")
    except NameError: #python3
        for user in data:
            content[user[1]] = user[0]
    # disconnect from server
    db.close()
    log("Database data is collected")
    return content

def get_web_emails(site, uri):
    """
    Scrapes the webserv for all of the users uploaded.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.

    Attributes:
        letters (list): Contains every letter representing a tab in the html.
        web_emails (list): Stores all of the scraped emails.
        maxUsers (int): Stores the total number of emails on the webserv. Used
            for logging progress.
        current (int): Counter for what percentage of emails have been scraped
        rows (str): Unused variable that stores how many rows the terminal window is.
        columns (int): Stores the number of columns wide the terminal window is
        chunks (int): Stores the current "chunk" the scraper is at from the html.
            Used for scraping all data if the webserv has organized it in
            sublists.
        links (splinter.element_list.ElementList): Stores splinter obj referring to all the matching
            elements. Used to find all emails on current screen.

    Returns:
        list: Web_emails attribute that contains all emails scraped from the webserv.
    """
    #navigate to membership management
    site.visit(uri + '/members/list')
    letters = map(str, re.findall(r'/members\?letter=[a-z0-9]', site.html))
    if letters != []:
        letters = list(set(letters))
    web_emails = list()
    maxUsers = int(re.search('<em>([0-9]*) members total', site.html).group(1))
    current = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = min(int(columns) - len("] 100% complete "), 80)
    log("Scraping data from webserv")
    if letters != []: #found letters
        for letter in letters:
            site.visit(uri + letter)
            chunks = len(site.find_link_by_partial_href('&chunk='))
            for chunk in range(chunks+1):
                site.visit(uri + letter + '&chunk=' + str(chunk))
                links = site.find_link_by_partial_href('--at--')
                for link in links:
                    web_emails.append(link.value)
            ratio = len(web_emails)/maxUsers
            current = int(round(ratio*columns))
            if not args.quiet:
                sys.stdout.write("\r\033[93m" + '['\
                    + '#'*(current) + ' '*(columns - current) \
                    + "] " + str(int(round(ratio*100)))\
                    + "% complete\033[0m")
                sys.stdout.flush()
        if not args.quiet:
            sys.stdout.write('\n')
    else: #all on one page
        site.visit(uri + '/members/list')
        links = site.find_link_by_partial_href('--at--')
        for link in links:
            web_emails.append(link.value)
    log("Webserv data is collected")
    return web_emails

def compare_datasets(webmail, db_content):
    """
    Compares email lists and appends data to appropriate add/rm_email data
        structs.

    Examples:
        if (email in database but not webserv) add;
        if (email in webserv but not datatbase) remove;

    Args:
        webmail (list): List of all emails scraped from the webserv.
        db_content (dict): Dictonary, to be used as a list of keys(emails), containing
            all the users on the database.

    Attributes:
        add_users (str): Newline separated emails to be added of the format:
            "lname fname <email>\\n".
        rm_emails (str): Newline separated emails to be removed of the format:
            "email\\n".

    Returns:
        tuple: Contains the emails to add and remove from the webserv
    """
    add_users = ""
    rm_emails = ""
    log("Comparing emails found on webserv with emails in database")
    #compares every email from the webserv to those found in the database
    for web_data in webmail:
        if web_data not in db_content: #if true, then that email must be removed
            rm_emails += web_data + '\n'
    #compares every email from the database to those found in the webserv
    for db_data in db_content:
        if db_data not in webmail: #if true, then that email must be added
            add_users += db_content[db_data] + ' <' + db_data + '>\n'
    return tuple([add_users, rm_emails])

def update_webserv(site, uri, data):
    """
    Updates the webserv by adding and removing emails based on descrepencies
        between the webser and database.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.
        data (tuple): First index is a list of emails to add. Second index is a
            list of emails to remove.

    Attributes:
        added_emails (list): Stores all emails to be added to webserv.
        removed_emails (list): Stores all emails to be removed from webserv.
    """
    log("Synchronizing data on the webserv")
    added_users, removed_emails = data
    add_webserv_emails(site, uri, added_users)
    remove_webserv_emails(site, uri, removed_emails)
    log("Webserv and database are synced")

def add_webserv_emails(site, uri, users):
    """
    Takes users that have been passed in and navigates to subscription page
        of the webserv that adds content to the webserv.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.
        users (str): All emails that are to be added to the webserv.
            Format: "lname fname <email>\\n"

    Attributes:
        users (list): Converted emails string (args) to list.

    """
    if not args.dryrun:
        # emails: string of emails newline separated
        site.visit(uri + '/members/add')
        site.choose('send_welcome_msg_to_this_batch', '0')
        site.fill('subscribees', users)
        site.find_by_name('setmemberopts_btn').click()
    users = users.split('\n')
    if users[-1] == "":
        users.pop()
    for user in users:
        log("\033[32madded\033[0m " + user)

def remove_webserv_emails(site, uri, emails):
    """
    Takes emails that have been passed in and navigates to unsubscription page
        of the webserv that removes all matching content in the webserv.

    Args:
        site (splinter.driver.webdriver): Instance of the splinter browser.
        uri (str): Web address to navigate with splinter browser.
        emails (str): All emails that are to be removed from the webserv.
            Format: "email\\n"

    Attributes:
        emails (list): Converted emails string (args) to list.

    """
    if not args.dryrun:
        # emails: string of emails newline separated
        site.visit(uri + '/members/remove')
        site.choose('send_unsub_ack_to_this_batch', '0')
        site.fill('unsubscribees', emails)
        site.find_by_name('setmemberopts_btn').click()
    emails = emails.split('\n')
    if emails[-1] == '':
        emails.pop()
    for email in emails:
        log("\033[34mremoved\033[0m " + email)

def log(message):
    """
    Outputs to stdout in the format of:
        "YYYY-mm-dd hh:mm:ss <message>"

    Args:
        message (str): Content to output with timestamp.
    """
    if not args.quiet:
        print(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message)

if __name__ == "__main__":
    # argparse used to generate help menu and easy commandline argument parsing
    parser = argparse.ArgumentParser(description="A headless opensource tool for\
            synchronizing user's contact information from a database to a\
            webserver utilizing scraping. This script is python2 and python3\
            compatible.", epilog="Author: Connor Christian")
    parser.add_argument("-q", "--quiet", help="suppress output", action="store_true")
    parser.add_argument("-v", "--verbose", help="use the firefox browser",
                        action="store_true")
    parser.add_argument("-d", "--dryrun", help="perform a dry run by not \
        changing the listserv", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        browser = splinter.Browser()
    else:
        browser = splinter.Browser('phantomjs')
    VERSION_NUMBER = "version 2.1.24"
    #collect login data collected from .env
    dotenv.load_dotenv(dotenv.find_dotenv())
    URI = os.getenv('LISTSERV_URI')
    PSWD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    UNAME = os.getenv('UNAME')
    DBPSWD = os.getenv('DBPASSWD')
    NAME = os.getenv('DBNAME')
    # Check that data is set in the .env
    assert URI, "No uri in .env\nAborting"
    assert PSWD, "No password in .env\nAborting"
    assert HOST, "No host for database in .env\nAborting"
    assert UNAME, "No database user in .env\nAborting"
    assert DBPSWD, "No database password in .env\nAborting"
    assert NAME, "No database name in .env\nAborting"
    if args.dryrun:
        log("\033[93mPerforming dry run\033[0m")
    login_webserv(browser, URI, PSWD)
    #data structures to be filled with scraped data:
    #dictionary format: key="email" value="lname fname"
    db_content = get_db_content(HOST, UNAME, DBPSWD, NAME)
    #list format: ["email"]
    web_emails = get_web_emails(browser, URI)
    update_webserv(browser, URI, compare_datasets(web_emails, db_content))
    logout_webserv(browser, URI)
