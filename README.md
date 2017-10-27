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
./update_emails.py [-h] [-q] [-v] [-d]
```
or
```
python2 update_emails.py [-h] [-q] [-v] [-d]
```
or
```
python3.x update_emails.py [-h] [-q] [-v] [-d]
```
