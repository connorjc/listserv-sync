#listserv-sync
A headless open source tool for synchronizing users' name and email between a
MySQL database and mailman server. Correct login credentials for the database
and mailman server must be provided in a '.env' file.

Python2 & Python3 compatible.

##SETUP:
###Python2:
```
virtualenv <DIRECTORY> --no-site-packages
```

###Python3:
```
python3.x -m venv <DIRECTORY>
```

###Both:
```
cd <DIRECTORY>
source bin/activate
git clone https://connorjc@bitbucket.org/fsurcc/listserv-sync.git
cd listserv-sync
cp phantomjs ../bin
cp geckodriver ../bin
cp .env.example .env
```
edit ```.env``` to store the credentials for the listserv and database

##INSTALL:
```
pip install -r requirements.txt
```

##COMMAND LINE ARGUMENTS:
-h, --help : show this help message and exit
-q, --quiet : suppress output
-v, --verbose : use the firefox browser
-d, --dryrun : perform a dry run by not changing the listserv

##RUN:
###Python2:
```
python2 update_emails.py [-h] [-q] [-v] [-d]
```

###Python3:
```
python3.x update_emails.py [-h] [-q] [-v] [-d]
```

###Both:
```
./update_emails.py [-h] [-q] [-v] [-d]
```

##GENERATE INSTALLATION LIST:
```
pip freeze > requirements.txt
```
