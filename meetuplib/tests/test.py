import unittest
from meetuplib import MeetupClient

YOUR_API_KEY="" #put here your private Meetup API key

class Test_test1(unittest.TestCase):
    def setUp(self):
        self.mclient = MeetupClient(YOUR_API_KEY, paging=200)

    def test_findSingleGroupByName(self):
        self.assertEqual(self.mclient.findGroupByName("PyData_Warsaw")[0].name, "PyData Warsaw")

    def test_pagingEvents(self):
        self.assertGreater(len(self.mclient.findEventsByGroup("LondonOnBoard")), 200)

if __name__ == '__main__':
    unittest.main()
