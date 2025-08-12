#!/usr/bin/env python3
"""
Contextual Disambiguation System
Phase 1.5 - Advanced Bengali Legal NER Implementation

Resolves ambiguous income types and legal contexts with interactive clarification.
Handles complex scenarios like YouTube income classification with multiple valid interpretations.
"""

import json
import re
from typing import List, Dict, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncomeType(Enum):
    """Income type classifications"""
    BUSINESS = "business_income"
    PROFESSIONAL = "professional_income"
    EMPLOYMENT = "employment_income"
    RENTAL = "rental_income"
    CAPITAL_GAIN = "capital_gain"
    FREELANCE = "freelance_income"
    ROYALTY = "royalty_income"
    OTHER = "other_income"

class TaxpayerType(Enum):
    """Taxpayer type classifications"""
    INDIVIDUAL = "individual"
    COMPANY = "company"
    PARTNERSHIP = "partnership"
    AOP = "association_of_persons"
    HUF = "hindu_undivided_family"
    COOPERATIVE = "cooperative_society"

@dataclass
class DisambiguationContext:
    """Context information for disambiguation"""
    query_text: str
    detected_entities: List[Dict]
    ambiguous_terms: List[str]
    potential_classifications: List[str]
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    clarification_needed: bool = False
    resolved_classification: Optional[str] = None

@dataclass
class ClarificationQuestion:
    """Clarification question for ambiguous cases"""
    question_bengali: str
    question_english: str
    options: List[Dict[str, str]]
    question_type: str
    priority: int = 1

class ContextualDisambiguator:
    """
    Contextual Disambiguation System for Bengali Legal Queries
    
    Resolves ambiguous income types and legal contexts through:
    - Pattern-based disambiguation rules
    - Interactive clarification dialogue
    - Context-aware classification
    - Intent refinement for complex scenarios
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize Contextual Disambiguator
        
        Args:
            knowledge_base_path: Path to legal knowledge base
        """
        self.knowledge_base_path = knowledge_base_path
        
        # Initialize disambiguation rules
        self.income_disambiguation_rules = self._initialize_income_rules()
        self.taxpayer_disambiguation_rules = self._initialize_taxpayer_rules()
        self.section_disambiguation_rules = self._initialize_section_rules()
        
        # Initialize clarification templates
        self.clarification_templates = self._initialize_clarification_templates()
        
        # Track disambiguation history
        self.disambiguation_history: List[DisambiguationContext] = []
        
        logger.info("🧠 Contextual Disambiguator initialized")
        logger.info(f"📋 Income rules: {len(self.income_disambiguation_rules)}")
        logger.info(f"👥 Taxpayer rules: {len(self.taxpayer_disambiguation_rules)}")
        logger.info(f"📜 Section rules: {len(self.section_disambiguation_rules)}")

    def _initialize_income_rules(self) -> Dict[str, Dict]:
        """Initialize income type disambiguation rules"""
        return {
            "youtube_income": {
                "triggers": [
                    "ইউটিউব", "youtube", "ইউটিউব আয়", "youtube income",
                    "ভিডিও আপলোড", "video upload", "চ্যানেল", "channel"
                ],
                "context_indicators": {
                    "business": [
                        "adsense", "বিজ্ঞাপন আয়", "advertisement revenue",
                        "নিয়মিত আপলোড", "regular upload", "ব্র্যান্ড স্পন্সর", "brand sponsor"
                    ],
                    "professional": [
                        "চুক্তিভিত্তিক", "contract based", "কোম্পানির সাথে", "with company",
                        "প্রোডাকশন হাউস", "production house", "মিডিয়া এজেন্সি", "media agency"
                    ],
                    "freelance": [
                        "ফ্রিল্যান্স", "freelance", "প্রজেক্ট বেসিস", "project basis",
                        "ভিডিও এডিটিং", "video editing", "কন্টেন্ট ক্রিয়েশন", "content creation"
                    ],
                    "royalty": [
                        "রয়্যালটি", "royalty", "সঙ্গীত", "music", "কপিরাইট", "copyright",
                        "লাইসেন্সিং", "licensing", "মেধা সম্পদ", "intellectual property"
                    ]
                },
                "clarification_questions": [
                    {
                        "question_bengali": "আপনি কি YouTube থেকে AdSense এর মাধ্যমে নিয়মিত আয় করেন?",
                        "question_english": "Do you earn regular income from YouTube through AdSense?",
                        "classification": "business",
                        "priority": 1
                    },
                    {
                        "question_bengali": "নাকি কোনো কোম্পানির সাথে চুক্তিভিত্তিক কাজ করেন?",
                        "question_english": "Or do you work on contract basis with companies?",
                        "classification": "professional",
                        "priority": 2
                    },
                    {
                        "question_bengali": "আপনি কি ফ্রিল্যান্স ভিত্তিতে ভিডিও তৈরি করেন?",
                        "question_english": "Do you create videos on freelance basis?",
                        "classification": "freelance",
                        "priority": 3
                    }
                ]
            },
            "online_income": {
                "triggers": [
                    "অনলাইন আয়", "online income", "ইন্টারনেট আয়", "internet income",
                    "ডিজিটাল আয়", "digital income", "ই-কমার্স", "e-commerce"
                ],
                "context_indicators": {
                    "business": [
                        "অনলাইন ব্যবসা", "online business", "দোকান", "shop",
                        "পণ্য বিক্রয়", "product sales", "ই-কমার্স", "e-commerce"
                    ],
                    "professional": [
                        "ওয়েব ডেভেলপমেন্ট", "web development", "গ্রাফিক্স ডিজাইন", "graphics design",
                        "ডিজিটাল মার্কেটিং", "digital marketing", "কনসালটেন্সি", "consultancy"
                    ],
                    "freelance": [
                        "ফ্রিল্যান্সিং", "freelancing", "upwork", "fiverr",
                        "প্রজেক্ট ভিত্তিক", "project based", "গিগ", "gig"
                    ]
                },
                "clarification_questions": [
                    {
                        "question_bengali": "আপনার অনলাইন আয়ের ধরন কী? ব্যবসা, সেবা, নাকি ফ্রিল্যান্সিং?",
                        "question_english": "What type of online income? Business, services, or freelancing?",
                        "classification": "general",
                        "priority": 1
                    }
                ]
            },
            "rental_income": {
                "triggers": [
                    "ভাড়া আয়", "rental income", "বাড়ি ভাড়া", "house rent",
                    "প্রপার্টি রেন্ট", "property rent", "ভাড়া", "rent"
                ],
                "context_indicators": {
                    "residential": [
                        "বাসা", "house", "ফ্ল্যাট", "flat", "অ্যাপার্টমেন্ট", "apartment",
                        "আবাসিক", "residential"
                    ],
                    "commercial": [
                        "দোকান", "shop", "অফিস", "office", "ব্যবসায়িক", "commercial",
                        "কমার্শিয়াল", "commercial property"
                    ],
                    "land": [
                        "জমি", "land", "প্লট", "plot", "কৃষি জমি", "agricultural land",
                        "ভূমি", "bhumi"
                    ]
                },
                "clarification_questions": [
                    {
                        "question_bengali": "এটি কি আবাসিক, ব্যবসায়িক, নাকি কৃষি সম্পত্তির ভাড়া?",
                        "question_english": "Is this residential, commercial, or agricultural property rent?",
                        "classification": "rental_type",
                        "priority": 1
                    }
                ]
            },
            "business_income": {
                "triggers": [
                    "ব্যবসা", "business", "ব্যবসায়িক আয়", "business income",
                    "ট্রেড", "trade", "বাণিজ্য", "commerce"
                ],
                "context_indicators": {
                    "manufacturing": [
                        "উৎপাদন", "manufacturing", "কারখানা", "factory",
                        "প্রোডাকশন", "production", "তৈরি", "making"
                    ],
                    "trading": [
                        "ব্যবসা", "trading", "কেনাবেচা", "buying selling",
                        "পাইকারি", "wholesale", "খুচরা", "retail"
                    ],
                    "service": [
                        "সেবা", "service", "সার্ভিস", "services",
                        "পরামর্শ", "consultation", "কনসালটেন্সি", "consultancy"
                    ]
                },
                "clarification_questions": [
                    {
                        "question_bengali": "আপনার ব্যবসার ধরন কী? উৎপাদন, ব্যবসা-বাণিজ্য, নাকি সেবা?",
                        "question_english": "What type of business? Manufacturing, trading, or services?",
                        "classification": "business_type",
                        "priority": 1
                    }
                ]
            }
        }

    def _initialize_taxpayer_rules(self) -> Dict[str, Dict]:
        """Initialize taxpayer type disambiguation rules"""
        return {
            "individual_vs_company": {
                "triggers": [
                    "আমার", "my", "আমি", "I", "ব্যক্তিগত", "personal",
                    "কোম্পানি", "company", "প্রতিষ্ঠান", "organization"
                ],
                "indicators": {
                    "individual": [
                        "আমার নামে", "in my name", "ব্যক্তিগত", "personal",
                        "একা", "alone", "নিজে", "myself"
                    ],
                    "company": [
                        "কোম্পানির নামে", "in company name", "লিমিটেড", "limited",
                        "প্রাইভেট লিমিটেড", "private limited", "পাবলিক লিমিটেড", "public limited"
                    ]
                }
            }
        }

    def _initialize_section_rules(self) -> Dict[str, Dict]:
        """Initialize legal section disambiguation rules"""
        return {
            "indirect_references": {
                "উক্ত_ধারা": {
                    "pattern": r"উক্ত\s*ধারা",
                    "resolution_strategy": "bind_to_recent_section",
                    "scope": "same_document",
                    "max_distance": 3  # sentences
                },
                "সংশ্লিষ্ট_তফসিল": {
                    "pattern": r"সংশ্লিষ্ট\s*তফসিল",
                    "resolution_strategy": "find_schedule_in_current_section",
                    "scope": "current_section",
                    "max_distance": 1
                },
                "পূর্বোক্ত_বিধি": {
                    "pattern": r"পূর্বোক্ত\s*বিধি",
                    "resolution_strategy": "bind_to_recent_rule",
                    "scope": "same_act",
                    "max_distance": 5
                }
            }
        }

    def _initialize_clarification_templates(self) -> Dict[str, List[Dict]]:
        """Initialize clarification question templates"""
        return {
            "income_classification": [
                {
                    "template_bengali": "আপনার {income_source} থেকে আয়ের ধরন সম্পর্কে আরও তথ্য দিন:",
                    "template_english": "Please provide more details about your {income_source} income type:",
                    "options": [
                        {"bengali": "নিয়মিত ব্যবসায়িক আয়", "english": "Regular business income"},
                        {"bengali": "পেশাগত সেবামূলক আয়", "english": "Professional service income"},
                        {"bengali": "ফ্রিল্যান্স/প্রজেক্ট ভিত্তিক আয়", "english": "Freelance/project-based income"},
                        {"bengali": "অন্যান্য", "english": "Others"}
                    ]
                }
            ],
            "taxpayer_classification": [
                {
                    "template_bengali": "আপনি কোন ধরনের করদাতা?",
                    "template_english": "What type of taxpayer are you?",
                    "options": [
                        {"bengali": "ব্যক্তি করদাতা", "english": "Individual taxpayer"},
                        {"bengali": "কোম্পানি", "english": "Company"},
                        {"bengali": "পার্টনারশিপ", "english": "Partnership"},
                        {"bengali": "সমিতি", "english": "Association of Persons"}
                    ]
                }
            ],
            "amount_clarification": [
                {
                    "template_bengali": "আপনার বার্ষিক আয়ের পরিমাণ কত?",
                    "template_english": "What is your annual income amount?",
                    "options": [
                        {"bengali": "৩.৫ লক্ষের কম", "english": "Less than 3.5 lakh"},
                        {"bengali": "৩.৫ লক্ষ - ৫ লক্ষ", "english": "3.5 lakh - 5 lakh"},
                        {"bengali": "৫ লক্ষ - ১০ লক্ষ", "english": "5 lakh - 10 lakh"},
                        {"bengali": "১০ লক্ষের বেশি", "english": "More than 10 lakh"}
                    ]
                }
            ]
        }

    def disambiguate_query(self, 
                          query_text: str, 
                          detected_entities: List[Dict]) -> DisambiguationContext:
        """
        Main disambiguation function
        
        Args:
            query_text: Input query text
            detected_entities: Entities detected by NER
            
        Returns:
            Disambiguation context with clarifications or resolved classification
        """
        logger.info(f"🧠 Disambiguating query: {query_text[:100]}...")
        
        # Create disambiguation context
        context = DisambiguationContext(
            query_text=query_text,
            detected_entities=detected_entities,
            ambiguous_terms=[],
            potential_classifications=[]
        )
        
        # Step 1: Identify ambiguous terms
        ambiguous_terms = self._identify_ambiguous_terms(query_text)
        context.ambiguous_terms = ambiguous_terms
        
        # Step 2: Apply disambiguation rules
        if ambiguous_terms:
            for term in ambiguous_terms:
                classifications = self._apply_disambiguation_rules(query_text, term)
                context.potential_classifications.extend(classifications)
                
                # Calculate confidence scores
                for classification in classifications:
                    confidence = self._calculate_classification_confidence(
                        query_text, term, classification
                    )
                    context.confidence_scores[f"{term}_{classification}"] = confidence
        
        # Step 3: Determine if clarification is needed
        needs_clarification = self._needs_clarification(context)
        context.clarification_needed = needs_clarification
        
        # Step 4: Auto-resolve if high confidence
        if not needs_clarification:
            resolved = self._auto_resolve_classification(context)
            context.resolved_classification = resolved
        
        # Add to history
        self.disambiguation_history.append(context)
        
        logger.info(f"✅ Disambiguation complete. Clarification needed: {needs_clarification}")
        return context

    def _identify_ambiguous_terms(self, query_text: str) -> List[str]:
        """Identify potentially ambiguous terms in query"""
        ambiguous_terms = []
        
        # Check for income-related ambiguity
        for income_type, rules in self.income_disambiguation_rules.items():
            for trigger in rules.get("triggers", []):
                if trigger.lower() in query_text.lower():
                    ambiguous_terms.append(income_type)
                    break
        
        return list(set(ambiguous_terms))

    def _apply_disambiguation_rules(self, query_text: str, term: str) -> List[str]:
        """Apply disambiguation rules for a specific term"""
        classifications = []
        
        if term in self.income_disambiguation_rules:
            rules = self.income_disambiguation_rules[term]
            context_indicators = rules.get("context_indicators", {})
            
            for classification, indicators in context_indicators.items():
                for indicator in indicators:
                    if indicator.lower() in query_text.lower():
                        classifications.append(classification)
                        break
        
        return list(set(classifications))

    def _calculate_classification_confidence(self, 
                                           query_text: str, 
                                           term: str, 
                                           classification: str) -> float:
        """Calculate confidence score for a classification"""
        confidence = 0.0
        
        if term in self.income_disambiguation_rules:
            rules = self.income_disambiguation_rules[term]
            context_indicators = rules.get("context_indicators", {}).get(classification, [])
            
            # Count matching indicators
            matches = 0
            total_indicators = len(context_indicators)
            
            for indicator in context_indicators:
                if indicator.lower() in query_text.lower():
                    matches += 1
            
            if total_indicators > 0:
                confidence = matches / total_indicators
            
            # Boost confidence for strong indicators
            strong_indicators = {
                "adsense": 0.9,
                "চুক্তিভিত্তিক": 0.8,
                "freelance": 0.85,
                "royalty": 0.9
            }
            
            for indicator, boost in strong_indicators.items():
                if indicator.lower() in query_text.lower():
                    confidence = max(confidence, boost)
        
        return min(confidence, 1.0)

    def _needs_clarification(self, context: DisambiguationContext) -> bool:
        """Determine if clarification is needed"""
        # If no ambiguous terms found, no clarification needed
        if not context.ambiguous_terms:
            return False
        
        # If multiple high-confidence classifications, need clarification
        high_confidence_count = sum(
            1 for score in context.confidence_scores.values() 
            if score > 0.8
        )
        
        if high_confidence_count > 1:
            return True
        
        # If no high-confidence classifications, need clarification
        max_confidence = max(context.confidence_scores.values()) if context.confidence_scores else 0.0
        
        return max_confidence < 0.7

    def _auto_resolve_classification(self, context: DisambiguationContext) -> Optional[str]:
        """Auto-resolve classification if confidence is high enough"""
        if not context.confidence_scores:
            return None
        
        # Find highest confidence classification
        max_score = max(context.confidence_scores.values())
        if max_score >= 0.8:
            for key, score in context.confidence_scores.items():
                if score == max_score:
                    return key
        
        return None

    def generate_clarification_questions(self, 
                                       context: DisambiguationContext) -> List[ClarificationQuestion]:
        """
        Generate clarification questions for ambiguous context
        
        Args:
            context: Disambiguation context
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        for ambiguous_term in context.ambiguous_terms:
            if ambiguous_term in self.income_disambiguation_rules:
                rules = self.income_disambiguation_rules[ambiguous_term]
                
                for q_data in rules.get("clarification_questions", []):
                    question = ClarificationQuestion(
                        question_bengali=q_data["question_bengali"],
                        question_english=q_data["question_english"],
                        options=[
                            {"bengali": "হ্যাঁ", "english": "Yes", "value": "yes"},
                            {"bengali": "না", "english": "No", "value": "no"}
                        ],
                        question_type=q_data.get("classification", "general"),
                        priority=q_data.get("priority", 1)
                    )
                    questions.append(question)
        
        # Sort by priority
        questions.sort(key=lambda x: x.priority)
        
        logger.info(f"🤔 Generated {len(questions)} clarification questions")
        return questions

    def resolve_with_clarification(self, 
                                 context: DisambiguationContext,
                                 clarification_responses: Dict[str, str]) -> str:
        """
        Resolve classification based on clarification responses
        
        Args:
            context: Original disambiguation context
            clarification_responses: User responses to clarification questions
            
        Returns:
            Resolved classification
        """
        logger.info("🎯 Resolving classification with clarification responses")
        
        # Simple resolution logic - can be made more sophisticated
        resolved_classification = "unknown"
        
        for ambiguous_term in context.ambiguous_terms:
            if ambiguous_term == "youtube_income":
                if clarification_responses.get("adsense_question") == "yes":
                    resolved_classification = "business_income"
                elif clarification_responses.get("contract_question") == "yes":
                    resolved_classification = "professional_income"
                elif clarification_responses.get("freelance_question") == "yes":
                    resolved_classification = "freelance_income"
                else:
                    resolved_classification = "other_income"
                break
        
        # Update context
        context.resolved_classification = resolved_classification
        
        logger.info(f"✅ Resolved classification: {resolved_classification}")
        return resolved_classification

    def resolve_indirect_reference(self, 
                                 text: str, 
                                 reference_pattern: str,
                                 document_context: Dict) -> Optional[str]:
        """
        Resolve indirect references like 'উক্ত ধারা'
        
        Args:
            text: Text containing indirect reference
            reference_pattern: Pattern to resolve
            document_context: Document context information
            
        Returns:
            Resolved canonical ID or None
        """
        if reference_pattern not in self.section_disambiguation_rules["indirect_references"]:
            return None
        
        rule = self.section_disambiguation_rules["indirect_references"][reference_pattern]
        strategy = rule["resolution_strategy"]
        
        if strategy == "bind_to_recent_section":
            return self._bind_to_recent_section(text, document_context, rule)
        elif strategy == "find_schedule_in_current_section":
            return self._find_schedule_in_section(document_context)
        elif strategy == "bind_to_recent_rule":
            return self._bind_to_recent_rule(text, document_context, rule)
        
        return None

    def _bind_to_recent_section(self, text: str, context: Dict, rule: Dict) -> Optional[str]:
        """Bind indirect reference to most recent section"""
        # Simple implementation - find most recent section reference
        section_patterns = [
            r'ধারা\s*([০-৯১-৯]+)',
            r'Section\s*(\d+)'
        ]
        
        recent_sections = []
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text))
            recent_sections.extend(matches)
        
        if recent_sections:
            # Sort by position and take the most recent one before current position
            recent_sections.sort(key=lambda x: x.start())
            # Return the section number of the most recent match
            last_match = recent_sections[-1]
            section_num = last_match.group(1)
            return f"ITA_2023_S{section_num.replace('০', '0').replace('১', '1').replace('২', '2').replace('৩', '3').replace('৪', '4').replace('৫', '5').replace('৬', '6').replace('৭', '7').replace('৮', '8').replace('৯', '9')}"
        
        return None

    def _find_schedule_in_section(self, context: Dict) -> Optional[str]:
        """Find schedule referenced in current section"""
        current_section = context.get("current_section", "")
        
        schedule_patterns = [
            r'তফসিল\s*([০-৯১-৯]+)',
            r'Schedule\s*(\d+)'
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, current_section)
            if match:
                schedule_num = match.group(1)
                return f"ITA_2023_SCH{schedule_num.replace('০', '0').replace('১', '1').replace('২', '2').replace('৩', '3').replace('৪', '4').replace('৫', '5').replace('৬', '6').replace('৭', '7').replace('৮', '8').replace('৯', '9')}"
        
        return None

    def _bind_to_recent_rule(self, text: str, context: Dict, rule: Dict) -> Optional[str]:
        """Bind to most recent rule reference"""
        # Similar to section binding but for rules
        rule_patterns = [
            r'বিধি\s*([০-৯১-৯]+)',
            r'Rule\s*(\d+)'
        ]
        
        for pattern in rule_patterns:
            match = re.search(pattern, text)
            if match:
                rule_num = match.group(1)
                return f"TDS_RULE_{rule_num}"
        
        return None

    def save_disambiguation_report(self, output_path: str) -> None:
        """Save disambiguation analysis report"""
        report = {
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "phase": "Phase_1.5_Contextual_Disambiguation",
                "version": "1.0",
                "total_disambiguations": len(self.disambiguation_history)
            },
            "disambiguation_statistics": {
                "total_queries_processed": len(self.disambiguation_history),
                "clarification_needed_count": sum(1 for ctx in self.disambiguation_history if ctx.clarification_needed),
                "auto_resolved_count": sum(1 for ctx in self.disambiguation_history if ctx.resolved_classification),
                "income_rule_types": len(self.income_disambiguation_rules),
                "taxpayer_rule_types": len(self.taxpayer_disambiguation_rules)
            },
            "rule_coverage": {
                "income_types_covered": list(self.income_disambiguation_rules.keys()),
                "taxpayer_types_covered": list(self.taxpayer_disambiguation_rules.keys()),
                "indirect_references_covered": list(self.section_disambiguation_rules["indirect_references"].keys())
            },
            "quality_metrics": {
                "disambiguation_accuracy": ">95% (target)",
                "clarification_success_rate": ">90% (target)",
                "false_positive_prevention": ">98% (target)"
            }
        }
        
        output_file = Path(output_path) / "disambiguation_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Disambiguation report saved to {output_file}")

def main():
    """Main function for testing contextual disambiguation"""
    logger.info("🧠 Testing Contextual Disambiguation System")
    
    disambiguator = ContextualDisambiguator()
    
    # Test queries
    test_queries = [
        {
            "text": "আমার ইউটিউব চ্যানেল থেকে মাসে ৫০ হাজার টাকা আয় হয়, এর জন্য কত কর দিতে হবে?",
            "entities": [
                {"text": "ইউটিউব", "type": "INCOME_SOURCE"},
                {"text": "৫০ হাজার টাকা", "type": "AMOUNT_BENGALI"}
            ]
        },
        {
            "text": "আমি অনলাইন ব্যবসা করি এবং ফ্রিল্যান্সিং ও করি, ধারা ২৫ কি প্রযোজ্য?",
            "entities": [
                {"text": "অনলাইন ব্যবসা", "type": "INCOME_SOURCE"},
                {"text": "ফ্রিল্যান্সিং", "type": "INCOME_SOURCE"},
                {"text": "ধারা ২৫", "type": "SECTION_DIRECT"}
            ]
        }
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        logger.info(f"\n--- Test Query {i} ---")
        
        context = disambiguator.disambiguate_query(
            test_query["text"], 
            test_query["entities"]
        )
        
        logger.info(f"Ambiguous terms: {context.ambiguous_terms}")
        logger.info(f"Confidence scores: {context.confidence_scores}")
        logger.info(f"Clarification needed: {context.clarification_needed}")
        
        if context.clarification_needed:
            questions = disambiguator.generate_clarification_questions(context)
            for q in questions:
                logger.info(f"Question: {q.question_bengali}")
    
    logger.info("✅ Contextual disambiguation testing completed")

if __name__ == "__main__":
    main()