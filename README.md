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
    * geckodriver is only included for graphical debugging purposes.

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
./update_emails.py 2> /dev/null
```

* Redirecting stderr because of selenium or requests warnings.

##NOTES:
The email text files contain dummy email/name data used
to populate webserv and simulate discrepencies between the
database and webserv data.

* oldEmails.txt : total fake data
* mixEmails.txt : oldEmails short ~164 emails 
* newEmails.txt : 5 emails from the original