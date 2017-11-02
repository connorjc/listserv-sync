# listserv-sync
A headless open source tool for synchronizing users' name and email between a
MySQL database and mailman server. Correct login credentials for the database
and mailman server must be provided in a `.env` file.


Python2 & Python3 compatible.

## SETUP:
### Python2:
```sh
virtualenv <DIRECTORY> --no-site-packages
```

### Python3:
```sh
python3.x -m venv <DIRECTORY>
```

### Both:
```sh
cd <DIRECTORY>
source bin/activate
git clone https://connorjc@bitbucket.org/fsurcc/listserv-sync.git
cd listserv-sync
cp phantomjs ../bin
cp geckodriver ../bin
cp .env.example .env
```
edit `.env` to store the credentials for the listserv and database

## INSTALL:
```sh
pip install -r requirements.txt
```
***
## COMMAND LINE ARGUMENTS:
 Short | Long        | Description                                    
 ----- | ----------- | ----------------------------------------------
 `-h`  | `--help`    | show this help message and exit               
 `-q`  | `--quiet`   | suppress output                               
 `-v`  | `--verbose` | use the headed firefox browser                
 `-d`  | `--dryrun`  | perform a dry run by not changing the listserv

## RUN:
### Python2:
```sh
python2 update_emails.py [-h] [-q] [-v] [-d]
```

### Python3:
```sh
python3.x update_emails.py [-h] [-q] [-v] [-d]
```

### Both:
```sh
./update_emails.py [-h] [-q] [-v] [-d]
```
***
## GENERATE INSTALLATION LIST:
```sh
pip freeze > requirements.txt
```
