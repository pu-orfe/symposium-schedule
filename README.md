# Symposium Schedule 

Generate the ORFE Thesis Symposium schedule from a corresponding web site and generate a nicely formatted, paginated PDF or JSON output.

## Features

- Scrapes schedule data from https://symposium.orfe.princeton.edu
- Handles Cloudflare protection using Playwright
- Extracts room information, advisors, graders, and presentation schedules
- Generates paginated PDF with formatted tables
- Optional JSON output for data processing
- Comprehensive unit tests

## Requirements

- Python 3.8+
- Playwright (for browser automation)
- BeautifulSoup4 (for HTML parsing)
- ReportLab (for PDF generation)

## Installation

1. Clone or download the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   python -m playwright install chromium
   ```

## Usage

### Generate PDF (default)
```bash
python scrape_schedule.py
```
This creates `symposium_schedule.pdf` with the formatted schedule, keeping each room's information together on pages.

### Allow page breaks within rooms
```bash
python scrape_schedule.py --allow-breaks
```
This allows page breaks that might separate room titles from their content (not recommended).

### Show table headers
```bash
python scrape_schedule.py --show-headers
```
Include column headers (Time, Presenter) in the tables.

### Generate JSON output
```bash
python scrape_schedule.py --json
```
This outputs the schedule data as JSON to stdout and saves it to `symposium_schedule.json`.

### Generate PDF without title
```bash
python scrape_schedule.py --no-title
```
Excludes the title header from the PDF output.

### Generate PDF with QR codes
```bash
python scrape_schedule.py --qr-codes
```
Includes QR codes for each room that link to the room's anchor on the webpage.

### Run tests
```bash
python -m unittest test_scrape.py -v
```

## Output Format

### PDF
- Title page with symposium name
- Separate sections for each room
- Advisor and grader information
- Table with Time and Presenter columns
- Automatic pagination

### JSON
```json
{
  "001": {
    "advisors": "ORFE Advisors: Dr. Smith, Dr. Johnson",
    "graders": "PhD Candidate Graders: Alex Chen",
    "schedule": [
      ["9:00 am – 9:15 am", "John Anderson"],
      ["9:15 am – 9:30 am", "Sarah Mitchell"]
    ]
  }
}
```

## Testing

The project includes unit tests to ensure:
- At least one room is scraped
- Each room has required data structure
- Schedule items are properly formatted
- No regression in parsing logic

Run tests with:
```bash
python -m unittest test_scrape.py
```

## Dependencies

- requests
- beautifulsoup4
- reportlab
- playwright
- pytest (optional, for testing)

## License

This project is for educational purposes. Please respect the website's terms of service and Princeton University's policies.

## GitHub Actions Workflow

This repository includes a GitHub Actions workflow that can generate the PDF and JSON outputs automatically.

### Manual Dispatch
Go to the Actions tab in your GitHub repository, select "Generate Symposium Schedule", and click "Run workflow". You can choose options for:
- **Show headers**: Include column headers in the PDF table
- **Allow breaks**: Allow page breaks within room sections

### Caching
The workflow includes intelligent caching that checks if the source webpage has changed. If no changes are detected since the last run, the workflow exits early without regenerating the files, saving time and resources.

### Outputs
The workflow generates two artifacts with stable download URLs:
- `symposium-schedule-pdf`: Contains the formatted PDF
- `symposium-schedule-json`: Contains the structured JSON data

These artifacts are available for download from the workflow run page.