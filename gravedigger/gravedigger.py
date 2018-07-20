"""
This module kills and removes containers that satisfy the following conditions:
* not matched by any pattern listed in whitelist.txt
* created more than 24h ago
Also, a logfile called gravedigger.log is created in the current directory
"""
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List

import docker
from dateutil import parser
from docker.errors import NotFound, APIError
from docker.models.containers import Container

WHITELIST_FILE = "whitelist.txt"
LOG_FILE = "gravedigger.log"


def read_whitelist() -> List[str]:
    with open(WHITELIST_FILE, encoding="utf-8") as f:
        return f.read().split()


def filter_whitelisted_containers(containers: List[Container], whitelist: List[str]) -> List[Container]:
    """
    Filter out whitelisted containers.

    :param containers:
    :param whitelist:
    :return: A list of containers not matching regex entries in the whitelist
    """
    containers_set = set(containers)

    for entry in whitelist:
        matcher = re.compile(entry)
        keep_containers = filter(lambda container: matcher.match(container.name), containers)

        containers_set -= set(keep_containers)

    return list(containers_set)


def filter_newer_containers(containers: List[Container]) -> List[Container]:
    """
    Filter out containers younger than 24h

    :param containers:
    :return: A list of containers created more than 24h ago
    """

    def fresh_container(container: Container) -> bool:
        creation_date = parser.parse(container.attrs["Created"])

        return datetime.now(timezone.utc) - creation_date < timedelta(hours=24)

    return list(filter(lambda x: not fresh_container(x), containers))


def kill_and_remove_containers(containers: List[Container]) -> None:
    """
    Take a list of containers and try to kill and remove them.

    :param containers:
    :return:
    """
    for container in containers:
        try:
            container.kill()
        except NotFound:
            log.warning("Tried to kill {}, but found no corresponding container".format(container.name))
            continue
        except APIError:
            log.exception("Could not kill {}".format(container.name))

        try:
            container.remove()
        except APIError:
            log.exception("Could not remove {}".format(container.name))

        log.info(" * Killed and removed {}".format(container.name))


def init_logger():
    global log
    log = logging.getLogger("gravedigger")
    log.setLevel(logging.INFO)
    log.addHandler(logging.FileHandler(LOG_FILE))
    log.addHandler(logging.StreamHandler())


def main():
    init_logger()
    log.info("Started at {}".format(datetime.now()))

    whitelist = read_whitelist()
    docker_client = docker.from_env()
    containers = docker_client.containers.list(all=True)

    filtered_containers = filter_whitelisted_containers(containers, whitelist)
    filtered_containers = filter_newer_containers(filtered_containers)
    kill_and_remove_containers(filtered_containers)

    running_containers = docker_client.containers.list()
    if running_containers:
        log.info("Left the following containers running:\n{}".format(
            "\n".join(map(lambda x: " * " + x.name, running_containers))))
    else:
        log.info("Left no containers running")

    log.info("Ended at {}".format(datetime.now()))


if __name__ == "__main__":
    main()
