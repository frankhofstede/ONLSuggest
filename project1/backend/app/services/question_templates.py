"""
Question template engine for generating natural Dutch questions.
Provides templates for different question types and context-aware selection.
"""
import random
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class TemplateType(Enum):
    """Question template types based on Dutch question words."""
    HOW = "hoe"  # How - application/request questions
    WHERE = "waar"  # Where - location questions
    WHAT = "wat"  # What - information/cost questions
    WHEN = "wanneer"  # When - timing questions
    WHO = "wie"  # Who - eligibility questions


@dataclass
class QuestionTemplate:
    """
    A question template with pattern and metadata.

    Attributes:
        pattern: Template string with {variable} placeholders
        type: Template type (HOW, WHERE, WHAT, WHEN, WHO)
        variables: Required variable names
        category_match: Service categories this template suits best
        weight: Template selection weight (higher = more likely)
    """
    pattern: str
    type: TemplateType
    variables: List[str]
    category_match: List[str] = None
    weight: float = 1.0

    def __post_init__(self):
        if self.category_match is None:
            self.category_match = []


class TemplateEngine:
    """Engine for rendering question templates with context-aware selection."""

    def __init__(self):
        """Initialize template engine with predefined Dutch question templates."""
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> List[QuestionTemplate]:
        """
        Create the initial set of Dutch question templates.

        Returns:
            List of QuestionTemplate objects
        """
        return [
            # HOW templates - Application/request questions
            QuestionTemplate(
                pattern="Hoe vraag ik {service} aan?",
                type=TemplateType.HOW,
                variables=["service"],
                category_match=["Documenten & Identiteit", "Vergunningen", "Subsidies"],
                weight=1.5
            ),
            QuestionTemplate(
                pattern="Hoe kan ik {service} aanvragen in {gemeente}?",
                type=TemplateType.HOW,
                variables=["service", "gemeente"],
                category_match=["Documenten & Identiteit", "Vergunningen"],
                weight=1.3
            ),
            QuestionTemplate(
                pattern="Hoe regel ik {service}?",
                type=TemplateType.HOW,
                variables=["service"],
                category_match=["Vergunningen", "Verkeer & Vervoer"],
                weight=1.2
            ),

            # WHERE templates - Location questions
            QuestionTemplate(
                pattern="Waar kan ik {service} aanvragen?",
                type=TemplateType.WHERE,
                variables=["service"],
                category_match=["Documenten & Identiteit", "Burgerzaken"],
                weight=1.0
            ),
            QuestionTemplate(
                pattern="Waar vind ik informatie over {service} in {gemeente}?",
                type=TemplateType.WHERE,
                variables=["service", "gemeente"],
                category_match=["Burgerzaken", "Jeugd & Onderwijs"],
                weight=1.1
            ),
            QuestionTemplate(
                pattern="Waar moet ik zijn voor {service}?",
                type=TemplateType.WHERE,
                variables=["service"],
                category_match=["Burgerzaken", "Documenten & Identiteit"],
                weight=0.9
            ),

            # WHAT templates - Information/cost questions
            QuestionTemplate(
                pattern="Wat kost {service}?",
                type=TemplateType.WHAT,
                variables=["service"],
                category_match=["Vergunningen", "Verkeer & Vervoer"],
                weight=1.2
            ),
            QuestionTemplate(
                pattern="Wat zijn de voorwaarden voor {service}?",
                type=TemplateType.WHAT,
                variables=["service"],
                category_match=["Subsidies", "Vergunningen", "Uitkeringen"],
                weight=1.1
            ),
            QuestionTemplate(
                pattern="Wat heb ik nodig voor {service}?",
                type=TemplateType.WHAT,
                variables=["service"],
                category_match=["Documenten & Identiteit", "Vergunningen"],
                weight=1.0
            ),

            # WHEN templates - Timing questions
            QuestionTemplate(
                pattern="Wanneer moet ik {service} aanvragen?",
                type=TemplateType.WHEN,
                variables=["service"],
                category_match=["Vergunningen", "Documenten & Identiteit"],
                weight=0.8
            ),
            QuestionTemplate(
                pattern="Wanneer krijg ik mijn {service}?",
                type=TemplateType.WHEN,
                variables=["service"],
                category_match=["Documenten & Identiteit", "Vergunningen"],
                weight=0.7
            ),

            # WHO templates - Eligibility questions
            QuestionTemplate(
                pattern="Wie kan {service} aanvragen?",
                type=TemplateType.WHO,
                variables=["service"],
                category_match=["Subsidies", "Uitkeringen", "Vergunningen"],
                weight=0.9
            ),
            QuestionTemplate(
                pattern="Voor wie is {service} bedoeld?",
                type=TemplateType.WHO,
                variables=["service"],
                category_match=["Subsidies", "Jeugd & Onderwijs", "Zorg & Welzijn"],
                weight=0.8
            ),

            # Generic templates (fallback)
            QuestionTemplate(
                pattern="Hoe werkt {service} in {gemeente}?",
                type=TemplateType.HOW,
                variables=["service", "gemeente"],
                category_match=[],
                weight=0.6
            ),
            QuestionTemplate(
                pattern="Welke {service} zijn er in {gemeente}?",
                type=TemplateType.WHAT,
                variables=["service", "gemeente"],
                category_match=[],
                weight=0.5
            ),
        ]

    def render(self, template: QuestionTemplate, **variables) -> str:
        """
        Render a template with provided variables.

        Args:
            template: QuestionTemplate to render
            **variables: Variable values (service, gemeente, etc.)

        Returns:
            Rendered question string

        Raises:
            ValueError: If required variables are missing
        """
        # Validate required variables
        missing = [var for var in template.variables if var not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        # Process variables for proper formatting
        processed_vars = {}
        for key, value in variables.items():
            if value is not None:
                # Lowercase service names for natural flow
                if key == "service":
                    processed_vars[key] = value.lower()
                else:
                    processed_vars[key] = value
            else:
                processed_vars[key] = ""

        # Render template
        return template.pattern.format(**processed_vars)

    def select_template(
        self,
        variables: Dict[str, Optional[str]],
        service_category: Optional[str] = None,
        used_templates: Optional[List[QuestionTemplate]] = None
    ) -> QuestionTemplate:
        """
        Select appropriate template based on context.

        Selection algorithm:
        1. Filter templates by available variables
        2. Boost templates matching service category
        3. Penalize recently used templates (for diversity)
        4. Weight randomization for natural variety

        Args:
            variables: Available variables (service, gemeente, etc.)
            service_category: Service category for matching
            used_templates: Recently used templates to avoid repetition

        Returns:
            Selected QuestionTemplate
        """
        if used_templates is None:
            used_templates = []

        # Filter templates by available variables
        available_vars = {k for k, v in variables.items() if v is not None}
        compatible_templates = [
            t for t in self.templates
            if set(t.variables).issubset(available_vars)
        ]

        if not compatible_templates:
            # Fallback to simplest template
            return self.templates[0]

        # Calculate selection weights
        weights = []
        for template in compatible_templates:
            weight = template.weight

            # Boost if category matches
            if service_category and service_category in template.category_match:
                weight *= 1.5

            # Penalize if recently used (reduce repetition)
            if template in used_templates:
                weight *= 0.3

            weights.append(weight)

        # Weighted random selection
        selected = random.choices(compatible_templates, weights=weights, k=1)[0]
        return selected

    def generate_question(
        self,
        service: Optional[str] = None,
        gemeente: Optional[str] = None,
        service_category: Optional[str] = None,
        used_templates: Optional[List[QuestionTemplate]] = None
    ) -> str:
        """
        Generate a natural Dutch question using template selection.

        Args:
            service: Service name
            gemeente: Gemeente name
            service_category: Service category for template matching
            used_templates: Recently used templates for diversity

        Returns:
            Generated question string
        """
        variables = {
            "service": service,
            "gemeente": gemeente
        }

        template = self.select_template(
            variables=variables,
            service_category=service_category,
            used_templates=used_templates
        )

        return self.render(template, **variables)

    def get_templates_by_type(self, template_type: TemplateType) -> List[QuestionTemplate]:
        """
        Get all templates of a specific type.

        Args:
            template_type: TemplateType to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self.templates if t.type == template_type]

    def get_template_count(self) -> int:
        """
        Get total number of templates.

        Returns:
            Number of templates
        """
        return len(self.templates)
