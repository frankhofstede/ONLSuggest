"""
Story 1.3: Question Template Engine for Gemeente/Service Combinations

This module generates natural-sounding Dutch questions by combining:
- Query fragments from user input
- Gemeente names from database
- Service terms from database
- Question templates for various intents

Acceptance Criteria:
- Template system supports multiple question formats ("Hoe...", "Waar...", "Wat kost...")
- Templates dynamically insert gemeente names and service terms
- Generated questions are grammatically correct Dutch
- Template selection based on query intent/context
- At least 5 different question templates available
"""

from typing import List, Dict, Optional
from datetime import datetime


class QuestionTemplate:
    """Represents a Dutch question template with placeholders"""

    def __init__(self, template: str, intent: str, confidence_boost: float = 0.0):
        self.template = template
        self.intent = intent
        self.confidence_boost = confidence_boost

    def generate(self, service_name: str, gemeente_name: Optional[str] = None) -> str:
        """Generate a question from this template"""
        question = self.template.replace("{service}", service_name)
        if gemeente_name:
            question = question.replace("{gemeente}", gemeente_name)
        return question


class QuestionTemplateEngine:
    """
    Template engine for generating Dutch questions from gemeente/service combinations
    """

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> List[QuestionTemplate]:
        """
        Initialize question templates for different intents

        Supported placeholders:
        - {service}: The service name (e.g., "parkeervergunning", "paspoort")
        - {gemeente}: The gemeente name (e.g., "Amsterdam", "Rotterdam")
        """
        return [
            # HOW questions - Most common intent
            QuestionTemplate(
                "Hoe kan ik {service} in {gemeente}?",
                intent="procedure",
                confidence_boost=0.05
            ),
            QuestionTemplate(
                "Hoe vraag ik {service} aan?",
                intent="procedure",
                confidence_boost=0.05
            ),
            QuestionTemplate(
                "Hoe regel ik {service}?",
                intent="procedure",
                confidence_boost=0.03
            ),

            # COST questions
            QuestionTemplate(
                "Wat kost {service}?",
                intent="cost",
                confidence_boost=0.02
            ),
            QuestionTemplate(
                "Hoeveel kost {service} in {gemeente}?",
                intent="cost",
                confidence_boost=0.02
            ),

            # WHERE questions
            QuestionTemplate(
                "Waar kan ik {service} aanvragen?",
                intent="location",
                confidence_boost=0.02
            ),
            QuestionTemplate(
                "Waar moet ik zijn voor {service}?",
                intent="location",
                confidence_boost=0.02
            ),

            # WHAT questions - Information
            QuestionTemplate(
                "Wat is {service}?",
                intent="information",
                confidence_boost=0.01
            ),
            QuestionTemplate(
                "Wat moet ik weten over {service}?",
                intent="information",
                confidence_boost=0.01
            ),

            # WHEN questions - Timing
            QuestionTemplate(
                "Wanneer kan ik {service} aanvragen?",
                intent="timing",
                confidence_boost=0.01
            ),
            QuestionTemplate(
                "Hoe lang duurt {service}?",
                intent="timing",
                confidence_boost=0.01
            ),

            # WHICH questions - Requirements
            QuestionTemplate(
                "Welke documenten heb ik nodig voor {service}?",
                intent="requirements",
                confidence_boost=0.01
            ),
            QuestionTemplate(
                "Wat heb ik nodig voor {service}?",
                intent="requirements",
                confidence_boost=0.01
            ),
        ]

    def generate_suggestions(
        self,
        query: str,
        matched_services: List[Dict],
        max_results: int = 5
    ) -> List[Dict]:
        """
        Generate question suggestions from matched services

        Args:
            query: The user's search query
            matched_services: List of services with their gemeentes and confidence scores
            max_results: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries with:
            - suggestion: The generated question text
            - confidence: Confidence score (0.0 to 1.0)
            - service: Service information
            - gemeente: Gemeente name
        """
        suggestions = []

        for service_match in matched_services[:max_results * 2]:  # Generate more than needed
            service = service_match['service']
            gemeente = service_match.get('gemeente')
            base_confidence = service_match.get('confidence', 0.5)

            # Determine best templates based on query intent
            selected_templates = self._select_templates_for_query(query)

            for template in selected_templates[:3]:  # Use top 3 templates per service
                suggestion = {
                    "suggestion": template.generate(service['name'], gemeente),
                    "confidence": min(1.0, base_confidence + template.confidence_boost),
                    "service": {
                        "id": service['id'],
                        "name": service['name'],
                        "description": service.get('description', ''),
                        "category": service.get('category', 'Algemeen')
                    },
                    "gemeente": gemeente
                }
                suggestions.append(suggestion)

        # Sort by confidence and return top results
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:max_results]

    def _select_templates_for_query(self, query: str) -> List[QuestionTemplate]:
        """
        Select the most appropriate templates based on query keywords

        Keywords trigger specific intents:
        - "hoe", "aanvragen" -> procedure
        - "kosten", "prijs", "betalen" -> cost
        - "waar", "locatie", "adres" -> location
        - "wat", "informatie" -> information
        - "wanneer", "tijd", "duur" -> timing
        - "documenten", "nodig", "papieren" -> requirements
        """
        query_lower = query.lower()

        # Intent detection based on keywords
        intent_keywords = {
            "procedure": ["hoe", "aanvragen", "regelen", "doen"],
            "cost": ["kosten", "kost", "prijs", "betalen", "betaling"],
            "location": ["waar", "locatie", "adres", "kantoor"],
            "information": ["wat", "informatie", "info", "is"],
            "timing": ["wanneer", "tijd", "duur", "lang"],
            "requirements": ["documenten", "nodig", "papieren", "bewijs", "welke"],
        }

        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)

        # If no specific intent detected, default to procedure (most common)
        if not detected_intents:
            detected_intents = ["procedure"]

        # Return templates matching detected intents, sorted by confidence boost
        matching_templates = [
            t for t in self.templates
            if t.intent in detected_intents
        ]

        # Sort by confidence boost (descending)
        matching_templates.sort(key=lambda t: t.confidence_boost, reverse=True)

        # If we have few matches, add some general templates
        if len(matching_templates) < 3:
            general_templates = [t for t in self.templates if t.intent == "procedure"]
            matching_templates.extend(general_templates[:3 - len(matching_templates)])

        return matching_templates


# Global template engine instance
template_engine = QuestionTemplateEngine()
