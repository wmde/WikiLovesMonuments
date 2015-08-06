# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import commons_bot


class TestCommonsBot(unittest.TestCase):

    def test_default_start_time_returns_1st_of_month(self):
        date = Mock()
        date.year = 2015
        date.month = 9
        date.day = 25
        default_start_time = commons_bot.default_start_time(date)
        self.assertEqual(default_start_time.year, 2015)
        self.assertEqual(default_start_time.month, 9)
        self.assertEqual(default_start_time.day, 1)
