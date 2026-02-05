"""
Agentic UX Patterns Grading Tests.

These tests evaluate widgets against patterns from the "15 Lessons Learned
Building ChatGPT Apps" blog post (worthreading/15-lessons-building-chatgpt-apps.md).

The key insight is the "three body problem": ChatGPT Apps have three actors
(user, widget, model) with different information needs. Good apps explicitly
decide what context each actor sees.

Categories tested:
1. Data Front-Loading - Send enough data upfront to avoid lazy-loading delays
2. Context Separation - Use structuredContent vs _meta appropriately
3. Interactive State Sync - Interactive widgets should sync selection state
4. Language-First Inputs - Use constrained enums to enable natural language
5. Tool Annotations - Required flags for production deployment

Each test category contributes to an overall "grade" for agentic UX.
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mcp.types as types
from pydantic import BaseModel


# =============================================================================
# GRADING INFRASTRUCTURE
# =============================================================================

@dataclass
class GradeResult:
    """Result of a grading check."""
    category: str
    check_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: str
    weight: float = 1.0
    fix_hint: str = ""


class AgenticUXReport:
    """Collects grading results and generates a report."""

    def __init__(self):
        self.results: List[GradeResult] = []

    def add_result(self, result: GradeResult):
        self.results.append(result)

    def get_category_score(self, category: str) -> float:
        """Get weighted score for a category (0-100%)."""
        category_results = [r for r in self.results if r.category == category]
        if not category_results:
            return 0.0

        total_weight = sum(r.weight for r in category_results)
        weighted_sum = sum(r.score * r.weight for r in category_results)
        return (weighted_sum / total_weight) * 100 if total_weight > 0 else 0.0

    def get_overall_score(self) -> float:
        """Get overall weighted score (0-100%)."""
        if not self.results:
            return 0.0

        total_weight = sum(r.weight for r in self.results)
        weighted_sum = sum(r.score * r.weight for r in self.results)
        return (weighted_sum / total_weight) * 100 if total_weight > 0 else 0.0

    def get_grade_letter(self) -> str:
        """Convert score to letter grade."""
        score = self.get_overall_score()
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def generate_report(self) -> str:
        """Generate a human-readable report."""
        lines = [
            "=" * 60,
            "AGENTIC UX PATTERNS GRADE REPORT",
            "=" * 60,
            "",
            "Based on: 15 Lessons Learned Building ChatGPT Apps",
            "(worthreading/15-lessons-building-chatgpt-apps.md)",
            "",
        ]

        # Group by category
        categories: Dict[str, List[GradeResult]] = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = []
            categories[r.category].append(r)

        # Report each category
        for category, results in sorted(categories.items()):
            score = self.get_category_score(category)
            lines.append(f"\n{category}: {score:.1f}%")
            lines.append("-" * 40)

            for r in results:
                status = "✓" if r.passed else "✗"
                lines.append(f"  {status} {r.check_name}: {r.score*100:.0f}%")
                if not r.passed:
                    if r.fix_hint:
                        lines.append(f"      FIX: {r.fix_hint}")
                    if r.details:
                        for detail_line in r.details.split("\n"):
                            lines.append(f"      {detail_line}")

        # Overall score
        lines.append("\n" + "=" * 60)
        overall = self.get_overall_score()
        grade = self.get_grade_letter()
        lines.append(f"OVERALL SCORE: {overall:.1f}% (Grade: {grade})")
        lines.append("=" * 60)

        return "\n".join(lines)


# Global report instance
_report = AgenticUXReport()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_widget_tsx_files() -> List[Path]:
    """Get all widget App.tsx files."""
    src_dir = Path(__file__).resolve().parent.parent.parent / "src"
    return list(src_dir.glob("*/App.tsx"))


def _read_widget_tsx(widget_name: str) -> str:
    """Read the App.tsx content for a widget."""
    src_dir = Path(__file__).resolve().parent.parent.parent / "src"
    app_file = src_dir / widget_name / "App.tsx"
    if app_file.exists():
        return app_file.read_text(encoding="utf8")
    return ""


def _get_widget_py_files() -> List[Path]:
    """Get all widget Python files (excluding _base.py and __init__.py)."""
    widgets_dir = Path(__file__).resolve().parent.parent / "widgets"
    return [
        f for f in widgets_dir.glob("*.py")
        if not f.name.startswith("_") and f.name != "__init__.py"
    ]


# =============================================================================
# 1. DATA FRONT-LOADING TESTS (Lesson 2)
# =============================================================================

class TestDataFrontLoading:
    """Tests for Lesson 2: Lazy-loading doesn't translate well to AI apps.

    In ChatGPT Apps, tool calls take several seconds. Front-load data
    aggressively instead of fetching on demand.

    What this tests:
    - Are widgets returning substantial initial data?
    - Do widgets avoid patterns that suggest they need follow-up fetches?
    """

    @pytest.mark.asyncio
    async def test_initial_response_has_meaningful_data(self):
        """Tool responses should contain actual data, not just placeholders."""
        from main import handle_call_tool, WIDGETS

        thin_responses = []

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )
            result = await handle_call_tool(request)

            if result.root.structuredContent:
                content = result.root.structuredContent

                # Check for lists - should have at least some items
                for key, value in content.items():
                    if isinstance(value, list):
                        if len(value) == 0:
                            thin_responses.append(
                                f"'{widget.identifier}.{key}' - empty list on first call"
                            )
                        elif len(value) == 1 and isinstance(value[0], dict):
                            # Single placeholder item might indicate lazy loading pattern
                            item = value[0]
                            if all(v in [None, "", 0, False, "loading", "placeholder"]
                                   for v in item.values() if not isinstance(v, (dict, list))):
                                thin_responses.append(
                                    f"'{widget.identifier}.{key}' - single placeholder item"
                                )

        score = 1.0 - (len(thin_responses) / max(len(WIDGETS), 1))
        _report.add_result(GradeResult(
            category="1. Data Front-Loading",
            check_name="Meaningful initial data",
            passed=len(thin_responses) == 0,
            score=max(0, score),
            details="\n".join(thin_responses) if thin_responses else "",
            weight=1.5,
            fix_hint="Return real sample data on first call. Users see widget instantly without waiting for follow-up fetches.",
        ))

    @pytest.mark.asyncio
    async def test_no_pagination_without_initial_batch(self):
        """If a widget supports pagination, it should return a meaningful first batch."""
        from main import handle_call_tool, WIDGETS, WIDGET_INPUT_MODELS

        violations = []

        for widget in WIDGETS:
            input_model = WIDGET_INPUT_MODELS.get(widget.identifier)
            if not input_model:
                continue

            # Check if widget has pagination parameters
            fields = input_model.model_fields
            has_pagination = any(
                f in fields for f in ['page', 'offset', 'cursor', 'limit', 'page_size']
            )

            if has_pagination:
                # Call with default params
                request = types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name=widget.identifier,
                        arguments={},
                    ),
                )
                result = await handle_call_tool(request)

                if result.root.structuredContent:
                    content = result.root.structuredContent
                    # Check if any list has at least 3 items
                    has_batch = any(
                        isinstance(v, list) and len(v) >= 3
                        for v in content.values()
                    )
                    if not has_batch:
                        violations.append(
                            f"'{widget.identifier}' - has pagination but returns <3 items by default"
                        )

        # This is optional - only applies to paginated widgets
        checked_count = len([w for w in WIDGETS if WIDGET_INPUT_MODELS.get(w.identifier)])
        if checked_count == 0:
            score = 1.0
        else:
            score = 1.0 - (len(violations) / checked_count)

        _report.add_result(GradeResult(
            category="1. Data Front-Loading",
            check_name="Pagination has good defaults",
            passed=len(violations) == 0,
            score=max(0, score),
            details="\n".join(violations) if violations else "No pagination widgets or all return good batches",
            weight=0.8,
            fix_hint="Return at least 3-5 items by default so users see content immediately.",
        ))


# =============================================================================
# 2. CONTEXT SEPARATION TESTS (Lesson 1)
# =============================================================================

class TestContextSeparation:
    """Tests for Lesson 1: Not all context should be shared.

    The 'structuredContent' field is visible to both the model and widget.
    The '_meta' field is visible only to the widget (hidden from model).

    Use _meta for:
    - Display configuration (colors, layout hints)
    - Large binary data the model doesn't need
    - Secrets the model shouldn't see (in games, etc.)

    What this tests:
    - Are widgets using _meta for display-only config?
    - Is structuredContent free of display-only fields?
    """

    @pytest.mark.asyncio
    async def test_display_config_in_meta(self):
        """Display-only fields should be in _meta, not structuredContent."""
        from main import handle_call_tool, WIDGETS

        # Fields that are typically display-only and should be in _meta
        display_only_patterns = [
            'display_mode', 'layout', 'theme_override', 'animation',
            'show_header', 'hide_footer', 'compact_mode', 'column_count',
            'max_height', 'overflow_behavior'
        ]

        violations = []

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )
            result = await handle_call_tool(request)

            if result.root.structuredContent:
                for key in result.root.structuredContent.keys():
                    key_lower = key.lower()
                    for pattern in display_only_patterns:
                        if pattern in key_lower:
                            violations.append(
                                f"'{widget.identifier}.{key}' - display config should be in _meta"
                            )
                            break

        score = 1.0 if not violations else max(0, 1.0 - len(violations) * 0.2)
        _report.add_result(GradeResult(
            category="2. Context Separation",
            check_name="Display config in _meta",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else "No display-only fields in structuredContent",
            weight=1.0,
            fix_hint="Move display-only config to _meta: return types.ServerResult(structuredContent={...}, _meta={'ui': {...}, 'display': {...}})",
        ))

    @pytest.mark.asyncio
    async def test_structured_content_is_semantic(self):
        """structuredContent should contain semantic data the model can reason about."""
        from main import handle_call_tool, WIDGETS

        # Fields that suggest semantic, model-useful data
        semantic_indicators = [
            'id', 'name', 'title', 'description', 'summary', 'items', 'results',
            'count', 'total', 'status', 'type', 'category', 'value', 'price',
            'rating', 'location', 'date', 'time', 'url', 'label', 'message'
        ]

        widgets_with_semantic_data = 0

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},
                ),
            )
            result = await handle_call_tool(request)

            if result.root.structuredContent:
                keys = [k.lower() for k in result.root.structuredContent.keys()]
                has_semantic = any(
                    any(ind in key for ind in semantic_indicators)
                    for key in keys
                )
                if has_semantic:
                    widgets_with_semantic_data += 1

        score = widgets_with_semantic_data / len(WIDGETS) if WIDGETS else 1.0
        _report.add_result(GradeResult(
            category="2. Context Separation",
            check_name="Semantic structuredContent",
            passed=score >= 0.8,
            score=score,
            details=f"{widgets_with_semantic_data}/{len(WIDGETS)} widgets have semantic field names",
            weight=1.2,
            fix_hint="Use semantic field names like 'items', 'title', 'status' that the model can understand and reference.",
        ))


# =============================================================================
# 3. INTERACTIVE STATE SYNC TESTS (Lesson 3)
# =============================================================================

class TestInteractiveStateSync:
    """Tests for Lesson 3: The model needs visibility.

    When users interact with a widget (click, select, navigate), the model
    should know what they're looking at. Otherwise, follow-up questions like
    "tell me more about this one" will fail.

    Use window.openai.setWidgetState(state) to sync UI state to the model.

    What this tests:
    - Do interactive widgets (with click handlers) use setWidgetState?
    - Is selection state being communicated to the model?
    """

    def test_interactive_widgets_use_widget_state(self):
        """Widgets with selection/navigation state should use setWidgetState."""
        tsx_files = _get_widget_tsx_files()

        violations = []
        checked_count = 0

        for tsx_file in tsx_files:
            content = tsx_file.read_text(encoding="utf8")
            widget_name = tsx_file.parent.name

            # Look for selection state patterns (user selecting from multiple items)
            # These are the interactions where the model needs to know what user is looking at
            has_selection_state = any(p in content for p in [
                'selectedId', 'selectedIndex', 'selectedItem', 'selected_id',
                'activeId', 'activeIndex', 'activeItem', 'active_id',
                'currentId', 'currentIndex', 'currentItem', 'current_id',
                'setSelected', 'setActive', 'setCurrent',
            ])

            # Also check for click handlers on list items (not just navigation buttons)
            # Pattern: onClick on something with item/id context
            has_item_click = (
                'onClick={() =>' in content and
                any(p in content for p in ['item.id', 'item.name', 'selectedId', 'activeId'])
            )

            is_selection_interactive = has_selection_state or has_item_click

            if is_selection_interactive:
                checked_count += 1
                # Check if widget imports and uses useWidgetState
                uses_widget_state = 'useWidgetState' in content
                # Also check for setWidgetState directly
                uses_set_widget_state = 'setWidgetState' in content

                if not (uses_widget_state or uses_set_widget_state):
                    violations.append(
                        f"'{widget_name}' - has selection state but doesn't sync to model"
                    )

        if checked_count == 0:
            score = 1.0
            details = "No interactive widgets found"
        else:
            score = 1.0 - (len(violations) / checked_count)
            details = "\n".join(violations) if violations else f"All {checked_count} interactive widgets sync state"

        _report.add_result(GradeResult(
            category="3. Interactive State Sync",
            check_name="Selection state syncs to model",
            passed=len(violations) == 0,
            score=max(0, score),
            details=details,
            weight=1.5,
            fix_hint="When user selects an item, sync to model: const [state, setState] = useWidgetState({ selectedId: null }); then setState({ selectedId: item.id })",
        ))

    def test_selection_state_includes_identifier(self):
        """Widget state should include selected item ID for model reference."""
        tsx_files = _get_widget_tsx_files()

        good_patterns = []
        needs_improvement = []

        for tsx_file in tsx_files:
            content = tsx_file.read_text(encoding="utf8")
            widget_name = tsx_file.parent.name

            # Only check widgets that use useWidgetState
            if 'useWidgetState' not in content:
                continue

            # Check if state includes identifiers
            has_id_in_state = any(p in content for p in [
                'selectedId', 'selected_id', 'activeId', 'active_id',
                'currentId', 'current_id', 'focusedId', 'focused_id',
                'selectedItem', 'activeItem'
            ])

            if has_id_in_state:
                good_patterns.append(widget_name)
            else:
                needs_improvement.append(
                    f"'{widget_name}' - uses widgetState but may not include item identifier"
                )

        total = len(good_patterns) + len(needs_improvement)
        if total == 0:
            score = 1.0
            details = "No widgets use widgetState"
        else:
            score = len(good_patterns) / total
            details = "\n".join(needs_improvement) if needs_improvement else f"All {total} widgets include identifiers"

        _report.add_result(GradeResult(
            category="3. Interactive State Sync",
            check_name="State includes item identifiers",
            passed=len(needs_improvement) == 0,
            score=score,
            details=details,
            weight=1.0,
            fix_hint="Include selected item ID in state: setState({ selectedId: item.id, selectedName: item.name })",
        ))


# =============================================================================
# 4. LANGUAGE-FIRST INPUTS TESTS (Lesson 7)
# =============================================================================

class TestLanguageFirstInputs:
    """Tests for Lesson 7: Language-first filtering.

    Instead of complex filter UIs, let the model map natural language to
    tool parameters. Provide constrained values (enums) so the model knows
    valid options.

    Example: If user says "sunny destinations", model calls with weather="sunny"
    because the tool declares weather as enum ["sunny", "rainy", "cloudy"].

    What this tests:
    - Do input models use Literal/enum types for categorical fields?
    - Are enum values documented in descriptions?
    """

    def test_categorical_fields_use_enums(self):
        """Fields with limited valid values should use Literal types."""
        from main import WIDGET_INPUT_MODELS

        # Fields that typically should be enums (categorical, not numeric)
        categorical_patterns = [
            'category', 'type', 'status', 'sort_by', 'order_by', 'filter_by',
            'mode', 'style', 'variant', 'theme', 'layout'
        ]
        # Exclude patterns that look categorical but are typically numeric
        numeric_exceptions = ['size', 'level', 'priority', 'count', 'limit', 'border']

        good_enums = []
        missing_enums = []

        for tool_name, model in WIDGET_INPUT_MODELS.items():
            for field_name, field_info in model.model_fields.items():
                field_lower = field_name.lower()

                # Check if this looks like a categorical field
                is_categorical = any(p in field_lower for p in categorical_patterns)
                # Exclude numeric-looking fields
                is_numeric_exception = any(p in field_lower for p in numeric_exceptions)

                if is_categorical and not is_numeric_exception:
                    # Check if it's typed as Literal or has enum annotation
                    annotation = field_info.annotation
                    annotation_str = str(annotation) if annotation else ""

                    is_enum = (
                        'Literal' in annotation_str or
                        'Enum' in annotation_str or
                        hasattr(annotation, '__args__')  # Literal types have __args__
                    )

                    if is_enum:
                        good_enums.append(f"{tool_name}.{field_name}")
                    else:
                        # Check if description lists valid values
                        desc = field_info.description or ""
                        has_values_in_desc = any(
                            p in desc.lower()
                            for p in ['valid values:', 'options:', 'one of:', 'choices:']
                        )
                        if has_values_in_desc:
                            good_enums.append(f"{tool_name}.{field_name} (via description)")
                        else:
                            missing_enums.append(
                                f"'{tool_name}.{field_name}' - categorical field without enum/Literal type"
                            )

        total = len(good_enums) + len(missing_enums)
        if total == 0:
            score = 1.0
            details = "No categorical fields found"
        else:
            score = len(good_enums) / total
            details = "\n".join(missing_enums) if missing_enums else f"All {total} categorical fields use enums"

        _report.add_result(GradeResult(
            category="4. Language-First Inputs",
            check_name="Categorical fields use enums",
            passed=len(missing_enums) == 0,
            score=score,
            details=details,
            weight=1.2,
            fix_hint="Use Literal types: category: Literal['restaurants', 'hotels', 'attractions'] = 'restaurants'",
        ))

    def test_enum_values_documented(self):
        """Enum/Literal fields should have values listed in description."""
        from main import WIDGET_INPUT_MODELS

        undocumented = []
        documented = []

        for tool_name, model in WIDGET_INPUT_MODELS.items():
            for field_name, field_info in model.model_fields.items():
                annotation = field_info.annotation
                annotation_str = str(annotation) if annotation else ""

                # Check if this is a Literal/enum type
                if 'Literal' in annotation_str or hasattr(annotation, '__args__'):
                    desc = field_info.description or ""

                    # Check if description mentions valid values
                    has_values = any(
                        p in desc.lower()
                        for p in ['valid', 'options', 'choices', 'one of', 'values:']
                    ) or any(
                        # Or if the Literal values are in the description
                        str(arg) in desc
                        for arg in getattr(annotation, '__args__', [])
                        if isinstance(arg, str)
                    )

                    if has_values:
                        documented.append(f"{tool_name}.{field_name}")
                    else:
                        undocumented.append(
                            f"'{tool_name}.{field_name}' - enum values not in description"
                        )

        total = len(documented) + len(undocumented)
        if total == 0:
            score = 1.0
            details = "No enum fields found"
        else:
            score = len(documented) / total
            details = "\n".join(undocumented) if undocumented else f"All {total} enum fields documented"

        _report.add_result(GradeResult(
            category="4. Language-First Inputs",
            check_name="Enum values documented",
            passed=len(undocumented) == 0,
            score=score,
            details=details,
            weight=0.8,
            fix_hint="Include valid values in description: Field(description='Category to show. Options: restaurants, hotels, attractions')",
        ))


# =============================================================================
# 5. TOOL ANNOTATIONS TESTS (Lesson 10)
# =============================================================================

class TestToolAnnotations:
    """Tests for Lesson 10: Small widget flags have outsized impact.

    Tool annotations like readOnly, destructiveHint, and openWorldHint
    are required for ChatGPT Apps publication. They tell the host how
    to handle the tool safely.

    What this tests:
    - Do tools have required annotations?
    - Are destructive tools properly marked?
    """

    def test_widgets_have_annotations_in_description(self):
        """Tool descriptions should mention if they're read-only or have side effects."""
        from main import WIDGETS

        needs_annotation = []

        for widget in WIDGETS:
            desc_lower = widget.description.lower()

            # Check for read-only indicator
            is_read_only = any(p in desc_lower for p in [
                'read-only', 'readonly', 'display', 'show', 'view',
                'does not modify', 'no side effects'
            ])

            # Check for destructive indicator
            is_destructive = any(p in desc_lower for p in [
                'delete', 'remove', 'destroy', 'clear', 'reset', 'drop'
            ])

            # Check for external API indicator
            uses_external = any(p in desc_lower for p in [
                'external api', 'third-party', '3rd party', 'calls', 'fetches from'
            ])

            # Most display widgets should indicate they're read-only
            if widget.identifier.startswith('show_'):
                if not is_read_only:
                    needs_annotation.append(
                        f"'{widget.identifier}' - 'show_' tool should indicate read-only nature"
                    )

        score = 1.0 - (len(needs_annotation) / len(WIDGETS)) if WIDGETS else 1.0
        _report.add_result(GradeResult(
            category="5. Tool Annotations",
            check_name="Read-only tools documented",
            passed=len(needs_annotation) == 0,
            score=max(0, score),
            details="\n".join(needs_annotation) if needs_annotation else "All show_ tools indicate read-only",
            weight=1.0,
            fix_hint="Add to description: 'This is a read-only display tool with no side effects.'",
        ))

    def test_server_exposes_annotations_metadata(self):
        """Check if the server infrastructure supports tool annotations."""
        # Check if _base.py or main.py has annotation support
        base_path = Path(__file__).resolve().parent.parent / "widgets" / "_base.py"
        main_path = Path(__file__).resolve().parent.parent / "main.py"

        has_annotation_support = False

        for path in [base_path, main_path]:
            if path.exists():
                content = path.read_text(encoding="utf8")
                # Check for annotation-related code
                if any(p in content for p in [
                    'readOnly', 'read_only', 'destructive', 'openWorld',
                    'annotations', 'tool_meta', 'hints'
                ]):
                    has_annotation_support = True
                    break

        # This is informational - the framework may not need explicit annotation support
        # if it's handled by the MCP protocol layer
        _report.add_result(GradeResult(
            category="5. Tool Annotations",
            check_name="Annotation infrastructure",
            passed=True,  # Soft check - informational
            score=1.0 if has_annotation_support else 0.7,
            details="Annotation support found in server code" if has_annotation_support else "Consider adding explicit annotation support for production deployment",
            weight=0.5,
            fix_hint="Add tool annotations for production: readOnly=True, destructiveHint=False, openWorldHint=False",
        ))


# =============================================================================
# REPORT GENERATION
# =============================================================================

class TestGenerateReport:
    """Final test to generate and display the grade report."""

    def test_zzz_generate_agentic_ux_report(self, capsys):
        """Generate final grade report (zzz_ prefix ensures it runs last)."""
        report = _report.generate_report()
        print("\n" + report)

        # Write to file
        report_path = Path(__file__).parent / "agentic_ux_patterns_report.txt"
        report_path.write_text(report)

        # Check overall grade
        overall = _report.get_overall_score()
        grade = _report.get_grade_letter()

        # Pass if grade is D or better (soft grading - these are aspirational patterns)
        # The template widgets are examples; new widgets should aim for higher scores
        assert overall >= 60, f"Agentic UX Patterns Grade: {grade} ({overall:.1f}%) - review the report above"
