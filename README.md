# docker-gravedigger
A tool to kill and remove docker containers after 24h.

## Setup
Create a pipenv and install requirements:
```
$ pipenv install
```

## Usage

1. Modify `whitelist.txt` to your needs. Here you can store a regex, which is
   interpreted by Python. Matching containers will not be removed. For example
   if you want to keep all containers starting with "dbas_", for example
   "dbas_web_1" or "dbas_db_1", you have to add "dbas_" to the whitelist. Reads
   one line at a time. Here is a sample whitelist.txt-file:
    ```
    dbas_
    pleasedontstopme
    ```

1. Use pipenv to run the `gravedigger` module:
    ```
    $ pipenv run python gravedigger/gravedigger.py
    ```

1. You can find a summary of the completed actions in `gravedigger.log`.

## Dependencies
We are using Python 3.6 with the following modules:
* `logging`
* `re`
* `datetime`
* `dateutil`
* `docker`
