# docker-gravedigger
A tool to kill and remove docker containers after 24h.

## setup
Create a pipenv and install requirements:
```
$ pipenv install
```

## run

1. Modify `whitelist.txt` to your needs.

1. Use pipenv to run the `gravedigger` module:
    ```
    $ pipenv run python gravedigger
    ```

1. You can find a summary of the completed actions in `gravedigger.log`.

## dependencies
We use the following modules:
* `logging`
* `re`
* `datetime`
* `docker`
