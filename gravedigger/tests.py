from unittest import TestCase

from gravedigger.gravedigger import filter_whitelisted_containers


class TestContainer:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class TestWhitelistedContainer(TestCase):
    container_foo = TestContainer("foo")
    container_bar = TestContainer("bar")
    container_dbas_web = TestContainer("dbas_web_1")
    container_dbas_db = TestContainer("dbas_db_1")

    def test_empty_whitelist_returns_container(self):
        containers = [self.container_foo]
        whitelist = []
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_foo], filtered_containers)

    def test_empty_whitelist_returns_two_containers(self):
        containers = [self.container_foo, self.container_bar]
        whitelist = []
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_foo, self.container_bar], filtered_containers)

    def test_unmatched_whitelist_returns_all_containers(self):
        containers = [self.container_foo, self.container_bar]
        whitelist = ["not_matching_containers"]
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_foo, self.container_bar], filtered_containers)

    def test_whitelist_matches_foo_should_return_bar_container(self):
        containers = [self.container_foo, self.container_bar]
        whitelist = ["foo"]
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_bar], filtered_containers)

    def test_whitelist_matches_substring_foo_should_return_bar_container(self):
        containers = [self.container_foo, self.container_bar]
        whitelist = ["fo"]
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_bar], filtered_containers)

    def test_whitelist_matches_dbas_returns_foo(self):
        containers = [self.container_foo, self.container_dbas_web, self.container_dbas_db]
        whitelist = ["dbas_"]
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_foo], filtered_containers)

    def test_multiple_whitelist_matches_returns_reduced_list(self):
        containers = [self.container_foo, self.container_dbas_web, self.container_dbas_db]
        whitelist = ["web", "db"]
        filtered_containers = filter_whitelisted_containers(containers, whitelist)
        self.assertCountEqual([self.container_foo], filtered_containers)
