"""
Unit tests for question template engine.
Tests template rendering, selection, and Dutch question generation.
"""
import pytest
from app.services.question_templates import (
    TemplateEngine,
    QuestionTemplate,
    TemplateType
)


class TestQuestionTemplate:
    """Test QuestionTemplate dataclass."""

    def test_template_creation(self):
        """Test basic template creation."""
        template = QuestionTemplate(
            pattern="Hoe vraag ik {service} aan?",
            type=TemplateType.HOW,
            variables=["service"],
            category_match=["Documenten"],
            weight=1.0
        )

        assert template.pattern == "Hoe vraag ik {service} aan?"
        assert template.type == TemplateType.HOW
        assert template.variables == ["service"]
        assert template.category_match == ["Documenten"]
        assert template.weight == 1.0

    def test_template_default_category(self):
        """Test template with default empty category list."""
        template = QuestionTemplate(
            pattern="Test {service}",
            type=TemplateType.WHAT,
            variables=["service"]
        )

        assert template.category_match == []


class TestTemplateEngine:
    """Test TemplateEngine class."""

    def test_engine_initialization(self):
        """Test engine initializes with templates."""
        engine = TemplateEngine()

        assert len(engine.templates) > 0
        assert all(isinstance(t, QuestionTemplate) for t in engine.templates)

    def test_template_count(self):
        """Test minimum template count (AC5: at least 5 templates)."""
        engine = TemplateEngine()

        assert engine.get_template_count() >= 5

    def test_all_template_types_present(self):
        """Test all 5 template types are represented (AC1)."""
        engine = TemplateEngine()

        types_present = set(t.type for t in engine.templates)

        assert TemplateType.HOW in types_present
        assert TemplateType.WHERE in types_present
        assert TemplateType.WHAT in types_present
        assert TemplateType.WHEN in types_present
        assert TemplateType.WHO in types_present

    def test_render_service_only(self):
        """Test rendering template with service variable (AC2)."""
        engine = TemplateEngine()
        template = QuestionTemplate(
            pattern="Hoe vraag ik {service} aan?",
            type=TemplateType.HOW,
            variables=["service"]
        )

        result = engine.render(template, service="Paspoort aanvragen")

        assert result == "Hoe vraag ik paspoort aanvragen aan?"
        assert "paspoort aanvragen" in result.lower()

    def test_render_service_and_gemeente(self):
        """Test rendering with service and gemeente variables (AC2)."""
        engine = TemplateEngine()
        template = QuestionTemplate(
            pattern="Hoe kan ik {service} aanvragen in {gemeente}?",
            type=TemplateType.HOW,
            variables=["service", "gemeente"]
        )

        result = engine.render(template, service="Rijbewijs", gemeente="Amsterdam")

        assert "rijbewijs" in result.lower()
        assert "Amsterdam" in result

    def test_render_missing_variable_raises_error(self):
        """Test that missing required variables raise error."""
        engine = TemplateEngine()
        template = QuestionTemplate(
            pattern="Hoe vraag ik {service} aan?",
            type=TemplateType.HOW,
            variables=["service"]
        )

        with pytest.raises(ValueError, match="Missing required variables"):
            engine.render(template)

    def test_service_lowercase_formatting(self):
        """Test that service names are lowercased for natural flow."""
        engine = TemplateEngine()
        template = QuestionTemplate(
            pattern="Hoe vraag ik {service} aan?",
            type=TemplateType.HOW,
            variables=["service"]
        )

        result = engine.render(template, service="PARKEERVERGUNNING")

        assert "parkeervergunning" in result
        assert "PARKEERVERGUNNING" not in result

    def test_select_template_with_available_variables(self):
        """Test template selection based on available variables (AC4)."""
        engine = TemplateEngine()

        # Only service available
        template = engine.select_template(
            variables={"service": "Paspoort", "gemeente": None}
        )

        assert "service" in template.variables
        assert "gemeente" not in template.variables or template.variables.count("service") == len(template.variables)

    def test_select_template_category_matching(self):
        """Test template selection prefers matching category (AC4)."""
        engine = TemplateEngine()

        # Run multiple times due to randomization
        results = []
        for _ in range(10):
            template = engine.select_template(
                variables={"service": "Parkeervergunning"},
                service_category="Verkeer & Vervoer"
            )
            results.append("Verkeer & Vervoer" in template.category_match)

        # At least some should match category (weighted)
        assert any(results), "Category matching should influence selection"

    def test_template_diversity(self):
        """Test that used templates are less likely to be reselected."""
        engine = TemplateEngine()

        # Get first template
        template1 = engine.select_template(
            variables={"service": "Test"}
        )

        # Get multiple templates marking first as used
        different_templates = []
        for _ in range(10):
            template2 = engine.select_template(
                variables={"service": "Test"},
                used_templates=[template1]
            )
            different_templates.append(template2 != template1)

        # Most should be different
        assert sum(different_templates) > 5, "Template diversity should avoid repetition"

    def test_generate_question_service_only(self):
        """Test generating question with service only."""
        engine = TemplateEngine()

        question = engine.generate_question(service="Parkeervergunning")

        assert isinstance(question, str)
        assert len(question) > 0
        assert "parkeervergunning" in question.lower()
        assert "?" in question

    def test_generate_question_service_and_gemeente(self):
        """Test generating question with service and gemeente."""
        engine = TemplateEngine()

        question = engine.generate_question(
            service="Paspoort",
            gemeente="Rotterdam"
        )

        assert "paspoort" in question.lower()
        assert "Rotterdam" in question
        assert "?" in question

    def test_grammatical_correctness_hoe_template(self):
        """Test HOW template generates grammatically correct Dutch (AC3)."""
        engine = TemplateEngine()
        hoe_templates = engine.get_templates_by_type(TemplateType.HOW)

        assert len(hoe_templates) > 0

        # Test first HOW template
        template = hoe_templates[0]
        question = engine.render(template, service="rijbewijs", gemeente="Amsterdam")

        # Should start with "Hoe"
        assert question.startswith("Hoe")
        # Should end with question mark
        assert question.endswith("?")

    def test_grammatical_correctness_waar_template(self):
        """Test WHERE template generates grammatically correct Dutch (AC3)."""
        engine = TemplateEngine()
        waar_templates = engine.get_templates_by_type(TemplateType.WHERE)

        assert len(waar_templates) > 0

        template = waar_templates[0]
        question = engine.render(template, service="paspoort")

        assert question.startswith("Waar")
        assert question.endswith("?")

    def test_grammatical_correctness_wat_template(self):
        """Test WHAT template generates grammatically correct Dutch (AC3)."""
        engine = TemplateEngine()
        wat_templates = engine.get_templates_by_type(TemplateType.WHAT)

        assert len(wat_templates) > 0

        template = wat_templates[0]
        question = engine.render(template, service="parkeervergunning")

        assert question.startswith("Wat")
        assert question.endswith("?")

    def test_grammatical_correctness_wanneer_template(self):
        """Test WHEN template generates grammatically correct Dutch (AC3)."""
        engine = TemplateEngine()
        wanneer_templates = engine.get_templates_by_type(TemplateType.WHEN)

        assert len(wanneer_templates) > 0

        template = wanneer_templates[0]
        question = engine.render(template, service="rijbewijs")

        assert question.startswith("Wanneer")
        assert question.endswith("?")

    def test_grammatical_correctness_wie_template(self):
        """Test WHO template generates grammatically correct Dutch (AC3)."""
        engine = TemplateEngine()
        wie_templates = engine.get_templates_by_type(TemplateType.WHO)

        assert len(wie_templates) > 0

        template = wie_templates[0]
        question = engine.render(template, service="subsidie")

        assert question.startswith("Wie") or question.startswith("Voor wie")
        assert question.endswith("?")

    def test_special_characters_in_service_name(self):
        """Test handling of special characters in service names."""
        engine = TemplateEngine()

        question = engine.generate_question(
            service="Vergunning voor evenementen"
        )

        assert "vergunning voor evenementen" in question.lower()
        assert "?" in question

    def test_gemeente_with_article(self):
        """Test handling of gemeente names with articles."""
        engine = TemplateEngine()

        question = engine.generate_question(
            service="Parkeervergunning",
            gemeente="Den Haag"
        )

        assert "Den Haag" in question
        assert "parkeervergunning" in question.lower()

    def test_template_variety_in_generation(self):
        """Test that generate_question produces variety."""
        engine = TemplateEngine()

        questions = []
        for _ in range(10):
            question = engine.generate_question(service="Paspoort")
            questions.append(question)

        # Should have at least 2 different questions due to randomization
        unique_questions = set(questions)
        assert len(unique_questions) >= 2, "Should generate variety in questions"
