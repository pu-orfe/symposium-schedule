import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from playwright.sync_api import sync_playwright
import argparse
import json
import hashlib

def scrape_schedule():
    url = "https://symposium.orfe.princeton.edu"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        page.goto(url)
        page.wait_for_timeout(5000)
        content = page.content()
        browser.close()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    rooms = {}
    current_room = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line in ['001 - Sherrerd Hall', '003 - Sherrerd Hall', '101 - Sherrerd Hall', '107 - Sherrerd Hall', '110 - Sherrerd Hall', '123 - Sherrerd Hall', '125 - Sherrerd Hall']:
            room = line.split(' - ')[0]
            current_room = room
            rooms[current_room] = {'advisors': '', 'graders': '', 'schedule': []}
        elif current_room and 'ORFE Advisors:' in line and 'PhD Candidate Graders:' in line:
            parts = line.split('PhD Candidate Graders:')
            rooms[current_room]['advisors'] = parts[0]
            rooms[current_room]['graders'] = 'PhD Candidate Graders:' + parts[1]
        elif current_room and 'ORFE Advisors:' in line:
            rooms[current_room]['advisors'] = line
        elif current_room and 'PhD Candidate Graders:' in line:
            rooms[current_room]['graders'] = line
        elif current_room and ('am – ' in line or 'pm – ' in line):
            time = line
            i += 1
            presenter = ''
            while i < len(lines):
                next_line = lines[i]
                if next_line and next_line != 'Link downloads document':
                    presenter = next_line.split(' Link')[0]
                    break
                i += 1
            rooms[current_room]['schedule'].append((time, presenter))
        i += 1
    return rooms

def create_pdf(rooms, filename, keep_together=True, show_headers=False, include_title=True):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    
    # Custom style for table text and advisors/graders
    table_style = ParagraphStyle(
        'TableStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica',
        leading=20,  # Increased line spacing
    )
    
    # Custom style for room titles
    room_style = ParagraphStyle(
        'RoomStyle',
        parent=styles['Heading2'],
        fontSize=18,
        fontName='Helvetica-Bold',
        spaceAfter=12,
    )
    
    story = []
    if include_title:
        story.append(Paragraph("Class of 2026 ORFE Thesis Symposium Schedule", title_style))
        story.append(Spacer(1, 12))
    
    for room, data in sorted(rooms.items()):
        room_elements = []
        room_elements.append(Paragraph(f"Room {room} - Sherrerd Hall", room_style))
        if data['advisors']:
            room_elements.append(Paragraph(data['advisors'], table_style))
        if data['graders']:
            room_elements.append(Paragraph(data['graders'], table_style))
        room_elements.append(Spacer(1, 6))
        
        # Table for schedule
        table_data = []
        if show_headers:
            table_data.append(['Time', 'Presenter'])
        for time, presenter in data['schedule']:
            table_data.append([time, presenter])
        
        table = Table(table_data, colWidths=[200, 200])  # Adjust to fit within margins
        # table.hAlign = 'LEFT'  # Remove to center the table
        
        styles_list = []
        if show_headers:
            # Header row styling
            styles_list.extend([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 16),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('LEADING', (0,0), (-1,0), 18),
                # Data rows
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 14),
                ('LEADING', (0,1), (-1,-1), 16),
                ('TOPPADDING', (0,1), (-1,-1), 6),
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ])
        else:
            # All rows are data
            styles_list.extend([
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 14),
                ('LEADING', (0,0), (-1,-1), 16),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ])
        
        styles_list.extend([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ])
        
        table.setStyle(TableStyle(styles_list))
        room_elements.append(table)
        room_elements.append(Spacer(1, 12))
        
        if keep_together:
            story.append(KeepTogether(room_elements))
        else:
            story.extend(room_elements)
    
    doc.build(story)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape symposium schedule and generate PDF or JSON.")
    parser.add_argument('--json', action='store_true', help="Output data as JSON instead of generating PDF.")
    parser.add_argument('--allow-breaks', action='store_true', help="Allow page breaks within room sections (default: keep rooms together).")
    parser.add_argument('--show-headers', action='store_true', help="Show table headers (Time, Presenter) in PDF.")
    parser.add_argument('--hash', action='store_true', help="Output hash of the schedule data instead of generating files.")
    parser.add_argument('--no-title', action='store_true', help="Exclude the title from PDF output.")
    args = parser.parse_args()
    
    rooms = scrape_schedule()
    
    if args.hash:
        hash_obj = hashlib.sha256(json.dumps(rooms, sort_keys=True).encode())
        print(hash_obj.hexdigest())
    elif args.json:
        json_output = json.dumps(rooms, indent=2)
        with open("symposium_schedule.json", "w") as f:
            f.write(json_output)
        print(json_output)
    else:
        create_pdf(rooms, "symposium_schedule.pdf", keep_together=not args.allow_breaks, show_headers=args.show_headers, include_title=not args.no_title)