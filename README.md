##SETUP:
```sh
virtualenv <DIRECTORY> --no-site-packages
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
```sh
pip install -r requirements.txt
```

##GENERATE INSTALLATION LIST:
```sh
pip freeze > requirements.txt
```

##RUN:
```sh
./update_emails.py [-h] [-q] [-v] [-d]
```

##NOTES:
phantomjs is a headless browser
geckodriver is used for Firefox for debugging
