##SETUP:
1. virtualenv DIRECTORY --no-site-packages
2. cd DIRECTORY
3. source bin/activate
4. git clone ________
5. cd listserv-sync
6. *cp phantomjs ../bin
7. *cp geckodriver ../bin
8. cp .env.example .env
9. edit .env to store the credentials for the listserv and database

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
