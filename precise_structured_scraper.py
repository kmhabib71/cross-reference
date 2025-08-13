



#!/usr/bin/env python3
"""
Precise Structured Legal Document Scraper
Based on actual HTML structure from Bangladesh Laws website
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class DocumentHeader:
    title: str  # From h3 tag
    ordinance_info: str  # From h4 tag 
    publish_date: str  # From .publish-date
    introduction: str  # From act-role-style section

@dataclass
class TableCell:
    content: str
    colspan: int
    rowspan: int
    is_header: bool

@dataclass
class TableRow:
    cells: List[TableCell]

@dataclass
class LegalTable:
    caption: str
    headers: List[str]
    rows: List[TableRow]
    context: str

@dataclass
class SubClause:
    identifier: str  # (অ), (আ), (ই) etc.
    text: str

@dataclass
class Clause:
    identifier: str  # (ক), (খ), (গ) etc.
    text: str
    sub_clauses: List[SubClause]
    tables: List[LegalTable]  # Tables associated with this clause

@dataclass
class Subsection:
    identifier: str  # (১), (২), (৩) etc.
    text: str
    clauses: List[Clause]
    tables: List[LegalTable]  # Tables associated with this subsection

@dataclass
class Footnote:
    number: str  # Footnote identifier (1, 2, *, **, etc.)
    text: str  # Footnote content
    position: str  # Where it appears (header, section, clause, etc.)

@dataclass
class Section:
    number: str  # ১, ২, ৩ etc.
    title: str  # From txt-head div
    content_text: str  # Main section text
    subsections: List[Subsection]
    clauses: List[Clause]  # Direct clauses (when no subsections)
    tables: List[LegalTable]
    footnotes: List[Footnote]  # Footnotes associated with this section

@dataclass
class Chapter:
    number: str  # প্রথম, দ্বিতীয় etc.
    title: str  # From act-chapter-name
    sections: List[Section]

@dataclass
class Part:
    number: str  # অংশ ১, অংশ ২ etc.
    title: str  # From act-part-name
    chapters: List[Chapter]
    sections: List[Section]  # Direct sections under part (when no chapters)

@dataclass
class StructuredLegalDocument:
    header: DocumentHeader
    chapters: List[Chapter]  # For documents without parts
    parts: List[Part]  # For documents with parts
    has_parts: bool  # Indicates whether document uses part structure
    scraped_at: str
    url: str

class PreciseStructuredScraper:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing excessive whitespace and formatting"""
        if not text:
            return ""
        
        # Remove excessive whitespace, newlines, and carriage returns
        text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
        text = re.sub(r'\r\n|\r|\n', ' ', text)  # Replace line breaks with space
        text = text.strip()  # Remove leading/trailing whitespace
        
        return text

    def clean_content_text(self, text: str) -> str:
        """Clean content text while preserving necessary line breaks"""
        if not text:
            return ""
        
        # Split into lines and clean each
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = re.sub(r'\s+', ' ', line.strip())  # Clean excessive spaces
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join with single newlines
        return '\n'.join(cleaned_lines)

    def convert_to_bengali_numerals(self, text: str) -> str:
        """Convert English numerals to Bengali numerals"""
        if not text:
            return ""
        
        # Mapping from English to Bengali numerals
        english_to_bengali = {
            '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
            '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
        }
        
        result = text
        for eng, ben in english_to_bengali.items():
            result = result.replace(eng, ben)
        
        return result

    def convert_to_english_numerals(self, text: str) -> str:
        """Convert Bengali numerals to English numerals"""
        if not text:
            return ""
        
        # Mapping from Bengali to English numerals
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = text
        for ben, eng in bengali_to_english.items():
            result = result.replace(ben, eng)
        
        return result

    def remove_table_content_from_text(self, text: str, tables: List[LegalTable]) -> str:
        """Remove table content from section text to avoid duplication"""
        if not tables:
            return text
        
        # Split text into paragraphs
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip if this line looks like table content
            should_skip = False
            
            for table in tables:
                # Skip table caption
                if table.caption and table.caption.strip() in line:
                    should_skip = True
                    break
                    
                # Skip table headers
                for header in table.headers:
                    if header and len(header) > 5 and header in line:
                        should_skip = True
                        break
                
                if should_skip:
                    break
                    
                # Skip table row content
                for row in table.rows:
                    for cell in row.cells:
                        cell_content = cell.content.strip()
                        if cell_content and len(cell_content) > 5:
                            # If this line is mostly this cell content, skip it
                            if cell_content in line and len(cell_content) > len(line) * 0.7:
                                should_skip = True
                                break
                    if should_skip:
                        break
                if should_skip:
                    break
            
            # Skip lines that look like table structure
            if not should_skip:
                # Skip lines with table-like patterns
                if re.match(r'^[০-৯0-9\.\s\,\(\)-]+$', line) and len(line) < 30:
                    should_skip = True
                elif any(word in line.lower() for word in ['heading', 'description', 'goods', 'rate', 'h.s.', 'code', 'শিরনামা', 'বিবরণ']):
                    should_skip = True
            
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join cleaned lines
        cleaned_text = '\n'.join(cleaned_lines)
        return self.clean_content_text(cleaned_text)

    def extract_document_header(self, soup: BeautifulSoup) -> DocumentHeader:
        """Extract document header information"""
        
        # Title from h3 in bg-act-section
        title = ""
        title_elem = soup.find('section', class_='bg-act-section')
        if title_elem:
            h3_elem = title_elem.find('h3')
            if h3_elem:
                title = self.clean_text(h3_elem.get_text())
        
        # Ordinance info from h4
        ordinance_info = ""
        if title_elem:
            h4_elem = title_elem.find('h4')
            if h4_elem:
                ordinance_info = self.clean_text(h4_elem.get_text())
        
        # Publish date from .publish-date
        publish_date = ""
        date_elem = soup.find('p', class_='publish-date')
        if date_elem:
            publish_date = self.clean_text(date_elem.get_text())
        
        # Introduction from act-role-style
        introduction = ""
        intro_elem = soup.find('div', class_='act-role-style')
        if intro_elem:
            # Get all p tags in the introduction
            intro_parts = []
            for p in intro_elem.find_all('p'):
                text = self.clean_text(p.get_text())
                if text:
                    intro_parts.append(text)
            introduction = '\n'.join(intro_parts)
        
        return DocumentHeader(
            title=title,
            ordinance_info=ordinance_info,
            publish_date=publish_date,
            introduction=introduction
        )
    
    def parse_table(self, table_elem: BeautifulSoup, context: str = "") -> LegalTable:
        """Parse table structure with precise handling"""
        
        # Extract caption (if any)
        caption = ""
        # Look for table caption in preceding elements
        prev_elem = table_elem.find_previous_sibling()
        while prev_elem and prev_elem.name in ['p', 'strong']:
            text = prev_elem.get_text().strip()
            if 'টেবিল' in text or 'Table' in text:
                caption = text
                break
            prev_elem = prev_elem.find_previous_sibling()
        
        # Get table rows
        rows = table_elem.find_all('tr')
        if not rows:
            return None
        
        # Extract headers from thead or first row
        headers = []
        thead = table_elem.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            if len(header_rows) >= 1:
                # Use first row for headers
                for cell in header_rows[0].find_all(['th', 'td']):
                    headers.append(self.clean_content_text(cell.get_text()))
        
        # Parse data rows (skip header rows)
        data_rows = []
        tbody = table_elem.find('tbody')
        if tbody:
            table_rows = tbody.find_all('tr')
        else:
            # Skip header rows manually
            table_rows = rows[2:] if thead and len(rows) > 2 else rows[1:] if len(rows) > 1 else rows
        
        for row in table_rows:
            cells = []
            for cell in row.find_all(['td', 'th']):
                table_cell = TableCell(
                    content=self.clean_content_text(cell.get_text()),
                    colspan=int(cell.get('colspan', 1)),
                    rowspan=int(cell.get('rowspan', 1)),
                    is_header=cell.name == 'th'
                )
                cells.append(table_cell)
            
            if cells:
                data_rows.append(TableRow(cells=cells))
        
        return LegalTable(
            caption=caption,
            headers=headers,
            rows=data_rows,
            context=context
        )
    
    def parse_subsections_clauses_subclauses(self, section_content: str) -> tuple:
        """Parse subsections, clauses and subclauses from section content"""
        
        subsections = []
        direct_clauses = []  # Clauses not under any subsection
        
        # Remove section number from beginning if present
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        for para in paragraphs:
            # Check if this is a subsection using Bengali numbers (১), (২), (৩) etc.
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                # Save previous subsection/clause if exists
                if current_clause and current_subsection:
                    current_subsection.clauses.append(current_clause)
                    current_clause = None
                elif current_clause and not current_subsection:
                    direct_clauses.append(current_clause)
                    current_clause = None
                    
                if current_subsection:
                    subsections.append(current_subsection)
                
                # Start new subsection
                subsection_id = subsection_match.group(1)
                subsection_text = self.clean_text(para[subsection_match.end():])
                
                current_subsection = Subsection(
                    identifier=subsection_id,
                    text=subsection_text,
                    clauses=[]
                )
            
            # Check if this is a main clause using Bengali letters (ক), (খ), (গ), (ঘ), (ঙ), (চ), (ছ), (জ), (ঝ), (ঞ) etc.
            elif re.match(r'^\(([ক-হ])\)', para):
                clause_match = re.match(r'^\(([ক-হ])\)', para)
                
                # Save previous clause
                if current_clause:
                    if current_subsection:
                        current_subsection.clauses.append(current_clause)
                    else:
                        direct_clauses.append(current_clause)
                
                # Start new clause
                clause_id = clause_match.group(1)
                clause_text = self.clean_text(para[clause_match.end():])
                
                current_clause = Clause(
                    identifier=clause_id,
                    text=clause_text,
                    sub_clauses=[]
                )
            
            # Check if this is a sub-clause using Bengali vowels (অ), (আ), (ই), (ঈ), (উ), (ঊ) etc.
            elif re.match(r'^\(([অ-ঔ])\)', para):
                subclause_match = re.match(r'^\(([অ-ঔ])\)', para)
                if subclause_match and current_clause:
                    subclause_id = subclause_match.group(1)
                    subclause_text = self.clean_text(para[subclause_match.end():])
                    
                    sub_clause = SubClause(
                        identifier=subclause_id,
                        text=subclause_text
                    )
                    current_clause.sub_clauses.append(sub_clause)
            
            # Regular content - add to current clause or subsection
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para:  # Only add non-empty content
                    if current_clause:
                        if current_clause.text:
                            current_clause.text += ' ' + cleaned_para
                        else:
                            current_clause.text = cleaned_para
                    elif current_subsection:
                        if current_subsection.text:
                            current_subsection.text += ' ' + cleaned_para
                        else:
                            current_subsection.text = cleaned_para
        
        # Add the last clause and subsection
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def parse_subsections_clauses_subclauses_with_tables(self, section_content: str, section_div, section_title: str) -> tuple:
        """Parse subsections, clauses and subclauses with table association"""
        
        subsections = []
        direct_clauses = []
        
        # Remove section number from beginning if present
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        # Find tables for potential association
        all_tables = []
        for table_elem in section_div.find_all('table'):
            table = self.parse_table(table_elem, section_title)
            if table:
                all_tables.append(table)
        
        for para in paragraphs:
            # Skip if this paragraph looks like table content
            if self.looks_like_table_content(para):
                continue
                
            # Check if this is a subsection using Bengali numbers (১), (২), (৩) etc.
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                # Save previous subsection/clause if exists
                if current_clause and current_subsection:
                    current_subsection.clauses.append(current_clause)
                    current_clause = None
                elif current_clause and not current_subsection:
                    direct_clauses.append(current_clause)
                    current_clause = None
                    
                if current_subsection:
                    subsections.append(current_subsection)
                
                # Start new subsection
                subsection_id = subsection_match.group(1)
                subsection_text = self.clean_text(para[subsection_match.end():])
                
                current_subsection = Subsection(
                    identifier=subsection_id,
                    text=subsection_text,
                    clauses=[],
                    tables=[]
                )
            
            # Check if this is a main clause using Bengali letters (ক), (খ), (গ), (ঘ), (ঙ), (চ), (ছ), (জ), (ঝ), (ঞ) etc.
            elif re.match(r'^\(([ক-হ])\)', para):
                clause_match = re.match(r'^\(([ক-হ])\)', para)
                
                # Save previous clause
                if current_clause:
                    if current_subsection:
                        current_subsection.clauses.append(current_clause)
                    else:
                        direct_clauses.append(current_clause)
                
                # Start new clause
                clause_id = clause_match.group(1)
                clause_text = self.clean_text(para[clause_match.end():])
                
                # Check if this clause mentions a table (like "টেবিল-১")
                associated_tables = []
                # Don't associate tables with clauses to avoid duplication
                # Tables will be associated at section level only
                
                current_clause = Clause(
                    identifier=clause_id,
                    text=clause_text,
                    sub_clauses=[],
                    tables=[]  # No tables at clause level to avoid duplication
                )
            
            # Check if this is a sub-clause using Bengali vowels (অ), (আ), (ই), (ঈ), (উ), (ঊ) etc.
            elif re.match(r'^\(([অ-ঔ])\)', para):
                subclause_match = re.match(r'^\(([অ-ঔ])\)', para)
                if subclause_match and current_clause:
                    subclause_id = subclause_match.group(1)
                    subclause_text = self.clean_text(para[subclause_match.end():])
                    
                    sub_clause = SubClause(
                        identifier=subclause_id,
                        text=subclause_text
                    )
                    current_clause.sub_clauses.append(sub_clause)
            
            # Regular content - add to current clause or subsection
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para and not self.looks_like_table_content(cleaned_para):
                    if current_clause:
                        if current_clause.text:
                            current_clause.text += ' ' + cleaned_para
                        else:
                            current_clause.text = cleaned_para
                    elif current_subsection:
                        if current_subsection.text:
                            current_subsection.text += ' ' + cleaned_para
                        else:
                            current_subsection.text = cleaned_para
        
        # Add the last clause and subsection
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def looks_like_table_content(self, text: str) -> bool:
        """Check if text looks like table content that should be skipped"""
        if not text:
            return False
            
        text = text.strip()
        
        # Skip very short numeric-only content that might be table data
        if re.match(r'^[০-৯০-৯a-zA-Z\s\.,\-\(\)]+$', text) and len(text) < 50:
            return True
            
        # Skip content that looks like table headers
        if any(word in text.lower() for word in ['heading', 'description', 'rate', 'h.s.', 'code']):
            return True
            
        # Skip content with lots of numbers and symbols (likely table data)
        if len(re.findall(r'[০-৯0-9\.\,\%]', text)) > len(text) * 0.3:
            return True
            
        return False

    def extract_footnotes(self, section_div, section_number: str) -> List[Footnote]:
        """Extract footnotes from section HTML elements"""
        footnotes = []
        
        # Find all footnote span elements in the section
        footnote_spans = section_div.find_all('span', class_='footnote')
        
        for footnote_span in footnote_spans:
            # Get the footnote title (actual footnote text)
            footnote_text = footnote_span.get('title', '')
            
            # Get the footnote number/marker from the link or sup element
            footnote_number = ""
            link_elem = footnote_span.find('a')
            if link_elem:
                footnote_number = link_elem.get_text().strip()
            else:
                # Fallback: try to find sup element
                sup_elem = footnote_span.find('sup')
                if sup_elem:
                    footnote_number = sup_elem.get_text().strip()
            
            # Only add if we have both number and text
            if footnote_number and footnote_text:
                footnote = Footnote(
                    number=footnote_number,  # The footnote number (like 302, 1, 2, etc.)
                    text=footnote_text,  # The actual footnote content from title attribute
                    position=f"section_{section_number}"
                )
                footnotes.append(footnote)
        
        return footnotes

    def extract_structured_content(self, soup: BeautifulSoup) -> tuple:
        """Extract structured content with support for Parts and Chapters"""
        
        chapters = []
        parts = []
        
        # Check if document has parts (অংশ) vs chapters (অধ্যায়)
        part_groups = soup.find_all('div', class_='act-part-group')
        chapter_groups = soup.find_all('div', class_='act-chapter-group')
        all_section_divs = soup.find_all('div', class_='row lineremoves')
        
        # Detect if 'act-part-group' elements actually contain chapters (অধ্যায়) instead of parts (অংশ)
        has_actual_parts = False
        if part_groups:
            # Check first few part groups for content
            for part_group in part_groups[:3]:
                part_text = part_group.get_text().strip()
                # Check for chapter patterns (more reliable than exact string match due to encoding issues)
                chapter_patterns = ['প্রথম', 'দ্বিতীয়', 'তৃতীয়', 'চতুর্থ', 'পঞ্চম', 'ষষ্ঠ', 'সপ্তম', 'অষ্টম']
                is_chapter = any(pattern in part_text for pattern in chapter_patterns)
                if is_chapter:
                    # This document uses act-part-group for chapters, not parts
                    print("🔄 Detected: act-part-group contains chapters (অধ্যায়), not parts (অংশ)")
                    chapter_groups = part_groups  # Treat part_groups as chapters
                    part_groups = []  # No actual parts
                    has_actual_parts = False
                    print(f"🔄 Reassigned: Now using {len(chapter_groups)} chapter groups from act-part-group")
                    break
                elif 'অংশ' in part_text:
                    has_actual_parts = True
                    break
        
        # If no 'row lineremoves' found, try just 'row' class
        if not all_section_divs:
            all_section_divs = soup.find_all('div', class_='row')
            print(f"🔍 Found {len(part_groups)} parts, {len(chapter_groups)} chapters and {len(all_section_divs)} potential sections (using 'row' class)")
        else:
            print(f"🔍 Found {len(part_groups)} parts, {len(chapter_groups)} chapters and {len(all_section_divs)} potential sections")
        
        has_parts = has_actual_parts and len(part_groups) > 0
        print(f"📋 Document structure: {'Parts → Chapters → Sections' if has_parts else 'Chapters → Sections'}")
        
        # Filter to only section divs with txt-head and txt-details, or try broader search
        section_divs_with_content = []
        for div in all_section_divs:
            txt_head = div.find('div', class_='txt-head')
            txt_details = div.find('div', class_='txt-details')
            if txt_head and txt_details:
                section_divs_with_content.append(div)
        
        # If no sections found with txt-head/txt-details, try broader approach
        if not section_divs_with_content:
            print("🔄 No txt-head/txt-details found, trying broader section detection...")
            # Look for divs that contain section numbers
            for div in all_section_divs:
                div_text = div.get_text()
                if re.search(r'[০-৯]+।', div_text):  # Contains Bengali section numbers
                    section_divs_with_content.append(div)
        
        print(f"✅ Found {len(section_divs_with_content)} sections with content")
        
        # Extract all sections first, with their numbers
        all_sections = []
        processed_section_numbers = set()
        
        for section_div in section_divs_with_content:
            txt_head = section_div.find('div', class_='txt-head')
            txt_details = section_div.find('div', class_='txt-details')
            
            # Handle both old structure (txt-head/txt-details) and new structure (direct content)
            if txt_head and txt_details:
                section_title = self.clean_text(txt_head.get_text())
                
                # Extract section content without table HTML elements
                txt_details_copy = txt_details.__copy__()
                
                # Remove table elements from the copy before extracting text
                for table_elem in txt_details_copy.find_all('table'):
                    table_elem.decompose()  # Remove table HTML
                    
                section_content = self.clean_content_text(txt_details_copy.get_text())
            else:
                # New structure - extract directly from div
                section_title = "Section"  # Default title
                
                # Extract section content without table HTML elements
                section_div_copy = section_div.__copy__()
                
                # Remove table elements from the copy before extracting text
                for table_elem in section_div_copy.find_all('table'):
                    table_elem.decompose()  # Remove table HTML
                    
                section_content = self.clean_content_text(section_div_copy.get_text())
            
            # Extract section number from content (both Bengali and English numbers)
            section_number = ""
            # Look for section number anywhere in the content, including those with footnotes
            
            # Pattern 1: Bengali section number followed by period, possibly with footnotes
            section_matches = re.findall(r'([০-৯]+)(?:\[[^\]]*\])*।', section_content)
            if not section_matches:
                # Pattern 2: English section number with footnotes but no period  
                section_matches = re.findall(r'([0-9]+)\[[^\]]*\]', section_content)
                # Convert English to Bengali numerals
                if section_matches:
                    section_matches = [self.convert_to_bengali_numerals(match) for match in section_matches]
            if not section_matches:
                # Pattern 3: Bengali section number with footnotes
                section_matches = re.findall(r'([০-৯]+)\[[^\]]*\]', section_content)
            if not section_matches:
                # Pattern 4: Simple Bengali section number
                section_matches = re.findall(r'([০-৯]+)', section_content)
            if not section_matches:
                # Pattern 5: Simple English section number (convert to Bengali)
                english_matches = re.findall(r'([0-9]+)', section_content)
                if english_matches:
                    section_matches = [self.convert_to_bengali_numerals(match) for match in english_matches]
            
            if not section_matches:
                print(f"⚠️ No section number found in: {section_content[:100]}...")
                continue
            
            # Take the first section number that looks reasonable (1-999)
            section_number = None
            for match in section_matches:
                try:
                    # Convert Bengali numerals to int for validation
                    num_value = int(self.convert_to_english_numerals(match))
                    if 1 <= num_value <= 999:
                        section_number = match
                        break
                except:
                    continue
            
            if not section_number:
                print(f"⚠️ No valid section number found in: {section_content[:100]}...")
                continue
            
            # Skip duplicates
            if section_number in processed_section_numbers:
                continue
            processed_section_numbers.add(section_number)
            
            # Look for tables in this section
            tables = []
            for table_elem in section_div.find_all('table'):
                table = self.parse_table(table_elem, section_title)
                if table:
                    tables.append(table)
            
            # Parse subsections, clauses and subclauses from content without tables
            subsections, direct_clauses = self.parse_subsections_clauses_subclauses_with_tables(
                section_content, section_div, section_title
            )
            
            # Extract footnotes from section HTML elements
            footnotes = self.extract_footnotes(section_div, section_number)
            
            # Create section object
            section = Section(
                number=section_number,
                title=section_title,
                content_text=section_content, # Use content without table HTML
                subsections=subsections,
                clauses=direct_clauses,
                tables=tables,
                footnotes=footnotes
            )
            
            all_sections.append(section)
        
        # Sort sections by number to ensure proper order
        all_sections.sort(key=lambda x: int(x.number))
        
        if has_parts:
            # Handle document with Parts structure
            parts = self.assign_sections_to_parts(part_groups, chapter_groups, all_sections, soup)
            return chapters, parts, True
        else:
            # Handle document with only Chapters structure (original logic)
            chapters = self.assign_sections_to_chapters_only(chapter_groups, all_sections)
            return chapters, [], False
    
    def assign_sections_to_parts(self, part_groups, chapter_groups, all_sections, soup) -> List[Part]:
        """Assign sections to parts, with or without chapters"""
        parts = []
        
        # For each part, we need to determine its position in the document
        # and find which chapters and sections belong to it
        all_structural_elements = []
        
        # Build ordered list of all structural elements (parts, chapters)
        for elem in soup.find_all(['div']):
            if 'act-part-group' in elem.get('class', []):
                all_structural_elements.append(('part', elem))
            elif 'act-chapter-group' in elem.get('class', []):
                all_structural_elements.append(('chapter', elem))
        
        current_part = None
        current_part_chapters = []
        current_chapter_sections = []
        section_index = 0
        
        for elem_type, elem in all_structural_elements:
            if elem_type == 'part':
                # Save previous part if exists
                if current_part:
                    # Assign remaining sections to last chapter or directly to part
                    if current_part_chapters:
                        current_part_chapters[-1].sections.extend(current_chapter_sections)
                        current_part.chapters = current_part_chapters
                        current_part.sections = []
                    else:
                        current_part.sections = current_chapter_sections
                    parts.append(current_part)
                
                # Extract part info
                part_no_elem = elem.find('p', class_='act-part-no')
                part_name_elem = elem.find('p', class_='act-part-name')
                
                if part_no_elem and part_name_elem:
                    part_number = part_no_elem.get_text().strip()
                    part_title = part_name_elem.get_text().strip()
                    
                    current_part = Part(
                        number=part_number,
                        title=part_title,
                        chapters=[],
                        sections=[]
                    )
                    current_part_chapters = []
                    current_chapter_sections = []
            
            elif elem_type == 'chapter':
                # Save previous chapter sections
                if current_chapter_sections:
                    if current_part_chapters:
                        current_part_chapters[-1].sections.extend(current_chapter_sections)
                    current_chapter_sections = []
                
                # Extract chapter info
                chapter_no_elem = elem.find('p', class_='act-chapter-no')
                chapter_name_elem = elem.find('p', class_='act-chapter-name')
                
                if chapter_no_elem and chapter_name_elem:
                    chapter_number = chapter_no_elem.get_text().strip()
                    chapter_title = chapter_name_elem.get_text().strip()
                    
                    chapter = Chapter(
                        number=chapter_number,
                        title=chapter_title,
                        sections=[]
                    )
                    current_part_chapters.append(chapter)
        
        # Handle remaining sections - assign all remaining to current structure
        remaining_sections = all_sections[section_index:]
        if current_part:
            if current_part_chapters:
                if current_part_chapters:
                    current_part_chapters[-1].sections.extend(remaining_sections)
                current_part.chapters = current_part_chapters
                current_part.sections = []
            else:
                current_part.sections = remaining_sections
            parts.append(current_part)
        
        return parts
    
    def assign_sections_to_chapters_only(self, chapter_groups, all_sections) -> List[Chapter]:
        """Original logic for documents without parts"""
        chapters = []
        
        # Use flexible assignment instead of hardcoded ranges
        # Distribute sections evenly across chapters
        sections_per_chapter = len(all_sections) // max(len(chapter_groups), 1) if chapter_groups else 0
        section_index = 0
        
        for chapter_idx, chapter_group in enumerate(chapter_groups):
            # Extract chapter info - handle both standard and VAT Act structures
            chapter_no_elem = chapter_group.find('p', class_='act-chapter-no')
            chapter_name_elem = chapter_group.find('p', class_='act-chapter-name')
            
            # If standard structure not found, try alternative structure (like VAT Act)
            if not chapter_no_elem or not chapter_name_elem:
                # Look for chapter info in the div's text content
                chapter_text = chapter_group.get_text().strip()
                lines = [line.strip() for line in chapter_text.split('\n') if line.strip()]
                
                if len(lines) >= 2:
                    # First non-empty line is chapter number, second is title
                    chapter_number = lines[0]
                    chapter_title = lines[1]
                else:
                    # Fallback: use whatever text we can find
                    chapter_number = f"Chapter {chapter_idx + 1}"
                    chapter_title = chapter_text[:100] if chapter_text else f"Chapter {chapter_idx + 1}"
            else:
                chapter_number = chapter_no_elem.get_text().strip()
                chapter_title = chapter_name_elem.get_text().strip()
            
            # Assign sections to this chapter
            if chapter_idx == len(chapter_groups) - 1:
                # Last chapter gets all remaining sections
                chapter_sections = all_sections[section_index:]
            else:
                # Other chapters get their portion
                chapter_sections = all_sections[section_index:section_index + sections_per_chapter]
                section_index += sections_per_chapter
            
            # Create chapter object
            chapter = Chapter(
                number=chapter_number,
                title=chapter_title,
                sections=chapter_sections
            )
            
            chapters.append(chapter)
        
        return chapters
    
    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Scrape document with precise structure extraction"""
        
        print(f"🔄 Scraping: {url}")
        
        try:
            # First establish session with main site
            try:
                self.session.get(self.base_url, timeout=10)
                print("📡 Session established")
            except:
                pass # Continue even if main site request fails

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            print(f"📄 Content size: {len(response.content)} bytes")

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract header information
            header = self.extract_document_header(soup)
            
            # Extract structured content
            chapters, parts, has_parts = self.extract_structured_content(soup)
            
            # Count elements based on structure
            if has_parts:
                total_sections = sum(len(part.sections) + sum(len(ch.sections) for ch in part.chapters) for part in parts)
                total_subsections = sum(
                    sum(len(sec.subsections) for sec in part.sections) + 
                    sum(len(sec.subsections) for ch in part.chapters for sec in ch.sections)
                    for part in parts
                )
                total_tables = sum(
                    sum(len(sec.tables) for sec in part.sections) + 
                    sum(len(sec.tables) for ch in part.chapters for sec in ch.sections)
                    for part in parts
                )
                total_clauses = sum(
                    sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) for sec in part.sections) + 
                    sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) for ch in part.chapters for sec in ch.sections)
                    for part in parts
                )
            else:
                total_sections = sum(len(ch.sections) for ch in chapters)
                total_subsections = sum(len(sec.subsections) for ch in chapters for sec in ch.sections)
                total_tables = sum(len(sec.tables) for ch in chapters for sec in ch.sections)
                total_clauses = sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) 
                                  for ch in chapters for sec in ch.sections)
            
            # Create document
            document = StructuredLegalDocument(
                header=header,
                chapters=chapters,
                parts=parts,
                has_parts=has_parts,
                scraped_at=datetime.now().isoformat(),
                url=url
            )
            
            print(f"✅ {header.title}")
            if has_parts:
                print(f"   📁 Parts: {len(parts)}")
                print(f"   📚 Chapters: {sum(len(part.chapters) for part in parts)}")
            else:
                print(f"   📚 Chapters: {len(chapters)}")
            print(f"   📋 Sections: {total_sections}")
            print(f"   📄 Subsections: {total_subsections}")
            print(f"   🔹 Clauses: {total_clauses}")
            print(f"   📊 Tables: {total_tables}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_document(self, document: StructuredLegalDocument, output_dir: str = 'precise_structured_laws'):
        """Save document with precise structure"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        clean_title = re.sub(r'[^\w\s-]', '', document.header.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        # Convert to dict (handling dataclasses recursively)
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert_dataclass(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [convert_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_dataclass(v) for k, v in obj.items()}
            else:
                return obj
        
        document_dict = convert_dataclass(document)
        
        # Add summary statistics
        if document.has_parts:
            document_dict['structure_summary'] = {
                'has_parts': True,
                'total_parts': len(document.parts),
                'total_chapters': sum(len(part.chapters) for part in document.parts),
                'total_sections': sum(len(part.sections) + sum(len(ch.sections) for ch in part.chapters) for part in document.parts),
                'total_subsections': sum(
                    sum(len(sec.subsections) for sec in part.sections) + 
                    sum(len(sec.subsections) for ch in part.chapters for sec in ch.sections)
                    for part in document.parts
                ),
                'total_clauses': sum(
                    sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) for sec in part.sections) + 
                    sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) for ch in part.chapters for sec in ch.sections)
                    for part in document.parts
                ),
                'total_tables': sum(
                    sum(len(sec.tables) for sec in part.sections) + 
                    sum(len(sec.tables) for ch in part.chapters for sec in ch.sections)
                    for part in document.parts
                ),
                'parts_breakdown': [
                    {
                        'part_number': part.number,
                        'part_title': part.title,
                        'chapters_count': len(part.chapters),
                        'direct_sections_count': len(part.sections),
                        'chapters_breakdown': [
                            {
                                'chapter_number': ch.number,
                                'chapter_title': ch.title,
                                'sections_count': len(ch.sections)
                            }
                            for ch in part.chapters
                        ]
                    }
                    for part in document.parts
                ]
            }
        else:
            document_dict['structure_summary'] = {
                'has_parts': False,
                'total_chapters': len(document.chapters),
                'total_sections': sum(len(ch.sections) for ch in document.chapters),
                'total_subsections': sum(len(sec.subsections) for ch in document.chapters for sec in ch.sections),
                'total_clauses': sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) 
                                   for ch in document.chapters for sec in ch.sections),
                'total_tables': sum(len(sec.tables) for ch in document.chapters for sec in ch.sections),
                'chapters_breakdown': [
                    {
                        'chapter_number': ch.number,
                        'chapter_title': ch.title,
                        'sections_count': len(ch.sections)
                    }
                    for ch in document.chapters
                ]
            }
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {filepath}")
        return filepath

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python precise_structured_scraper.py <url1> <url2> ... or --file <urls.txt>")
        return
    
    scraper = PreciseStructuredScraper()
    
    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = sys.argv[1:]
    
    print(f"🎯 PRECISE STRUCTURED SCRAPER")
    print(f"📋 URLs: {len(urls)}")
    print("=" * 50)
    
    for url in urls:
        document = scraper.scrape_document(url)
        if document:
            scraper.save_document(document)

if __name__ == "__main__":
    main()