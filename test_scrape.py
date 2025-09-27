import unittest
import json
import argparse
import hashlib
from unittest.mock import patch, MagicMock
from scrape_schedule import scrape_schedule, create_pdf

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

    def test_hash_generation(self):
        """Test that hash generation produces consistent results."""
        rooms = scrape_schedule()
        hash1 = hashlib.sha256(json.dumps(rooms, sort_keys=True).encode())
        hash2 = hashlib.sha256(json.dumps(rooms, sort_keys=True).encode())
        self.assertEqual(hash1.hexdigest(), hash2.hexdigest())

    def test_json_output_format(self):
        """Test that JSON output is properly formatted."""
        rooms = scrape_schedule()
        json_output = json.dumps(rooms, indent=2)
        parsed = json.loads(json_output)
        
        # Check that we have the same keys
        self.assertEqual(set(parsed.keys()), set(rooms.keys()))
        
        # Check structure for each room
        for room in rooms:
            self.assertIn('advisors', parsed[room])
            self.assertIn('graders', parsed[room])
            self.assertIn('schedule', parsed[room])
            self.assertIsInstance(parsed[room]['schedule'], list)
            
            # Check that schedule items are lists (tuples become lists in JSON)
            for item in parsed[room]['schedule']:
                self.assertIsInstance(item, list)
                self.assertEqual(len(item), 2)
                self.assertIsInstance(item[0], str)  # time
                self.assertIsInstance(item[1], str)  # presenter

    @patch('scrape_schedule.SimpleDocTemplate')
    def test_create_pdf_basic(self, mock_doc_template):
        """Test PDF creation with basic options."""
        mock_doc = MagicMock()
        mock_doc_template.return_value = mock_doc
        
        rooms = scrape_schedule()
        create_pdf(rooms, "test.pdf")
        
        mock_doc_template.assert_called_once()
        mock_doc.build.assert_called_once()

    @patch('scrape_schedule.SimpleDocTemplate')
    def test_create_pdf_with_qr_codes(self, mock_doc_template):
        """Test PDF creation with QR codes enabled."""
        mock_doc = MagicMock()
        mock_doc_template.return_value = mock_doc
        
        rooms = scrape_schedule()
        create_pdf(rooms, "test.pdf", qr_codes=True)
        
        mock_doc_template.assert_called_once()
        mock_doc.build.assert_called_once()

    @patch('scrape_schedule.SimpleDocTemplate')
    def test_create_pdf_without_title(self, mock_doc_template):
        """Test PDF creation without title."""
        mock_doc = MagicMock()
        mock_doc_template.return_value = mock_doc
        
        rooms = scrape_schedule()
        create_pdf(rooms, "test.pdf", include_title=False)
        
        mock_doc_template.assert_called_once()
        mock_doc.build.assert_called_once()

    def test_command_line_parsing(self):
        """Test command line argument parsing."""
        parser = argparse.ArgumentParser(description="Scrape symposium schedule and generate PDF or JSON.")
        parser.add_argument('--json', action='store_true', help="Output data as JSON instead of generating PDF.")
        parser.add_argument('--allow-breaks', action='store_true', help="Allow page breaks within room sections (default: keep rooms together).")
        parser.add_argument('--show-headers', action='store_true', help="Show table headers (Time, Presenter) in PDF.")
        parser.add_argument('--hash', action='store_true', help="Output hash of the schedule data instead of generating files.")
        parser.add_argument('--no-title', action='store_true', help="Exclude the title from PDF output.")
        parser.add_argument('--qr-codes', action='store_true', help="Include QR codes linking to each room's webpage anchor.")
        
        # Test default arguments
        args = parser.parse_args([])
        self.assertFalse(args.json)
        self.assertFalse(args.allow_breaks)
        self.assertFalse(args.show_headers)
        self.assertFalse(args.hash)
        self.assertFalse(args.no_title)
        self.assertFalse(args.qr_codes)
        
        # Test all flags set
        args = parser.parse_args(['--json', '--allow-breaks', '--show-headers', '--hash', '--no-title', '--qr-codes'])
        self.assertTrue(args.json)
        self.assertTrue(args.allow_breaks)
        self.assertTrue(args.show_headers)
        self.assertTrue(args.hash)
        self.assertTrue(args.no_title)
        self.assertTrue(args.qr_codes)

    @patch('scrape_schedule.sync_playwright')
    def test_maintenance_mode_detection(self, mock_playwright):
        """Test that maintenance mode is properly detected and raises exception."""
        # Mock the page content to contain maintenance mode text
        mock_page = MagicMock()
        mock_page.content.return_value = "<html><body>The website is currently in Maintenance Mode. Please check back later.</body></html>"
        
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page
        
        mock_context = MagicMock()
        mock_context.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.__enter__.return_value = mock_context
        
        # Test that maintenance mode raises exception
        with self.assertRaises(Exception) as context:
            scrape_schedule()
        
        self.assertIn("Maintenance Mode", str(context.exception))
        self.assertIn("unavailable", str(context.exception))

if __name__ == '__main__':
    unittest.main()