#!/usr/bin/env python3
"""
Local HTML Act Parser (Income Tax Act 2023 - Bangla)
=====================================================

Parses the locally saved HTML of the Income Tax Act, 2023 (Bangla) and
extracts a complete hierarchical structure while preserving the document's
original ordering and content text as presented on the website.

Hierarchy handled:
- Part (অংশ) → Chapter (অধ্যায়) → Section (ধারা)
- Within Section: Subsection → Clause → Subclause → Article
- Tables can appear at section, subsection, clause, subclause, or article level.

Notes:
- Some Parts have Chapters and some do not. Sections are serialized across the
  whole document, not reset per Part or Chapter.
- This parser associates each Section to the current Part/Chapter context based
  on in-document order, not by numeric ranges.

Usage:
  python local_html_act_parser.py --input data/act/income-tax-act-2023-bangla.html --output enhanced_structured_laws/income_tax_act_2023_local.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag


# ===============================
# Data models
# ===============================


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
    context: str  # The textual context (e.g., surrounding heading)


@dataclass
class Article:
    identifier: str  # অনুচ্ছেদ number or label
    title: str
    text: str
    tables: List[LegalTable]


@dataclass
class SubClause:
    identifier: str  # (অ), (আ), (ই), ...
    text: str
    tables: List[LegalTable]


@dataclass
class Clause:
    identifier: str  # (ক), (খ), (গ), ...
    text: str
    sub_clauses: List[SubClause]
    articles: List[Article]
    tables: List[LegalTable]


@dataclass
class Subsection:
    identifier: str  # (১), (২), (৩), ... in Bangla numerals
    text: str
    clauses: List[Clause]
    articles: List[Article]
    tables: List[LegalTable]


@dataclass
class Footnote:
    number: str
    text: str
    position: str  # e.g., section_১


@dataclass
class Section:
    number: str  # Bengali numerals preferred
    title: str
    content_text: str  # Section body text (excluding table cell text)
    subsections: List[Subsection]
    clauses: List[Clause]  # Direct clauses when no subsections
    articles: List[Article]
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
    sections: List[Section]  # Direct sections under part (no chapter)


@dataclass
class StructuredLegalDocument:
    header: DocumentHeader
    chapters: List[Chapter]
    parts: List[Part]
    has_parts: bool
    scraped_at: str
    source_html_path: str


# ===============================
# Parser implementation
# ===============================


class LocalActParser:
    def __init__(self) -> None:
        pass

    # ---------- Text utilities ----------
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\r\n|\r|\n", " ", text)
        return text.strip()

    def clean_content_text(self, text: str) -> str:
        if not text:
            return ""
        lines = text.split("\n")
        cleaned_lines: List[str] = []
        for line in lines:
            cleaned_line = re.sub(r"\s+", " ", line.strip())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        return "\n".join(cleaned_lines)

    def convert_to_bengali_numerals(self, text: str) -> str:
        if not text:
            return ""
        mapping = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
        for eng, ben in mapping.items():
            text = text.replace(eng, ben)
        return text

    def convert_to_english_numerals(self, text: str) -> str:
        if not text:
            return ""
        mapping = {'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'}
        for ben, eng in mapping.items():
            text = text.replace(ben, eng)
        return text

    # ---------- Header extraction ----------
    def extract_document_header(self, soup: BeautifulSoup) -> DocumentHeader:
        title = ""
        ordinance_info = ""
        publish_date = ""
        introduction_parts: List[str] = []

        title_section = soup.find('section', class_='bg-act-section')
        if title_section:
            h3 = title_section.find('h3')
            if h3:
                title = self.clean_text(h3.get_text())
            h4 = title_section.find('h4')
            if h4:
                ordinance_info = self.clean_text(h4.get_text())

        date_elem = soup.find('p', class_='publish-date')
        if date_elem:
            publish_date = self.clean_text(date_elem.get_text())

        intro_div = soup.find('div', class_='act-role-style')
        if intro_div:
            for p in intro_div.find_all('p'):
                text = self.clean_text(p.get_text())
                if text:
                    introduction_parts.append(text)

        return DocumentHeader(
            title=title,
            ordinance_info=ordinance_info,
            publish_date=publish_date,
            introduction="\n".join(introduction_parts),
        )

    # ---------- Table parsing ----------
    def parse_table(self, table_elem: Tag, context: str) -> Optional[LegalTable]:
        if not isinstance(table_elem, Tag):
            return None

        # Caption from preceding sibling text that looks like a table caption
        caption = ""
        prev = table_elem.find_previous_sibling()
        while prev and isinstance(prev, Tag) and prev.name in ['p', 'strong']:
            text = self.clean_text(prev.get_text())
            if 'টেবিল' in text or 'Table' in text:
                caption = text
                break
            prev = prev.find_previous_sibling()

        headers: List[str] = []
        rows: List[TableRow] = []

        thead = table_elem.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            if header_rows:
                first = header_rows[0]
                for cell in first.find_all(['th', 'td']):
                    headers.append(self.clean_content_text(cell.get_text()))

        # Body rows
        tbody = table_elem.find('tbody')
        if tbody:
            tr_elems = tbody.find_all('tr')
        else:
            tr_elems = table_elem.find_all('tr')
            # Skip first row if it seems header
            if thead is None and tr_elems:
                # Heuristic: if first row is header-like (th present)
                if tr_elems[0].find('th') is not None:
                    tr_elems = tr_elems[1:]

        for tr in tr_elems:
            cells: List[TableCell] = []
            for cell in tr.find_all(['td', 'th']):
                cells.append(
                    TableCell(
                        content=self.clean_content_text(cell.get_text()),
                        colspan=int(cell.get('colspan', 1)),
                        rowspan=int(cell.get('rowspan', 1)),
                        is_header=(cell.name == 'th'),
                    )
                )
            if cells:
                rows.append(TableRow(cells=cells))

        if not rows:
            return None

        return LegalTable(caption=caption, headers=headers, rows=rows, context=context)

    # ---------- Footnotes ----------
    def extract_footnotes(self, container: Tag, section_number: str) -> List[Footnote]:
        footnotes: List[Footnote] = []
        for span in container.find_all('span', class_='footnote'):
            text = span.get('title', '')
            number = ''
            a = span.find('a')
            if a:
                number = self.clean_text(a.get_text())
            else:
                sup = span.find('sup')
                if sup:
                    number = self.clean_text(sup.get_text())
            if number and text:
                footnotes.append(Footnote(number=number, text=text, position=f"section_{section_number}"))
        return footnotes

    # ---------- Hierarchical content parsing within a section ----------
    _re_subsection = re.compile(r"^\(([০-৯]+)\)")
    _re_clause = re.compile(r"^\(([ক-হ])\)")
    _re_subclause = re.compile(r"^\(([অ-ঔ])\)")
    _re_article = re.compile(r"^(অনুচ্ছেদ)\s+([০-৯0-9]+)(?:\s*[:\-\.\)]+\s*)?(.*)$")

    def _append_text(self, base: str, addition: str) -> str:
        if not base:
            return addition
        # Prefer space separator to preserve readability
        return f"{base} {addition}".strip()

    def parse_section_stream(self, section_div: Tag, section_title: str) -> Tuple[str, List[LegalTable], List[Subsection], List[Clause], List[Article]]:
        """Iterate over the section's content in-order, creating hierarchical items.

        Returns:
            content_text: Cleaned text content excluding table cell text
            tables: Tables attached at section level (when not attached deeper)
            subsections: Parsed subsections
            direct_clauses: Clauses not under any subsection
            articles: Articles not under any subsection/clause
        """
        txt_details = section_div.find('div', class_='txt-details')
        if not txt_details:
            # Fallback: use the whole section_div
            txt_details = section_div

        content_lines: List[str] = []
        section_tables: List[LegalTable] = []
        subsections: List[Subsection] = []
        direct_clauses: List[Clause] = []
        loose_articles: List[Article] = []

        current_subsection: Optional[Subsection] = None
        current_clause: Optional[Clause] = None
        current_subclause: Optional[SubClause] = None
        current_article: Optional[Article] = None

        def attach_table(table: LegalTable) -> None:
            # Attach to the most specific currently-open construct
            if current_article is not None:
                current_article.tables.append(table)
            elif current_subclause is not None:
                current_subclause.tables.append(table)
            elif current_clause is not None:
                current_clause.tables.append(table)
            elif current_subsection is not None:
                current_subsection.tables.append(table)
            else:
                section_tables.append(table)

        def finalize_clause_if_open() -> None:
            nonlocal current_clause
            if current_clause is not None:
                if current_subsection is not None:
                    current_subsection.clauses.append(current_clause)
                else:
                    direct_clauses.append(current_clause)
                current_clause = None

        def finalize_subsection_if_open() -> None:
            nonlocal current_subsection
            if current_subsection is not None:
                subsections.append(current_subsection)
                current_subsection = None

        def finalize_article_if_open(target_list: Optional[List[Article]] = None) -> None:
            nonlocal current_article
            if current_article is not None:
                if target_list is not None:
                    target_list.append(current_article)
                else:
                    # Attach to appropriate container
                    if current_clause is not None:
                        current_clause.articles.append(current_article)
                    elif current_subsection is not None:
                        current_subsection.articles.append(current_article)
                    else:
                        loose_articles.append(current_article)
                current_article = None

        # Iterate children in order (paragraphs, tables, etc.)
        for child in txt_details.children:
            if isinstance(child, NavigableString):
                text = self.clean_content_text(str(child))
                if text:
                    content_lines.append(text)
                    # Append to the deepest open node's text
                    if current_article is not None:
                        current_article.text = self._append_text(current_article.text, text)
                    elif current_subclause is not None:
                        current_subclause.text = self._append_text(current_subclause.text, text)
                    elif current_clause is not None:
                        current_clause.text = self._append_text(current_clause.text, text)
                    elif current_subsection is not None:
                        current_subsection.text = self._append_text(current_subsection.text, text)
                continue

            if not isinstance(child, Tag):
                continue

            # Handle tables in-place
            if child.name == 'table':
                table = self.parse_table(child, section_title)
                if table:
                    attach_table(table)
                # Do not include table text in content_lines to avoid duplication
                continue

            # For div/p/ul/li etc., extract meaningful text blocks
            if child.name in ['p', 'div', 'li']:
                # Parse any nested tables first and attach them
                try:
                    nested_tables = child.find_all('table')
                except Exception:
                    nested_tables = []
                for tbl in nested_tables:
                    table_obj = self.parse_table(tbl, section_title)
                    if table_obj:
                        attach_table(table_obj)

                # Prepare text without table content to avoid duplication
                try:
                    child_soup = BeautifulSoup(str(child), 'html.parser')
                    for t in child_soup.find_all('table'):
                        t.decompose()
                    raw_text = self.clean_content_text(child_soup.get_text("\n"))
                except Exception:
                    raw_text = self.clean_content_text(child.get_text("\n"))
                if not raw_text:
                    continue

                # Detect markers
                # Normalize by removing leading section number like "১। " if present so that (১) is detectable
                normalized_for_match = re.sub(r'^\s*[০-৯]+(?:\[[^\]]*\])?।\s*', '', raw_text)

                sub_match = self._re_subsection.match(normalized_for_match)
                clause_match = self._re_clause.match(normalized_for_match)
                subclause_match = self._re_subclause.match(normalized_for_match)
                article_match = self._re_article.match(normalized_for_match)

                if article_match:
                    # Starting a new Article closes the previous one
                    finalize_article_if_open()
                    # Start new article
                    art_id = self.convert_to_bengali_numerals(article_match.group(2))
                    art_title = self.clean_text(article_match.group(3) or "")
                    remaining_text = self.clean_text(normalized_for_match[article_match.end():])
                    current_article = Article(identifier=art_id, title=art_title, text=remaining_text, tables=[])
                    content_lines.append(raw_text)
                    continue

                if sub_match:
                    # New subsection: finalize deeper items
                    finalize_article_if_open()
                    finalize_clause_if_open()
                    finalize_subsection_if_open()

                    sub_id = sub_match.group(1)
                    sub_text = self.clean_text(normalized_for_match[sub_match.end():])
                    current_subsection = Subsection(identifier=sub_id, text=sub_text, clauses=[], articles=[], tables=[])
                    content_lines.append(raw_text)
                    # Reset deeper levels
                    current_clause = None
                    current_subclause = None
                    continue

                if clause_match:
                    finalize_article_if_open()
                    finalize_clause_if_open()
                    clause_id = clause_match.group(1)
                    clause_text = self.clean_text(normalized_for_match[clause_match.end():])
                    current_clause = Clause(identifier=clause_id, text=clause_text, sub_clauses=[], articles=[], tables=[])
                    content_lines.append(raw_text)
                    current_subclause = None
                    continue

                if subclause_match:
                    finalize_article_if_open()
                    subc_id = subclause_match.group(1)
                    subc_text = self.clean_text(normalized_for_match[subclause_match.end():])
                    current_subclause = SubClause(identifier=subc_id, text=subc_text, tables=[])
                    # Attach new subclause to current clause if any; if no clause, create a synthetic one
                    if current_clause is None:
                        current_clause = Clause(identifier="", text="", sub_clauses=[], articles=[], tables=[])
                        if current_subsection is not None:
                            current_subsection.clauses.append(current_clause)
                        else:
                            direct_clauses.append(current_clause)
                    current_clause.sub_clauses.append(current_subclause)
                    content_lines.append(raw_text)
                    continue

                # Regular paragraph: append to deepest open node
                content_lines.append(raw_text)
                if current_article is not None:
                    current_article.text = self._append_text(current_article.text, normalized_for_match)
                elif current_subclause is not None:
                    current_subclause.text = self._append_text(current_subclause.text, normalized_for_match)
                elif current_clause is not None:
                    current_clause.text = self._append_text(current_clause.text, normalized_for_match)
                elif current_subsection is not None:
                    current_subsection.text = self._append_text(current_subsection.text, normalized_for_match)
                continue

            # Any other tag: extract and append cleaned text
            text = self.clean_content_text(child.get_text("\n"))
            if text:
                content_lines.append(text)
                if current_article is not None:
                    current_article.text = self._append_text(current_article.text, text)
                elif current_subclause is not None:
                    current_subclause.text = self._append_text(current_subclause.text, text)
                elif current_clause is not None:
                    current_clause.text = self._append_text(current_clause.text, text)
                elif current_subsection is not None:
                    current_subsection.text = self._append_text(current_subsection.text, text)

        # Finalize any open constructs
        finalize_article_if_open()
        finalize_clause_if_open()
        finalize_subsection_if_open()

        content_text = self.clean_content_text("\n".join(content_lines))
        return content_text, section_tables, subsections, direct_clauses, loose_articles

    # ---------- Section extraction ----------
    def extract_section_from_div(self, section_div: Tag) -> Optional[Section]:
        txt_head = section_div.find('div', class_='txt-head')
        section_title = self.clean_text(txt_head.get_text()) if txt_head else "Section"

        # Build hierarchical content from stream
        content_text, section_tables, subsections, direct_clauses, loose_articles = self.parse_section_stream(section_div, section_title)

        # Determine section number from content_text
        section_number: Optional[str] = None
        # Heuristic: try first paragraph to catch leading "১।"
        try:
            txt_details_fp = section_div.find('div', class_='txt-details') or section_div
            first_p = txt_details_fp.find('p') if txt_details_fp else None
            if first_p:
                fp_text = self.clean_content_text(first_p.get_text())
                m_bn = re.match(r'^\s*([০-৯]+)\s*।', fp_text)
                if m_bn:
                    section_number = m_bn.group(1)
                else:
                    m_en = re.match(r'^\s*([0-9]+)\s*[\.|)]', fp_text)
                    if m_en:
                        section_number = self.convert_to_bengali_numerals(m_en.group(1))
        except Exception:
            pass
        candidates: List[str] = []
        # Bengali number followed by danda (।), possibly with footnotes in brackets
        candidates += re.findall(r'([০-৯]+)(?:\[[^\]]*\])*।', content_text)
        if not candidates:
            # English number with footnotes; convert to Bengali after
            eng = re.findall(r'([0-9]+)\[[^\]]*\]', content_text)
            candidates += [self.convert_to_bengali_numerals(x) for x in eng]
        if not candidates:
            candidates += re.findall(r'([০-৯]+)\[[^\]]*\]', content_text)
        if not candidates:
            candidates += re.findall(r'([০-৯]+)', content_text)
        if not candidates:
            eng2 = re.findall(r'([0-9]+)', content_text)
            candidates += [self.convert_to_bengali_numerals(x) for x in eng2]

        if not section_number:
            for cand in candidates:
                try:
                    val = int(self.convert_to_english_numerals(cand))
                    if 1 <= val <= 999:
                        section_number = cand
                        break
                except Exception:
                    continue

        # Final fallback: detect classic Section 1 phrasing
        if not section_number:
            # Typical first section wording present in Bangla acts
            if re.search(r'এই আইন.*অভিহিত হইবে', content_text):
                section_number = '১'

        if not section_number:
            return None

        # Footnotes
        footnotes = self.extract_footnotes(section_div, section_number)

        return Section(
            number=section_number,
            title=section_title,
            content_text=content_text,
            subsections=subsections,
            clauses=direct_clauses,
            articles=loose_articles,
            tables=section_tables,
            footnotes=footnotes,
        )

    # ---------- Document structure assembly ----------
    def extract_all_sections_with_context(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Scan the document in order, track current Part/Chapter, and collect sections with context."""
        all_elements: List[Dict[str, Any]] = []
        for elem in soup.find_all('div'):
            classes = elem.get('class', [])
            class_str = ' '.join(classes)

            if 'act-part-group' in classes:
                part_no = elem.find('p', class_='act-part-no')
                part_name = elem.find('p', class_='act-part-name')
                if part_no and part_name:
                    all_elements.append({
                        'type': 'part',
                        'number': self.clean_text(part_no.get_text()),
                        'title': self.clean_text(part_name.get_text()),
                        'element': elem,
                    })

            elif 'act-chapter-group' in classes:
                chap_no = elem.find('p', class_='act-chapter-no')
                chap_name = elem.find('p', class_='act-chapter-name')
                if chap_no and chap_name:
                    all_elements.append({
                        'type': 'chapter',
                        'number': self.clean_text(chap_no.get_text()),
                        'title': self.clean_text(chap_name.get_text()),
                        'element': elem,
                    })

            # Section wrapper rows can be marked as 'row lineremoves' or similar
            elif 'row' in classes and ('lineremoves' in classes or 'txt-head' in class_str or 'txt-details' in class_str):
                txt_head = elem.find('div', class_='txt-head')
                txt_details = elem.find('div', class_='txt-details')
                # Heuristic: treat as section if has head or details or contains a Bengali section number pattern
                if txt_head or txt_details or re.search(r'[০-৯]+।', elem.get_text()):
                    all_elements.append({'type': 'section', 'element': elem})

        sections_with_context: List[Dict[str, Any]] = []
        current_part: Optional[Dict[str, Any]] = None
        current_chapter: Optional[Dict[str, Any]] = None

        for item in all_elements:
            if item['type'] == 'part':
                current_part = item
                current_chapter = None
            elif item['type'] == 'chapter':
                current_chapter = item
            elif item['type'] == 'section':
                section_div = item['element']
                # If a Part/Chapter header is embedded within this section div (common in first section of a Part),
                # capture and set them BEFORE extracting/recording the section to avoid losing the first section.
                embedded_part = section_div.find('div', class_='act-part-group')
                if embedded_part:
                    part_no_elem = embedded_part.find('p', class_='act-part-no')
                    part_name_elem = embedded_part.find('p', class_='act-part-name')
                    if part_no_elem and part_name_elem:
                        current_part = {
                            'type': 'part',
                            'number': self.clean_text(part_no_elem.get_text()),
                            'title': self.clean_text(part_name_elem.get_text()),
                            'element': embedded_part,
                        }
                        # New part implies chapter context resets
                        current_chapter = None

                embedded_chapter = section_div.find('div', class_='act-chapter-group')
                if embedded_chapter:
                    chap_no_elem = embedded_chapter.find('p', class_='act-chapter-no')
                    chap_name_elem = embedded_chapter.find('p', class_='act-chapter-name')
                    if chap_no_elem and chap_name_elem:
                        current_chapter = {
                            'type': 'chapter',
                            'number': self.clean_text(chap_no_elem.get_text()),
                            'title': self.clean_text(chap_name_elem.get_text()),
                            'element': embedded_chapter,
                        }
                section = self.extract_section_from_div(section_div)
                if section is not None:
                    sections_with_context.append({'section': section, 'part': current_part, 'chapter': current_chapter})

        return sections_with_context

    def build_structured_document(self, sections_with_context: List[Dict[str, Any]], header: DocumentHeader, source_path: str) -> StructuredLegalDocument:
        has_parts = any(item['part'] is not None for item in sections_with_context)

        parts: List[Part] = []
        chapters_top: List[Chapter] = []

        if has_parts:
            # Map: part_number -> { part_info, chapters: {chapter_number: [sections]}, direct_sections: [] }
            pmap: Dict[str, Dict[str, Any]] = {}
            for item in sections_with_context:
                part = item['part']
                chapter = item['chapter']
                section: Section = item['section']
                if part is None:
                    # Ignore stray sections before first part
                    continue
                pkey = part['number']
                if pkey not in pmap:
                    pmap[pkey] = {'info': part, 'chapters': {}, 'direct_sections': []}
                if chapter is not None:
                    ckey = chapter['number']
                    pmap[pkey]['chapters'].setdefault(ckey, {'info': chapter, 'sections': []})
                    pmap[pkey]['chapters'][ckey]['sections'].append(section)
                else:
                    pmap[pkey]['direct_sections'].append(section)

            # Build dataclasses preserving natural (string) order; attempt numeric sort on section.number
            def sort_sections(sections: List[Section]) -> List[Section]:
                try:
                    return sorted(sections, key=lambda s: int(self.convert_to_english_numerals(s.number)))
                except Exception:
                    return sections

            for pkey in pmap.keys():
                pinfo = pmap[pkey]['info']
                part_chapters: List[Chapter] = []
                for ckey in pmap[pkey]['chapters'].keys():
                    cinfo = pmap[pkey]['chapters'][ckey]['info']
                    csections = sort_sections(pmap[pkey]['chapters'][ckey]['sections'])
                    part_chapters.append(Chapter(number=cinfo['number'], title=cinfo['title'], sections=csections))
                direct_sections = sort_sections(pmap[pkey]['direct_sections'])
                parts.append(Part(number=pinfo['number'], title=pinfo['title'], chapters=part_chapters, sections=direct_sections))

        else:
            # Chapters only
            cmap: Dict[str, Dict[str, Any]] = {}
            for item in sections_with_context:
                chapter = item['chapter']
                section: Section = item['section']
                if chapter is None:
                    # If the document truly lacks chapters, aggregate all under a synthetic chapter
                    cmap.setdefault('Chapter 1', {'info': {'number': 'Chapter 1', 'title': header.title}, 'sections': []})
                    cmap['Chapter 1']['sections'].append(section)
                else:
                    ckey = chapter['number']
                    cmap.setdefault(ckey, {'info': chapter, 'sections': []})
                    cmap[ckey]['sections'].append(section)

            def sort_sections(sections: List[Section]) -> List[Section]:
                try:
                    return sorted(sections, key=lambda s: int(self.convert_to_english_numerals(s.number)))
                except Exception:
                    return sections

            for ckey in cmap.keys():
                cinfo = cmap[ckey]['info']
                csections = sort_sections(cmap[ckey]['sections'])
                chapters_top.append(Chapter(number=cinfo['number'], title=cinfo['title'], sections=csections))

        return StructuredLegalDocument(
            header=header,
            chapters=chapters_top,
            parts=parts,
            has_parts=has_parts,
            scraped_at=datetime.now().isoformat(),
            source_html_path=source_path,
        )

    # ---------- Public API ----------
    def parse_file(self, html_path: str) -> StructuredLegalDocument:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        header = self.extract_document_header(soup)
        sections_with_context = self.extract_all_sections_with_context(soup)
        document = self.build_structured_document(sections_with_context, header, html_path)
        return document

    def save_document(self, document: StructuredLegalDocument, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        # Convert dataclasses recursively
        def conv(obj: Any) -> Any:
            if hasattr(obj, '__dataclass_fields__'):
                return {k: conv(v) for k, v in asdict(obj).items()}
            if isinstance(obj, list):
                return [conv(x) for x in obj]
            if isinstance(obj, dict):
                return {k: conv(v) for k, v in obj.items()}
            return obj

        data = conv(document)

        # Summary
        if document.has_parts:
            total_parts = len(document.parts)
            total_chapters = sum(len(p.chapters) for p in document.parts)
            total_sections = sum(len(p.sections) + sum(len(ch.sections) for ch in p.chapters) for p in document.parts)
        else:
            total_parts = 0
            total_chapters = len(document.chapters)
            total_sections = sum(len(ch.sections) for ch in document.chapters)

        data['structure_summary'] = {
            'has_parts': document.has_parts,
            'total_parts': total_parts,
            'total_chapters': total_chapters,
            'total_sections': total_sections,
            'format': 'অংশ → অধ্যায় → ধারা → subsection → clause → subclause → article → table',
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description='Parse local Income Tax Act 2023 Bangla HTML into structured JSON')
    parser.add_argument('--input', required=True, help='Path to the local HTML file')
    parser.add_argument('--output', required=False, help='Path to output JSON file')
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input HTML not found: {input_path}")

    parser_engine = LocalActParser()
    document = parser_engine.parse_file(input_path)

    if args.output:
        output_path = args.output
    else:
        # Derive an output path from the header title
        title_clean = re.sub(r'[^\w\s-]', '', document.header.title).strip()
        title_clean = re.sub(r'[-\s]+', '_', title_clean) or 'income_tax_act_2023'
        output_dir = 'enhanced_structured_laws'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{title_clean}_local.json")

    saved = parser_engine.save_document(document, output_path)
    print(f"Saved structured document to: {saved}")


if __name__ == '__main__':
    main()
