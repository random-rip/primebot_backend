from django.test import TestCase

from data_crawling.api import Api


class MatchHTMLParserTests(TestCase):

    def test_random(self):
        api = Api()
        correct_values = [
            # TODO
        ]
        for i in range(10):
            print(api._get_random_user_agent())
