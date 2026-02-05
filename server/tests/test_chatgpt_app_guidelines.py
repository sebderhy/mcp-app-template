"""
ChatGPT Apps Development Guidelines Grading Tests.

These tests evaluate the MCP server against OpenAI's guidance from
docs/chatgpt-apps-development-guidelines.md.

Categories tested:
1. Value Proposition (Know/Do/Show)
2. Model-Friendly Outputs
3. Privacy by Design
4. Ecosystem Fit
5. First Turn Experience

Each test category contributes to an overall "grade" for the server.

NOTE: Unlike MCP best practices tests, these are "soft" grading tests.
Individual checks record scores but don't fail - only the final grade
(must be C or better) determines pass/fail. This allows the server to
have minor guideline deviations while still passing CI.
"""

import pytest
import re
import inspect
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel
import mcp.types as types


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


class ChatGPTGuidelinesReport:
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
            "CHATGPT APP GUIDELINES GRADE REPORT",
            "=" * 60,
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
_report = ChatGPTGuidelinesReport()


# =============================================================================
# 1. VALUE PROPOSITION TESTS (Know/Do/Show)
# =============================================================================

class TestValueProposition:
    """Tests for Section 2: The Three Ways to Add Real Value.

    Every tool should clearly provide Know, Do, or Show value.
    """

    @pytest.mark.asyncio
    async def test_tools_document_value_type(self):
        """Tool descriptions should indicate what value they provide (know/do/show).

        TODO: Improve with LLM. Current implementation uses keyword lists for each value
        type (know: 'fetch', 'get'; do: 'create', 'delete'; show: 'display', 'render').
        An LLM could understand that a tool 'Generates an interactive map of nearby
        restaurants' provides 'Show' value without containing keywords like 'display'.
        """
        from main import list_tools

        tools = await list_tools()

        # Keywords indicating each value type
        know_keywords = ['data', 'information', 'fetch', 'get', 'retrieve', 'lookup', 'search', 'find', 'query']
        do_keywords = ['create', 'update', 'delete', 'send', 'trigger', 'schedule', 'book', 'order', 'submit']
        show_keywords = ['display', 'show', 'render', 'visualize', 'present', 'view', 'chart', 'graph', 'dashboard']

        violations = []
        for tool in tools:
            desc_lower = tool.description.lower()
            name_lower = tool.name.lower()

            has_know = any(kw in desc_lower or kw in name_lower for kw in know_keywords)
            has_do = any(kw in desc_lower or kw in name_lower for kw in do_keywords)
            has_show = any(kw in desc_lower or kw in name_lower for kw in show_keywords)

            if not (has_know or has_do or has_show):
                violations.append(f"'{tool.name}' - unclear value type (Know/Do/Show)")

        score = 1.0 - (len(violations) / len(tools)) if tools else 0.0
        _report.add_result(GradeResult(
            category="1. Value Proposition",
            check_name="Clear Know/Do/Show value",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else "",
            weight=1.5,
            fix_hint="Use verbs that clarify value: 'show_*' for visual output, 'get_*'/'search_*' for data, 'create_*'/'send_*' for actions",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"Unclear value:\n" + "\n".join(violations)


# =============================================================================
# 2. MODEL-FRIENDLY OUTPUTS TESTS
# =============================================================================

class TestModelFriendlyOutputs:
    """Tests for Section 5: Build for the Model AND the User.

    Outputs should be structured, include IDs, and have summaries.
    """

    @pytest.mark.asyncio
    async def test_outputs_include_stable_ids(self):
        """Outputs with lists/items should include stable IDs for chaining."""
        from main import handle_call_tool, WIDGETS

        violations = []
        checked = 0

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
                # Check for lists/arrays that should have IDs
                for key, value in content.items():
                    if isinstance(value, list) and len(value) > 0:
                        checked += 1
                        if isinstance(value[0], dict):
                            # Items in list should have id or identifier
                            has_id = any(
                                'id' in str(item.keys()).lower()
                                for item in value
                                if isinstance(item, dict)
                            )
                            if not has_id:
                                violations.append(
                                    f"'{widget.identifier}.{key}' - list items missing 'id' field"
                                )

        if checked == 0:
            # No lists to check - pass by default
            score = 1.0
            passed = True
        else:
            score = 1.0 - (len(violations) / checked)
            passed = len(violations) == 0

        _report.add_result(GradeResult(
            category="2. Model-Friendly Outputs",
            check_name="List items have IDs",
            passed=passed,
            score=score,
            details="\n".join(violations) if violations else f"Checked {checked} lists",
            weight=1.2,
            fix_hint="Add 'id' field to each item: [{\"id\": \"item-1\", \"name\": \"...\"}, ...]",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert passed, f"Missing IDs:\n" + "\n".join(violations)

    @pytest.mark.asyncio
    async def test_complex_outputs_have_summary(self):
        """Complex outputs should include a human-readable summary field."""
        from main import handle_call_tool, WIDGETS

        violations = []
        checked = 0

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
                # Check outputs with multiple items or nested structures
                has_list = any(isinstance(v, list) and len(v) > 1 for v in content.values())
                has_nested = any(isinstance(v, dict) for v in content.values())

                if has_list or has_nested:
                    checked += 1
                    # Look for summary-like fields
                    summary_keys = ['summary', 'description', 'title', 'message', 'headline']
                    has_summary = any(
                        any(sk in key.lower() for sk in summary_keys)
                        for key in content.keys()
                    )
                    if not has_summary:
                        violations.append(f"'{widget.identifier}' - complex output missing summary field")

        if checked == 0:
            score = 1.0
            passed = True
        else:
            score = 1.0 - (len(violations) / checked)
            passed = len(violations) == 0

        _report.add_result(GradeResult(
            category="2. Model-Friendly Outputs",
            check_name="Complex outputs have summary",
            passed=passed,
            score=score,
            details="\n".join(violations) if violations else f"Checked {checked} complex outputs",
            weight=1.0,
            fix_hint="Add 'summary' or 'title' field: {\"summary\": \"3 items found\", \"items\": [...]}",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert passed, f"Missing summaries:\n" + "\n".join(violations)


# =============================================================================
# 3. PRIVACY BY DESIGN TESTS
# =============================================================================

class TestPrivacyByDesign:
    """Tests for Section 5: Privacy by Design.

    Avoid "blob" parameters that collect unnecessary context.
    """

    def test_no_blob_parameters(self):
        """Input models should not have generic "blob" parameters."""
        import main

        # Generic param names that suggest over-collection
        blob_names = ['context', 'data', 'payload', 'body', 'content', 'raw', 'blob', 'input']
        violations = []
        total_fields = 0

        for name in dir(main):
            obj = getattr(main, name)
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj is not BaseModel
                and name.endswith("Input")
            ):
                for field_name in obj.model_fields.keys():
                    total_fields += 1
                    if field_name.lower() in blob_names:
                        violations.append(f"'{name}.{field_name}' - generic blob parameter")

        score = 1.0 - (len(violations) / total_fields) if total_fields > 0 else 1.0
        _report.add_result(GradeResult(
            category="3. Privacy by Design",
            check_name="No blob parameters",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else f"Checked {total_fields} fields",
            weight=1.0,
            fix_hint="Replace generic params like 'data' with specific ones: 'user_id', 'search_query', 'item_name'",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"Blob parameters:\n" + "\n".join(violations)

    def test_minimal_required_fields(self):
        """Most fields should be optional (have defaults) to reduce friction."""
        import main

        violations = []
        models_checked = 0

        for name in dir(main):
            obj = getattr(main, name)
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseModel)
                and obj is not BaseModel
                and name.endswith("Input")
            ):
                models_checked += 1
                total_fields = len(obj.model_fields)
                required_fields = sum(
                    1 for f in obj.model_fields.values()
                    if f.is_required()
                )

                # Allow up to 2 required fields, or 25% of total
                max_required = max(2, total_fields * 0.25)
                if required_fields > max_required:
                    violations.append(
                        f"'{name}' - {required_fields}/{total_fields} required fields (max recommended: {int(max_required)})"
                    )

        score = 1.0 - (len(violations) / models_checked) if models_checked > 0 else 1.0
        _report.add_result(GradeResult(
            category="3. Privacy by Design",
            check_name="Minimal required fields",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else f"Checked {models_checked} models",
            weight=0.8,
            fix_hint="Add sensible defaults to most fields so tools work with minimal input",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"Too many required fields:\n" + "\n".join(violations)


# =============================================================================
# 4. ECOSYSTEM FIT TESTS
# =============================================================================

class TestEcosystemFit:
    """Tests for Section 6: Design for an Ecosystem.

    Outputs should be easy to chain with other tools/apps.
    """

    @pytest.mark.asyncio
    async def test_outputs_use_standard_field_names(self):
        """Outputs should use standard, predictable field names."""
        from main import handle_call_tool, WIDGETS

        # Standard field names that are easy to chain
        standard_names = {
            'id', 'name', 'title', 'description', 'summary', 'items', 'results',
            'url', 'link', 'image', 'price', 'count', 'total', 'status',
            'created', 'updated', 'type', 'value', 'label', 'text', 'message'
        }

        unusual_fields = []
        total_fields = 0

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
                    total_fields += 1
                    # Check if field name is standard or contains standard substring
                    key_lower = key.lower()
                    is_standard = any(std in key_lower for std in standard_names)
                    if not is_standard and not key_lower.startswith('_'):
                        unusual_fields.append(f"'{widget.identifier}.{key}'")

        # Allow up to 30% unusual fields (some domain-specific names are fine)
        unusual_ratio = len(unusual_fields) / total_fields if total_fields > 0 else 0
        passed = unusual_ratio <= 0.3
        score = max(0, 1.0 - unusual_ratio)

        _report.add_result(GradeResult(
            category="4. Ecosystem Fit",
            check_name="Standard field names",
            passed=passed,
            score=score,
            details=f"Unusual fields: {', '.join(unusual_fields[:5])}" + (f" (+{len(unusual_fields)-5} more)" if len(unusual_fields) > 5 else "") if unusual_fields else f"All {total_fields} fields use standard names",
            weight=0.8,
            fix_hint="Use common field names: 'id', 'title', 'items', 'url', 'description', 'status'",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert passed, f"Too many unusual field names (>30%)"

    @pytest.mark.asyncio
    async def test_no_deeply_nested_outputs(self):
        """Outputs should not be deeply nested (hard to chain)."""
        from main import handle_call_tool, WIDGETS

        def get_max_depth(obj, depth=0) -> int:
            if isinstance(obj, dict):
                if not obj:
                    return depth
                return max(get_max_depth(v, depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return depth
                return max(get_max_depth(item, depth + 1) for item in obj)
            return depth

        violations = []
        max_allowed_depth = 4

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
                depth = get_max_depth(result.root.structuredContent)
                if depth > max_allowed_depth:
                    violations.append(f"'{widget.identifier}' - depth {depth} (max {max_allowed_depth})")

        score = 1.0 - (len(violations) / len(WIDGETS)) if WIDGETS else 1.0
        _report.add_result(GradeResult(
            category="4. Ecosystem Fit",
            check_name="Shallow output structure",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else "",
            weight=0.6,
            fix_hint="Flatten deeply nested structures. Prefer {items: [{...}]} over {data: {nested: {items: [...]}}}",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"Deeply nested outputs:\n" + "\n".join(violations)


# =============================================================================
# 5. FIRST TURN EXPERIENCE TESTS
# =============================================================================

class TestFirstTurnExperience:
    """Tests for Section 4: Design for Conversation & Discovery.

    Tools should deliver value on first turn without excessive setup.
    """

    @pytest.mark.asyncio
    async def test_tools_work_with_no_args(self):
        """Tools should return useful output even with no arguments (first turn value)."""
        from main import handle_call_tool, WIDGETS

        violations = []

        for widget in WIDGETS:
            request = types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=widget.identifier,
                    arguments={},  # No args - simulates first turn
                ),
            )
            result = await handle_call_tool(request)

            # Should not be an error
            if result.root.isError:
                violations.append(f"'{widget.identifier}' - fails with no arguments")
            # Should have actual content
            elif not result.root.structuredContent:
                violations.append(f"'{widget.identifier}' - returns empty with no arguments")

        score = 1.0 - (len(violations) / len(WIDGETS)) if WIDGETS else 0.0
        _report.add_result(GradeResult(
            category="5. First Turn Experience",
            check_name="Works with no arguments",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else "",
            weight=1.5,
            fix_hint="Provide sensible defaults so tools show example/demo content when called without args",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"No-arg failures:\n" + "\n".join(violations)

    @pytest.mark.asyncio
    async def test_descriptions_explain_capability(self):
        """Tool descriptions should explain what the tool does in one line (cold start).

        TODO: Improve with LLM. Current implementation only checks length (20-200 chars).
        Length doesn't equal clarity - a 50-char description could be vague ('Does
        important data processing') while a 25-char one could be clear ('Finds nearby
        restaurants'). An LLM could assess whether the first line actually explains
        the capability clearly.
        """
        from main import list_tools

        tools = await list_tools()
        violations = []

        for tool in tools:
            # First line should be a clear capability statement
            first_line = tool.description.split('\n')[0].strip()

            # Should be substantial but not too long
            if len(first_line) < 20:
                violations.append(f"'{tool.name}' - first line too short: '{first_line}'")
            elif len(first_line) > 200:
                violations.append(f"'{tool.name}' - first line too long ({len(first_line)} chars)")

        score = 1.0 - (len(violations) / len(tools)) if tools else 0.0
        _report.add_result(GradeResult(
            category="5. First Turn Experience",
            check_name="Clear capability statement",
            passed=len(violations) == 0,
            score=score,
            details="\n".join(violations) if violations else "",
            weight=1.0,
            fix_hint="Start description with clear statement: 'Displays a carousel of items with images and descriptions.'",
        ))

        # Soft check - contributes to grade but doesn't fail test
        # assert len(violations) == 0, f"Poor first lines:\n" + "\n".join(violations)


# =============================================================================
# REPORT GENERATION
# =============================================================================

class TestGenerateReport:
    """Final test to generate and display the grade report."""

    def test_zzz_generate_grade_report(self, capsys):
        """Generate final grade report (zzz_ prefix ensures it runs last)."""
        report = _report.generate_report()
        print("\n" + report)

        # Write to file
        report_path = Path(__file__).parent / "chatgpt_app_guidelines_report.txt"
        report_path.write_text(report)

        # Check overall grade
        overall = _report.get_overall_score()
        grade = _report.get_grade_letter()

        # Pass if grade is C or better
        assert overall >= 70, f"ChatGPT App Guidelines Grade: {grade} ({overall:.1f}%) - needs improvement"
