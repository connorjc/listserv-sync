##SETUP:
1. virtualenv DIRECTORY --no-site-packages
2. cd DIRECTORY
3. source bin/activate
4. git clone ________

##INSTALL OPTION 1: pip install ______ 
* splinter
* requests

##INTSTALL OPTION 2:
* pip install -r requirements.txt

##DOWNLOAD:
place phantomjs executable in virtualenv bin

##RUN:
./test.py 2> /dev/null
* Redirecting stderr because of selenium or requests warnings.

##NOTES:
The email text files contain dummy email/name data used
to populate webserv and simulate discrepencies between the
database and webserv data.

* oldEmails.txt : total fake data
* mixEmails.txt : oldEmails short six 
* newEmails.txt : 5 emails from the original
