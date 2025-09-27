import unittest
import json
from scrape_schedule import scrape_schedule

class TestScrapeSchedule(unittest.TestCase):
    def test_scrape_returns_dict(self):
        rooms = scrape_schedule()
        self.assertIsInstance(rooms, dict)
    
    def test_has_at_least_one_room(self):
        rooms = scrape_schedule()
        self.assertGreater(len(rooms), 0)
    
    def test_each_room_has_required_keys(self):
        rooms = scrape_schedule()
        for room, data in rooms.items():
            self.assertIn('advisors', data)
            self.assertIn('graders', data)
            self.assertIn('schedule', data)
            self.assertIsInstance(data['schedule'], list)
    
    def test_each_room_has_at_least_one_schedule_item(self):
        rooms = scrape_schedule()
        for room, data in rooms.items():
            self.assertGreater(len(data['schedule']), 0)
    
    def test_schedule_items_are_tuples(self):
        rooms = scrape_schedule()
        for room, data in rooms.items():
            for item in data['schedule']:
                self.assertIsInstance(item, tuple)
                self.assertEqual(len(item), 2)
                self.assertIsInstance(item[0], str)  # time
                self.assertIsInstance(item[1], str)  # presenter

if __name__ == '__main__':
    unittest.main()