import docker
import logging
import re
from datetime import datetime, timedelta
from dateutil.parser import parser
from docker.errors import NotFound, APIError
from docker.models.containers import Container
from typing import List

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
        keep_containers = filter(lambda x: matcher.match(x.name), containers)

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

        return datetime.now() - creation_date < timedelta(hours=24)

    return list(filter(lambda x: not fresh_container(x), containers))


def kill_containers(hitlist_containers: List[Container]) -> None:
    """
    Take a list of containers and try to kill and remove them.

    :param hitlist_containers:
    :return:
    """
    for container in hitlist_containers:
        try:
            container.kill()
        except NotFound:
            log.warning("Tried to kill {}, but found no corresponding container".format(container.name))
            continue
        except APIError as exception:
            log.error("Could not kill {}:\n{}".format(container.name, exception.__traceback__))

        try:
            container.remove()
        except APIError as exception:
            log.error("Could not remove {}:\n{}".format(container.name, exception.__traceback__))

        log.info(" * Killed and removed {}".format(container.name))


def init_logger():
    global log
    log = logging.getLogger("gravedigger")
    handler = logging.FileHandler(LOG_FILE)
    log.setLevel(logging.INFO)
    log.addHandler(handler)


def main():
    init_logger()
    log.info("Started at {}".format(datetime.now()))

    whitelist = read_whitelist()
    docker_client = docker.from_env()
    containers = docker_client.containers.list(all=True)

    hitlist_containers = filter_whitelisted_containers(containers, whitelist)
    hitlist_containers = filter_newer_containers(hitlist_containers)
    kill_containers(hitlist_containers)

    log.info("Left the following containers running:\n{}".format(
        "\n".join(map(lambda x: " * " + x.name, docker_client.containers.list()))))

    log.info("Ended at {}".format(datetime.now()))


if __name__ == "__main__":
    main()
