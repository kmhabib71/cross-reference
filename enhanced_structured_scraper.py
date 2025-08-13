#!/usr/bin/env python3
"""
Enhanced Structured Legal Document Scraper
==========================================

Enhanced version that properly extracts content in exact website format:
- অংশ (Parts) → অধ্যায় (Chapters) → ধারা (Sections)
- Proper section-to-part/chapter mapping based on HTML structure
- Maintains serialized section numbering across all parts

Author: Phase 2.5 Integration Team
Date: August 13, 2025
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
    title: str
    ordinance_info: str
    publish_date: str
    introduction: str

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
    identifier: str
    text: str

@dataclass
class Clause:
    identifier: str
    text: str
    sub_clauses: List[SubClause]
    tables: List[LegalTable]

@dataclass
class Subsection:
    identifier: str
    text: str
    clauses: List[Clause]
    tables: List[LegalTable]

@dataclass
class Footnote:
    number: str
    text: str
    position: str

@dataclass
class Section:
    number: str
    title: str
    content_text: str
    subsections: List[Subsection]
    clauses: List[Clause]
    tables: List[LegalTable]
    footnotes: List[Footnote]

@dataclass
class Chapter:
    number: str
    title: str
    sections: List[Section]

@dataclass
class Part:
    number: str
    title: str
    chapters: List[Chapter]
    sections: List[Section]

@dataclass
class StructuredLegalDocument:
    header: DocumentHeader
    chapters: List[Chapter]
    parts: List[Part]
    has_parts: bool
    scraped_at: str
    url: str

class EnhancedStructuredScraper:
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
        """Clean text by removing excessive whitespace"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        return text.strip()

    def clean_content_text(self, text: str) -> str:
        """Clean content text while preserving structure"""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)

    def convert_to_bengali_numerals(self, text: str) -> str:
        """Convert English numerals to Bengali numerals"""
        if not text:
            return ""
        
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
        
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        result = text
        for ben, eng in bengali_to_english.items():
            result = result.replace(ben, eng)
        
        return result

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
        
        # Publish date
        publish_date = ""
        date_elem = soup.find('p', class_='publish-date')
        if date_elem:
            publish_date = self.clean_text(date_elem.get_text())
        
        # Introduction
        introduction = ""
        intro_elem = soup.find('div', class_='act-role-style')
        if intro_elem:
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
        """Parse table structure"""
        
        # Extract caption
        caption = ""
        prev_elem = table_elem.find_previous_sibling()
        while prev_elem and prev_elem.name in ['p', 'strong']:
            text = prev_elem.get_text().strip()
            if 'টেবিল' in text or 'Table' in text:
                caption = text
                break
            prev_elem = prev_elem.find_previous_sibling()
        
        # Get rows
        rows = table_elem.find_all('tr')
        if not rows:
            return None
        
        # Extract headers
        headers = []
        thead = table_elem.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            if len(header_rows) >= 1:
                for cell in header_rows[0].find_all(['th', 'td']):
                    headers.append(self.clean_content_text(cell.get_text()))
        
        # Parse data rows
        data_rows = []
        tbody = table_elem.find('tbody')
        if tbody:
            table_rows = tbody.find_all('tr')
        else:
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
        """Parse subsections, clauses and subclauses from content"""
        
        subsections = []
        direct_clauses = []
        
        # Remove section number from beginning
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        for para in paragraphs:
            # Check for subsection (১), (২), (৩)
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                # Save previous
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
            
            # Check for clause (ক), (খ), (গ)
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
                    sub_clauses=[],
                    tables=[]
                )
            
            # Check for sub-clause (অ), (আ), (ই)
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
            
            # Regular content
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para:
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
        
        # Add the last items
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def extract_footnotes(self, section_div, section_number: str) -> List[Footnote]:
        """Extract footnotes from section"""
        footnotes = []
        
        footnote_spans = section_div.find_all('span', class_='footnote')
        
        for footnote_span in footnote_spans:
            footnote_text = footnote_span.get('title', '')
            
            footnote_number = ""
            link_elem = footnote_span.find('a')
            if link_elem:
                footnote_number = link_elem.get_text().strip()
            else:
                sup_elem = footnote_span.find('sup')
                if sup_elem:
                    footnote_number = sup_elem.get_text().strip()
            
            if footnote_number and footnote_text:
                footnote = Footnote(
                    number=footnote_number,
                    text=footnote_text,
                    position=f"section_{section_number}"
                )
                footnotes.append(footnote)
        
        return footnotes

    def extract_all_sections_with_context(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all sections with their structural context (part/chapter info)"""
        
        print("🔍 Extracting sections with structural context...")
        
        # Find all structural elements in document order
        all_elements = []
        
        # Add parts, chapters, and sections in order they appear
        for elem in soup.find_all(['div']):
            classes = elem.get('class', [])
            
            if 'act-part-group' in classes:
                # Extract part info
                part_no_elem = elem.find('p', class_='act-part-no')
                part_name_elem = elem.find('p', class_='act-part-name')
                
                if part_no_elem and part_name_elem:
                    part_number = self.clean_text(part_no_elem.get_text())
                    part_title = self.clean_text(part_name_elem.get_text())
                    
                    all_elements.append({
                        'type': 'part',
                        'number': part_number,
                        'title': part_title,
                        'element': elem
                    })
            
            elif 'act-chapter-group' in classes:
                # Extract chapter info
                chapter_no_elem = elem.find('p', class_='act-chapter-no')
                chapter_name_elem = elem.find('p', class_='act-chapter-name')
                
                if chapter_no_elem and chapter_name_elem:
                    chapter_number = self.clean_text(chapter_no_elem.get_text())
                    chapter_title = self.clean_text(chapter_name_elem.get_text())
                    
                    all_elements.append({
                        'type': 'chapter',
                        'number': chapter_number,
                        'title': chapter_title,
                        'element': elem
                    })
            
            elif 'row' in classes and ('lineremoves' in classes or 'txt-head' in str(elem) or 'txt-details' in str(elem)):
                # This might be a section
                txt_head = elem.find('div', class_='txt-head')
                txt_details = elem.find('div', class_='txt-details')
                
                if txt_head or txt_details or re.search(r'[০-৯]+।', elem.get_text()):
                    all_elements.append({
                        'type': 'section',
                        'element': elem
                    })
        
        print(f"📊 Found {len(all_elements)} structural elements")
        
        # Now process sections and assign them to current part/chapter context
        sections_with_context = []
        current_part = None
        current_chapter = None
        
        for elem_data in all_elements:
            if elem_data['type'] == 'part':
                current_part = elem_data
                current_chapter = None  # Reset chapter when new part starts
                
            elif elem_data['type'] == 'chapter':
                current_chapter = elem_data
                
            elif elem_data['type'] == 'section':
                section_div = elem_data['element']
                
                # Extract section content
                section = self.extract_section_from_div(section_div)
                if section:
                    sections_with_context.append({
                        'section': section,
                        'part': current_part,
                        'chapter': current_chapter
                    })
        
        print(f"✅ Extracted {len(sections_with_context)} sections with context")
        return sections_with_context

    def extract_section_from_div(self, section_div) -> Optional[Section]:
        """Extract section data from a div element"""
        
        txt_head = section_div.find('div', class_='txt-head')
        txt_details = section_div.find('div', class_='txt-details')
        
        # Extract title and content
        if txt_head and txt_details:
            section_title = self.clean_text(txt_head.get_text())
            
            # Remove tables from content copy for text extraction
            txt_details_copy = txt_details.__copy__()
            for table_elem in txt_details_copy.find_all('table'):
                table_elem.decompose()
                
            section_content = self.clean_content_text(txt_details_copy.get_text())
        else:
            # Alternative structure
            section_title = "Section"
            section_div_copy = section_div.__copy__()
            for table_elem in section_div_copy.find_all('table'):
                table_elem.decompose()
            section_content = self.clean_content_text(section_div_copy.get_text())
        
        # Extract section number
        section_number = ""
        section_matches = re.findall(r'([০-৯]+)(?:\[[^\]]*\])*।', section_content)
        if not section_matches:
            section_matches = re.findall(r'([0-9]+)\[[^\]]*\]', section_content)
            if section_matches:
                section_matches = [self.convert_to_bengali_numerals(match) for match in section_matches]
        if not section_matches:
            section_matches = re.findall(r'([০-৯]+)\[[^\]]*\]', section_content)
        if not section_matches:
            section_matches = re.findall(r'([০-৯]+)', section_content)
        if not section_matches:
            english_matches = re.findall(r'([0-9]+)', section_content)
            if english_matches:
                section_matches = [self.convert_to_bengali_numerals(match) for match in english_matches]
        
        if not section_matches:
            return None
        
        # Take first valid section number
        section_number = None
        for match in section_matches:
            try:
                num_value = int(self.convert_to_english_numerals(match))
                if 1 <= num_value <= 999:
                    section_number = match
                    break
            except:
                continue
        
        if not section_number:
            return None
        
        # Extract tables
        tables = []
        for table_elem in section_div.find_all('table'):
            table = self.parse_table(table_elem, section_title)
            if table:
                tables.append(table)
        
        # Parse subsections and clauses
        subsections, direct_clauses = self.parse_subsections_clauses_subclauses(section_content)
        
        # Extract footnotes
        footnotes = self.extract_footnotes(section_div, section_number)
        
        # Create section
        section = Section(
            number=section_number,
            title=section_title,
            content_text=section_content,
            subsections=subsections,
            clauses=direct_clauses,
            tables=tables,
            footnotes=footnotes
        )
        
        return section

    def build_structured_document(self, sections_with_context: List[Dict], header: DocumentHeader, url: str) -> StructuredLegalDocument:
        """Build properly structured document from sections with context"""
        
        print("🏗️ Building structured document...")
        
        parts = []
        chapters = []
        has_parts = False
        
        # Group sections by part/chapter
        structure_map = {}
        
        for item in sections_with_context:
            section = item['section']
            part_info = item['part']
            chapter_info = item['chapter']
            
            # Create structure key
            if part_info:
                has_parts = True
                part_key = part_info['number']
                chapter_key = chapter_info['number'] if chapter_info else ''
                
                if part_key not in structure_map:
                    structure_map[part_key] = {
                        'part_info': part_info,
                        'chapters': {}
                    }
                
                if chapter_key:
                    if chapter_key not in structure_map[part_key]['chapters']:
                        structure_map[part_key]['chapters'][chapter_key] = {
                            'chapter_info': chapter_info,
                            'sections': []
                        }
                    structure_map[part_key]['chapters'][chapter_key]['sections'].append(section)
                else:
                    # Direct section under part
                    if 'direct_sections' not in structure_map[part_key]:
                        structure_map[part_key]['direct_sections'] = []
                    structure_map[part_key]['direct_sections'].append(section)
            
            elif chapter_info:
                # Chapter without part
                chapter_key = chapter_info['number']
                
                if chapter_key not in structure_map:
                    structure_map[chapter_key] = {
                        'chapter_info': chapter_info,
                        'sections': []
                    }
                structure_map[chapter_key]['sections'].append(section)
        
        # Build parts structure
        if has_parts:
            for part_key in sorted(structure_map.keys()):
                part_data = structure_map[part_key]
                part_info = part_data['part_info']
                
                part_chapters = []
                for chapter_key in sorted(part_data.get('chapters', {}).keys()):
                    chapter_data = part_data['chapters'][chapter_key]
                    chapter_info = chapter_data['chapter_info']
                    
                    # Sort sections by number
                    chapter_sections = sorted(chapter_data['sections'], 
                                           key=lambda x: int(self.convert_to_english_numerals(x.number)))
                    
                    chapter = Chapter(
                        number=chapter_info['number'],
                        title=chapter_info['title'],
                        sections=chapter_sections
                    )
                    part_chapters.append(chapter)
                
                # Get direct sections under part
                direct_sections = part_data.get('direct_sections', [])
                direct_sections = sorted(direct_sections, 
                                       key=lambda x: int(self.convert_to_english_numerals(x.number)))
                
                part = Part(
                    number=part_info['number'],
                    title=part_info['title'],
                    chapters=part_chapters,
                    sections=direct_sections
                )
                parts.append(part)
        
        else:
            # Build chapters structure
            for chapter_key in sorted(structure_map.keys()):
                chapter_data = structure_map[chapter_key]
                chapter_info = chapter_data['chapter_info']
                
                # Sort sections by number
                chapter_sections = sorted(chapter_data['sections'], 
                                        key=lambda x: int(self.convert_to_english_numerals(x.number)))
                
                chapter = Chapter(
                    number=chapter_info['number'],
                    title=chapter_info['title'],
                    sections=chapter_sections
                )
                chapters.append(chapter)
        
        # Create document
        document = StructuredLegalDocument(
            header=header,
            chapters=chapters,
            parts=parts,
            has_parts=has_parts,
            scraped_at=datetime.now().isoformat(),
            url=url
        )
        
        print(f"✅ Document structure built:")
        if has_parts:
            print(f"   📁 Parts: {len(parts)}")
            print(f"   📚 Total Chapters: {sum(len(part.chapters) for part in parts)}")
            print(f"   📋 Total Sections: {sum(len(part.sections) + sum(len(ch.sections) for ch in part.chapters) for part in parts)}")
        else:
            print(f"   📚 Chapters: {len(chapters)}")
            print(f"   📋 Total Sections: {sum(len(ch.sections) for ch in chapters)}")
        
        return document

    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Main scraping method with enhanced structure extraction"""
        
        print(f"🔄 Enhanced Scraping: {url}")
        
        try:
            # Establish session
            try:
                self.session.get(self.base_url, timeout=10)
                print("📡 Session established")
            except:
                pass
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"📄 Content size: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract header
            header = self.extract_document_header(soup)
            
            # Extract sections with their structural context
            sections_with_context = self.extract_all_sections_with_context(soup)
            
            # Build structured document
            document = self.build_structured_document(sections_with_context, header, url)
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

    def save_document(self, document: StructuredLegalDocument, output_dir: str = 'enhanced_structured_laws'):
        """Save document with enhanced structure"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        clean_title = re.sub(r'[^\w\s-]', '', document.header.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}_enhanced.json"
        
        # Convert to dict
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
        
        # Add enhanced summary
        if document.has_parts:
            total_sections = sum(len(part.sections) + sum(len(ch.sections) for ch in part.chapters) for part in document.parts)
            document_dict['enhanced_structure_summary'] = {
                'extraction_method': 'context_aware_enhanced_scraping',
                'has_parts': True,
                'total_parts': len(document.parts),
                'total_chapters': sum(len(part.chapters) for part in document.parts),
                'total_sections': total_sections,
                'structure_validation': 'sections_properly_distributed_by_context',
                'serialization_method': 'continuous_across_all_parts_and_chapters',
                'structure_format': 'অংশ → অধ্যায় → ধারা (context-aware) → subsection → clause → subclause → article → table'
            }
        else:
            total_sections = sum(len(ch.sections) for ch in document.chapters)
            document_dict['enhanced_structure_summary'] = {
                'extraction_method': 'context_aware_enhanced_scraping',
                'has_parts': False,
                'total_chapters': len(document.chapters),
                'total_sections': total_sections,
                'structure_validation': 'sections_properly_distributed_by_context',
                'structure_format': 'অধ্যায় → ধারা (context-aware) → subsection → clause → subclause → article → table'
            }
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Enhanced structure saved to: {filepath}")
        return filepath

def main():
    """Main function for enhanced scraping"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_structured_scraper.py <url>")
        print("Example: python enhanced_structured_scraper.py http://bdlaws.minlaw.gov.bd/act-details-1429.html")
        return
    
    scraper = EnhancedStructuredScraper()
    url = sys.argv[1]
    
    print(f"🎯 ENHANCED STRUCTURED SCRAPER")
    print(f"📋 URL: {url}")
    print("=" * 50)
    
    document = scraper.scrape_document(url)
    if document:
        scraper.save_document(document)
        print(f"\n🎉 Enhanced scraping completed successfully!")
    else:
        print(f"\n💥 Enhanced scraping failed!")

if __name__ == "__main__":
    main()