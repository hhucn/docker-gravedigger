# docker-gravedigger
A tool to kill and remove docker containers after 24h. Looks into "whitelist"
to find containers, which should not be removed.

We use this project to remove containers, which have been started in our
GitLab CI with privileged mode. If a pipeline then fails, the started
containers are not being killed by the CI. Therefore, we had containers on our
shared runners, which were running forever. This script then kills them after
24 hours.

## Setup
Create a pipenv and install requirements:
```
$ pipenv install
```

## Usage

1. Modify `whitelist.txt` to your needs. Here you can store a
   [regex](https://docs.python.org/3/library/re.html#regular-expression-syntax),
   which is interpreted by Python. Matching containers will not be removed. For
   example, if you want to keep all containers containing the substring
   "dbas_", e.g.  "dbas_web_1" or "dbas_db_1", you have to add "dbas_" to the
   whitelist. Reads one line at a time. Here is a sample whitelist.txt-file:
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
