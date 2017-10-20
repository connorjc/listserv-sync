##SETUP:
1. virtualenv DIRECTORY --no-site-packages
2. cd DIRECTORY
3. source bin/activate
4. git clone ________
5. cd listserv-sync
6. *cp phantomjs ../bin
7. *cp geckodriver ../bin
8. cp .env.example .env
9. edit .env to store the values with website and password to the listserv

* phantomjs is a headless browser
* geckodriver is used for Firefox
    * geckodriver is only included for debugging purposes.

##INTSTALL:
```
pip install -r requirements.txt
```

##GENERATE INSTALLATION LIST:
```
pip freeze > requirements.txt
```

##RUN:
```
./update_emails.py [-h] [-q] [-d]
```

##NOTES:
The email text files contain dummy email/name data used
to populate webserv and simulate discrepencies between the
database and webserv data.

* newEmails.txt : 5 emails
* mixEmails.txt : 36 emails; oldEmails - ~164 emails 
* oldEmails.txt : 203 emails
* mostEmails.txt : 1000 emails for a stress test
* extreme.txt : 2703 emails for a larger stress test
