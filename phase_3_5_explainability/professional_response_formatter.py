#!/usr/bin/env python3
"""
Professional Explanation Generator - Phase 3.5.3 Implementation
==============================================================
Formats legal responses like professional tax advisor with Bengali legal standards.
Provides expert-level legal writing, proper citation, safety warnings, and
structured professional communication for Bangladesh tax law queries.

Integrates with Legal Reasoning Engine and Confidence Scoring for
comprehensive professional-grade legal advice formatting.

Author: Phase 3.5 Implementation  
Date: August 10, 2025
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResponseFormat(Enum):
    """Response format types"""
    COMPREHENSIVE = "comprehensive"        # Full professional analysis
    SUMMARY = "summary"                   # Brief professional summary  
    FAQ_STYLE = "faq_style"              # Question-answer format
    LEGAL_MEMO = "legal_memo"            # Formal legal memorandum

class ConfidenceDisplayLevel(Enum):
    """How to display confidence information"""
    DETAILED = "detailed"                # Full confidence breakdown
    STANDARD = "standard"                # Confidence level only
    MINIMAL = "minimal"                  # Basic reliability indicator
    HIDDEN = "hidden"                    # No confidence display

@dataclass
class FormattingPreferences:
    """User preferences for response formatting"""
    language: str = "bengali"            # bengali, english, bilingual
    format_type: ResponseFormat = ResponseFormat.COMPREHENSIVE
    confidence_display: ConfidenceDisplayLevel = ConfidenceDisplayLevel.STANDARD
    include_citations: bool = True
    include_alternatives: bool = True
    include_safety_warnings: bool = True
    technical_level: str = "professional"  # basic, intermediate, professional
    
class ProfessionalResponseFormatter:
    """
    Professional explanation generator for Bangladesh tax law responses.
    
    Features:
    - Expert-level Bengali legal writing standards
    - Proper legal document citation with access links
    - Professional structure and terminology
    - Safety warnings and expert referral recommendations
    - Cultural and linguistic appropriateness for Bangladesh context
    """
    
    def __init__(self):
        """Initialize Professional Response Formatter"""
        
        # Bengali legal terminology
        self.legal_terms = {
            'law': 'আইন',
            'act': 'আইন',
            'section': 'ধারা',
            'schedule': 'তফসিল',
            'rule': 'বিধি',
            'circular': 'সার্কুলার',
            'ordinance': 'অধ্যাদেশ',
            'tax': 'কর',
            'income': 'আয়',
            'return': 'রিটার্ন',
            'filing': 'দাখিল',
            'obligation': 'বাধ্যবাধকতা',
            'exemption': 'অব্যাহতি',
            'deduction': 'কর্তন',
            'assessment': 'নিরূপণ',
            'penalty': 'জরিমানা',
            'appeal': 'আপিল',
            'authority': 'কর্তৃপক্ষ'
        }
        
        # Professional structure templates
        self.response_templates = {
            'comprehensive': {
                'bengali': {
                    'header': 'আইনি বিশ্লেষণ:',
                    'question_intro': 'প্রশ্ন:',
                    'legal_basis_header': 'আইনি ভিত্তি:',
                    'analysis_header': 'বিশ্লেষণ:',
                    'conclusion_header': 'সিদ্ধান্ত:',
                    'confidence_header': 'নির্ভরযোগ্যতা:',
                    'recommendation_header': 'সুপারিশ:',
                    'alternatives_header': 'বিকল্প ব্যাখ্যা:',
                    'warnings_header': 'সতর্কতা:'
                },
                'english': {
                    'header': 'Legal Analysis:',
                    'question_intro': 'Query:',
                    'legal_basis_header': 'Legal Basis:',
                    'analysis_header': 'Analysis:',
                    'conclusion_header': 'Conclusion:',
                    'confidence_header': 'Reliability:',
                    'recommendation_header': 'Recommendation:',
                    'alternatives_header': 'Alternative Interpretations:',
                    'warnings_header': 'Warnings:'
                }
            }
        }
        
        # Confidence level descriptions
        self.confidence_descriptions = {
            'bengali': {
                'professional_grade': 'পেশাদার মানের (৯৫%+ আস্থা) - নিরাপদে ব্যবহারযোগ্য',
                'good_advice': 'ভাল পরামর্শ (৮৫-৯৪% আস্থা) - গুরুত্বপূর্ণ ক্ষেত্রে বিশেষজ্ঞ পর্যালোচনা প্রয়োজন',
                'reasonable_guidance': 'যুক্তিসঙ্গত নির্দেশনা (৭০-৮৪% আস্থা) - বিশেষজ্ঞ পরামর্শ প্রস্তাবিত',
                'low_confidence': 'কম আস্থা (৭০% এর নিচে) - বিশেষজ্ঞ সহায়তা প্রয়োজন'
            },
            'english': {
                'professional_grade': 'Professional Grade (95%+ confidence) - Safe for direct use',
                'good_advice': 'Good Advice (85-94% confidence) - Expert review for critical cases',
                'reasonable_guidance': 'Reasonable Guidance (70-84% confidence) - Expert consultation recommended',
                'low_confidence': 'Low Confidence (<70%) - Expert assistance required'
            }
        }
        
        logger.info("Professional Response Formatter initialized")
    
    def format_professional_response(
        self,
        query: str,
        legal_answer: str,
        reasoning_trace: Dict[str, Any],
        confidence_score: Dict[str, Any],
        matched_sections: List[Dict[str, Any]],
        preferences: FormattingPreferences = None
    ) -> str:
        """
        Format a complete professional legal response
        
        Args:
            query: User's legal query
            legal_answer: System's legal answer
            reasoning_trace: Legal reasoning trace
            confidence_score: Confidence scoring results
            matched_sections: Legal sections that were matched
            preferences: Formatting preferences
            
        Returns:
            Professionally formatted legal response
        """
        if preferences is None:
            preferences = FormattingPreferences()
        
        logger.info(f"Formatting professional response in {preferences.language}")
        
        # Select template based on language and format
        templates = self.response_templates['comprehensive'][preferences.language]
        
        # Build professional response
        response_parts = []
        
        # Header
        response_parts.append(f"{templates['header']}\n")
        
        # Query restatement
        response_parts.append(f"{templates['question_intro']} {query}\n")
        
        # Legal basis section
        legal_basis = self._format_legal_basis(matched_sections, preferences.language)
        if legal_basis:
            response_parts.append(f"\n{templates['legal_basis_header']}")
            response_parts.append(legal_basis)
        
        # Analysis section
        analysis = self._format_analysis_section(
            reasoning_trace, matched_sections, preferences.language
        )
        if analysis:
            response_parts.append(f"\n{templates['analysis_header']}")
            response_parts.append(analysis)
        
        # Conclusion section
        conclusion = self._format_conclusion_section(legal_answer, preferences.language)
        response_parts.append(f"\n{templates['conclusion_header']}")
        response_parts.append(conclusion)
        
        # Confidence section
        if preferences.confidence_display != ConfidenceDisplayLevel.HIDDEN:
            confidence_section = self._format_confidence_section(
                confidence_score, preferences
            )
            if confidence_section:
                response_parts.append(f"\n{templates['confidence_header']}")
                response_parts.append(confidence_section)
        
        # Alternative interpretations
        if preferences.include_alternatives and reasoning_trace.get('alternative_interpretations'):
            alternatives = self._format_alternatives_section(
                reasoning_trace['alternative_interpretations'], preferences.language
            )
            response_parts.append(f"\n{templates['alternatives_header']}")
            response_parts.append(alternatives)
        
        # Safety warnings
        if preferences.include_safety_warnings:
            warnings = self._format_safety_warnings(
                confidence_score.get('safety_warnings', []),
                reasoning_trace.get('safety_warnings', []),
                preferences.language
            )
            if warnings:
                response_parts.append(f"\n{templates['warnings_header']}")
                response_parts.append(warnings)
        
        # Expert recommendation
        recommendation = self._format_expert_recommendation(
            confidence_score, reasoning_trace, preferences.language
        )
        if recommendation:
            response_parts.append(f"\n{templates['recommendation_header']}")
            response_parts.append(recommendation)
        
        # Citations section
        if preferences.include_citations:
            citations = self._format_citations_section(matched_sections, preferences.language)
            if citations:
                response_parts.append(f"\n{self._get_citations_header(preferences.language)}")
                response_parts.append(citations)
        
        return "\n".join(response_parts)
    
    def _format_legal_basis(self, matched_sections: List[Dict[str, Any]], language: str) -> str:
        """Format the legal basis section with proper citations"""
        if not matched_sections:
            return ""
        
        legal_basis_items = []
        
        for i, section in enumerate(matched_sections[:3], 1):  # Top 3 sections
            section_id = section.get('section_id', 'Unknown')
            title = section.get('title', '')
            document_type = section.get('document_type', '')
            
            # Format section reference
            if language == 'bengali':
                if 'section' in section_id.lower():
                    section_ref = section_id.replace('Section', 'ধারা').replace('S', 'ধারা ')
                else:
                    section_ref = section_id
                
                basis_text = f"{i}. {section_ref}"
                if title:
                    basis_text += f": {title}"
                
                # Add document context
                if 'income_tax_act' in document_type:
                    basis_text += " (আয়কর আইন ২০২৩)"
                elif 'finance_ordinance' in document_type:
                    basis_text += " (অর্থ অধ্যাদেশ ২০২৫)"
                elif 'schedule' in document_type:
                    basis_text += " (তফসিল)"
            else:
                basis_text = f"{i}. {section_id}"
                if title:
                    basis_text += f": {title}"
                
                if 'income_tax_act' in document_type:
                    basis_text += " (Income Tax Act 2023)"
                elif 'finance_ordinance' in document_type:
                    basis_text += " (Finance Ordinance 2025)"
                elif 'schedule' in document_type:
                    basis_text += " (Schedule)"
            
            legal_basis_items.append(basis_text)
        
        return "\n".join(legal_basis_items)
    
    def _format_analysis_section(
        self,
        reasoning_trace: Dict[str, Any],
        matched_sections: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Format the legal analysis section"""
        analysis_parts = []
        
        reasoning_steps = reasoning_trace.get('reasoning_steps', [])
        
        if language == 'bengali':
            # Step-by-step analysis in Bengali
            for i, step in enumerate(reasoning_steps[:4], 1):  # Top 4 steps
                step_type = step.get('step_type', '')
                action = step.get('action', '')
                evidence = step.get('evidence', [])
                
                if step_type == 'query_analysis':
                    analysis_parts.append(f"{i}. প্রশ্ন বিশ্লেষণ: {action}")
                elif step_type == 'section_mapping':
                    analysis_parts.append(f"{i}. ধারা সনাক্তকরণ: {action}")
                elif step_type == 'precedence_application':
                    analysis_parts.append(f"{i}. আইনি অগ্রাধিকার প্রয়োগ: {action}")
                elif step_type == 'temporal_validation':
                    analysis_parts.append(f"{i}. সময়কাল যাচাই: {action}")
                
                # Add evidence if available
                if evidence and len(evidence) > 0:
                    analysis_parts.append(f"   প্রমাণ: {evidence[0]}")
        else:
            # Step-by-step analysis in English
            for i, step in enumerate(reasoning_steps[:4], 1):
                step_type = step.get('step_type', '')
                action = step.get('action', '')
                evidence = step.get('evidence', [])
                
                analysis_parts.append(f"{i}. {step_type.replace('_', ' ').title()}: {action}")
                
                if evidence and len(evidence) > 0:
                    analysis_parts.append(f"   Evidence: {evidence[0]}")
        
        return "\n".join(analysis_parts) if analysis_parts else ""
    
    def _format_conclusion_section(self, legal_answer: str, language: str) -> str:
        """Format the conclusion section with proper legal language"""
        
        if language == 'bengali':
            # Ensure professional Bengali legal terminology
            formatted_answer = legal_answer
            
            # Replace common terms with formal equivalents
            replacements = {
                'হ্যাঁ': 'হ্যাঁ, নিয়মানুযায়ী',
                'না': 'না, আইনি বিধান অনুযায়ী',
                'লাগবে': 'প্রয়োজন হবে',
                'দিতে হবে': 'দাখিল করতে হবে'
            }
            
            for original, formal in replacements.items():
                formatted_answer = formatted_answer.replace(original, formal)
        else:
            formatted_answer = legal_answer
        
        return formatted_answer
    
    def _format_confidence_section(
        self,
        confidence_score: Dict[str, Any],
        preferences: FormattingPreferences
    ) -> str:
        """Format confidence information based on display level"""
        
        overall_confidence = confidence_score.get('overall_confidence', 0.0)
        confidence_level = confidence_score.get('confidence_level', 'low_confidence')
        
        language = preferences.language
        display_level = preferences.confidence_display
        
        confidence_descriptions = self.confidence_descriptions[language]
        
        if display_level == ConfidenceDisplayLevel.MINIMAL:
            # Just confidence percentage
            if language == 'bengali':
                return f"{overall_confidence:.0%} আস্থা"
            else:
                return f"{overall_confidence:.0%} confidence"
        
        elif display_level == ConfidenceDisplayLevel.STANDARD:
            # Confidence with category description
            description = confidence_descriptions.get(confidence_level, '')
            return f"{overall_confidence:.0%} - {description}"
        
        elif display_level == ConfidenceDisplayLevel.DETAILED:
            # Detailed confidence breakdown
            factors = confidence_score.get('factors', {})
            
            if language == 'bengali':
                details = [f"সামগ্রিক: {overall_confidence:.0%} - {confidence_descriptions.get(confidence_level, '')}"]
                details.append("বিস্তারিত:")
                
                factor_names = {
                    'section_match_confidence': 'ধারা মিল',
                    'precedence_clarity': 'আইনি অগ্রাধিকার',
                    'temporal_accuracy': 'সময়কাল নির্ভুলতা',
                    'completeness_score': 'সম্পূর্ণতা',
                    'consistency_score': 'সুসংগতি'
                }
                
                for factor, value in factors.items():
                    if factor in factor_names and value > 0:
                        details.append(f"• {factor_names[factor]}: {value:.0%}")
            else:
                details = [f"Overall: {overall_confidence:.0%} - {confidence_descriptions.get(confidence_level, '')}"]
                details.append("Breakdown:")
                
                for factor, value in factors.items():
                    if value > 0:
                        factor_name = factor.replace('_', ' ').title()
                        details.append(f"• {factor_name}: {value:.0%}")
            
            return "\n".join(details)
        
        return ""
    
    def _format_alternatives_section(self, alternatives: List[str], language: str) -> str:
        """Format alternative interpretations section"""
        if not alternatives:
            return ""
        
        formatted_alternatives = []
        for i, alt in enumerate(alternatives, 1):
            formatted_alternatives.append(f"{i}. {alt}")
        
        return "\n".join(formatted_alternatives)
    
    def _format_safety_warnings(
        self,
        confidence_warnings: List[str],
        reasoning_warnings: List[str],
        language: str
    ) -> str:
        """Format safety warnings section"""
        all_warnings = confidence_warnings + reasoning_warnings
        
        if not all_warnings:
            return ""
        
        # Remove duplicates while preserving order
        unique_warnings = []
        for warning in all_warnings:
            if warning not in unique_warnings:
                unique_warnings.append(warning)
        
        return "\n".join(f"• {warning}" for warning in unique_warnings)
    
    def _format_expert_recommendation(
        self,
        confidence_score: Dict[str, Any],
        reasoning_trace: Dict[str, Any],
        language: str
    ) -> str:
        """Format expert recommendation section"""
        
        expert_review_recommended = confidence_score.get('expert_review_recommended', False)
        overall_confidence = confidence_score.get('overall_confidence', 0.0)
        safety_triggers = confidence_score.get('safety_triggers', [])
        
        if not expert_review_recommended and overall_confidence >= 0.95:
            return ""  # No recommendation needed for high-confidence cases
        
        if language == 'bengali':
            if 'criminal_implications' in safety_triggers:
                return "🚨 অবিলম্বে একজন পেশাদার ট্যাক্স আইনজীবীর পরামর্শ নিন। ফৌজদারি কর বিষয়ক জটিলতা রয়েছে।"
            
            elif overall_confidence < 0.70:
                return "⚠️ কম আস্থার কারণে বিশেষজ্ঞ সহায়তা প্রয়োজন। অভিজ্ঞ ট্যাক্স পরামর্শদাতার সাথে যোগাযোগ করুন।"
            
            elif 'high_stakes_topic' in safety_triggers:
                return "🔍 গুরুত্বপূর্ণ কর বিষয়ক সমস্যা। চূড়ান্ত সিদ্ধান্তের আগে পেশাদার ট্যাক্স পরামর্শদাতার মতামত নিন।"
            
            else:
                return "💡 জটিল পরিস্থিতির জন্য একজন অভিজ্ঞ ট্যাক্স পরামর্শদাতার সাথে পরামর্শ করার পরামর্শ দেওয়া হচ্ছে।"
        
        else:
            if 'criminal_implications' in safety_triggers:
                return "🚨 Seek immediate professional legal counsel. Criminal tax implications detected."
            
            elif overall_confidence < 0.70:
                return "⚠️ Low confidence requires expert assistance. Contact an experienced tax advisor."
            
            elif 'high_stakes_topic' in safety_triggers:
                return "🔍 High-stakes tax matter. Consult professional tax advisor before final decisions."
            
            else:
                return "💡 Consider consulting with an experienced tax advisor for complex situations."
    
    def _format_citations_section(self, matched_sections: List[Dict[str, Any]], language: str) -> str:
        """Format legal citations with document links"""
        if not matched_sections:
            return ""
        
        citations = []
        
        for section in matched_sections[:5]:  # Top 5 citations
            section_id = section.get('section_id', '')
            title = section.get('title', '')
            document_type = section.get('document_type', '')
            relevance = section.get('relevance_score', 0.0)
            
            # Create citation text
            if language == 'bengali':
                citation = f"• {section_id}"
                if title:
                    citation += f": {title}"
                citation += f" (প্রাসঙ্গিকতা: {relevance:.0%})"
            else:
                citation = f"• {section_id}"
                if title:
                    citation += f": {title}"
                citation += f" (Relevance: {relevance:.0%})"
            
            # Add document reference
            if 'income_tax_act' in document_type:
                citation += " [Income Tax Act 2023]"
            elif 'finance_ordinance' in document_type:
                citation += " [Finance Ordinance 2025]"
            elif 'schedule' in document_type:
                citation += " [Schedule]"
            elif 'rules' in document_type:
                citation += " [Rules]"
            
            citations.append(citation)
        
        return "\n".join(citations)
    
    def _get_citations_header(self, language: str) -> str:
        """Get appropriate citations header"""
        return "আইনি রেফারেন্স:" if language == 'bengali' else "Legal References:"
    
    def format_summary_response(
        self,
        query: str,
        legal_answer: str,
        confidence_score: Dict[str, Any],
        language: str = "bengali"
    ) -> str:
        """Format a brief summary response for quick answers"""
        
        overall_confidence = confidence_score.get('overall_confidence', 0.0)
        expert_review = confidence_score.get('expert_review_recommended', False)
        
        if language == 'bengali':
            summary = f"প্রশ্ন: {query}\n\n"
            summary += f"উত্তর: {legal_answer}\n\n"
            summary += f"নির্ভরযোগ্যতা: {overall_confidence:.0%}"
            
            if expert_review:
                summary += "\n⚠️ বিশেষজ্ঞ পর্যালোচনা প্রয়োজন"
        else:
            summary = f"Query: {query}\n\n"
            summary += f"Answer: {legal_answer}\n\n"
            summary += f"Confidence: {overall_confidence:.0%}"
            
            if expert_review:
                summary += "\n⚠️ Expert review recommended"
        
        return summary
    
    def save_formatted_response(self, response: str, output_path: str) -> bool:
        """Save formatted response to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response)
            
            logger.info(f"Formatted response saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save formatted response: {e}")
            return False

def main():
    """Test the Professional Response Formatter"""
    
    # Initialize formatter
    formatter = ProfessionalResponseFormatter()
    
    # Sample test data
    test_query = "২০২৫ অর্থবছরে ইউটিউব থেকে ৬ লক্ষ টাকা আয় হলে রিটার্ন দিতে হবে কি?"
    test_answer = "হ্যাঁ, ইউটিউব থেকে ৬ লক্ষ টাকা আয় থাকলে রিটার্ন দাখিল করতে হবে।"
    
    mock_reasoning = {
        'reasoning_steps': [
            {
                'step_type': 'query_analysis',
                'action': 'Query analysis identified return filing obligation',
                'evidence': ['Return filing keywords detected'],
                'confidence': 0.90
            },
            {
                'step_type': 'section_mapping', 
                'action': 'Mapped to Income Tax Act Section 75-76',
                'evidence': ['Section 75: Return filing requirement'],
                'confidence': 0.92
            }
        ],
        'alternative_interpretations': [
            'YouTube আয় ব্যবসায়িক আয় হিসেবে গণ্য',
            'YouTube আয় পেশাগত আয় হিসেবে গণ্য'
        ],
        'safety_warnings': []
    }
    
    mock_confidence = {
        'overall_confidence': 0.91,
        'confidence_level': 'good_advice',
        'factors': {
            'section_match_confidence': 0.92,
            'precedence_clarity': 0.90,
            'temporal_accuracy': 0.95,
            'completeness_score': 0.88,
            'consistency_score': 0.85,
            'ambiguity_penalty': 0.02
        },
        'expert_review_recommended': False,
        'safety_warnings': [],
        'safety_triggers': []
    }
    
    mock_sections = [
        {
            'section_id': 'ITA_2023_S75',
            'title': 'Return filing obligation',
            'document_type': 'income_tax_act_2023',
            'relevance_score': 0.92
        },
        {
            'section_id': 'ITA_2023_S44',
            'title': 'Tax-free income threshold',
            'document_type': 'income_tax_act_2023',
            'relevance_score': 0.88
        }
    ]
    
    # Format comprehensive response
    preferences = FormattingPreferences(
        language='bengali',
        format_type=ResponseFormat.COMPREHENSIVE,
        confidence_display=ConfidenceDisplayLevel.STANDARD
    )
    
    formatted_response = formatter.format_professional_response(
        query=test_query,
        legal_answer=test_answer,
        reasoning_trace=mock_reasoning,
        confidence_score=mock_confidence,
        matched_sections=mock_sections,
        preferences=preferences
    )
    
    # Display results
    print("\n" + "="*70)
    print("PROFESSIONAL RESPONSE FORMATTER TEST")
    print("="*70)
    
    print("\nComprehensive Professional Response:")
    print("-" * 40)
    print(formatted_response)
    
    # Test summary format
    print("\n" + "="*70)
    print("SUMMARY FORMAT TEST")
    print("="*70)
    
    summary_response = formatter.format_summary_response(
        query=test_query,
        legal_answer=test_answer,
        confidence_score=mock_confidence,
        language='bengali'
    )
    
    print(summary_response)
    
    # Save responses
    formatter.save_formatted_response(formatted_response, "test_professional_response.txt")
    formatter.save_formatted_response(summary_response, "test_summary_response.txt")
    
    print(f"\nResponses saved to files")

if __name__ == "__main__":
    main()