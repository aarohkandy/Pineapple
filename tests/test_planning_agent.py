"""
Unit tests for PlanningAgent extraction helpers and the planning -> coding hand-off.

These cover the two historical defects in ``_extract_list`` (a ``NameError``
because ``re`` was only imported inside another method, and an invalid regex
range ``\\s-*`` in the character class) and confirm that activating the
previously dormant section-parsing path still feeds a sensible plan downstream.
"""

import unittest

from agents.planning_agent import PlanningAgent


class FakeModelManager:
    """Minimal stand-in for ModelManager that returns a canned response."""

    def __init__(self, content):
        self._content = content
        self.calls = []

    def call_model(self, model_type, prompt, system_prompt):
        self.calls.append({"model_type": model_type, "prompt": prompt})
        return {"success": True, "content": self._content}


class ExtractListTests(unittest.TestCase):
    def setUp(self):
        self.agent = PlanningAgent(None)

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(self.agent._extract_list(""), [])
        self.assertEqual(self.agent._extract_list("   \n  \n"), [])

    def test_strips_dash_star_and_bullet_markers(self):
        text = "- first\n* second\n• third"
        self.assertEqual(self.agent._extract_list(text), ["first", "second", "third"])

    def test_strips_numbered_markers_and_indentation(self):
        text = "1. alpha\n2. beta\n   3. gamma"
        self.assertEqual(self.agent._extract_list(text), ["alpha", "beta", "gamma"])

    def test_marker_only_and_blank_lines_produce_no_items(self):
        # A lone "-" collapses to an empty string and must not become an item.
        text = "-\n\n- real item\n   \n*   "
        self.assertEqual(self.agent._extract_list(text), ["real item"])

    def test_runs_without_nameerror_or_regex_error(self):
        # Regression guard for the two original defects. Before the fix this
        # call raised NameError (re not imported in scope); once re was in
        # scope it raised re.error for the invalid range "\\s-*". A plain,
        # successful call is enough to prove both are gone.
        self.assertEqual(self.agent._extract_list("- ok"), ["ok"])


class ExtractPlanningDataTests(unittest.TestCase):
    def setUp(self):
        self.agent = PlanningAgent(None)

    def test_json_block_is_preferred(self):
        content = 'prose\n```json\n{"plan": "do X", "requirements": ["r1"]}\n```'
        data = self.agent._extract_planning_data(content)
        self.assertEqual(data["plan"], "do X")
        self.assertEqual(data["requirements"], ["r1"])

    def test_sections_are_extracted_into_structured_fields(self):
        content = (
            "## Plan\nStep one then step two.\n\n"
            "## Research\nUse the requests library.\n\n"
            "## Requirements\n- must parse input\n- must handle errors\n\n"
            "## Tasks\n1. build parser\n2. add tests\n"
        )
        data = self.agent._extract_planning_data(content)
        self.assertEqual(data["plan"], "Step one then step two.")
        self.assertEqual(data["research"], "Use the requests library.")
        self.assertEqual(
            data["requirements"], ["must parse input", "must handle errors"]
        )
        self.assertEqual(data["task_breakdown"], ["build parser", "add tests"])

    def test_plan_falls_back_to_full_content_without_plan_section(self):
        # No JSON block and no "## Plan" header: the coding agent must still get
        # the full content as the plan, never an empty string. This is the
        # behavior that guards against the regression the fix could introduce.
        content = "Here is a freeform plan with no markdown headers at all."
        data = self.agent._extract_planning_data(content)
        self.assertEqual(data["plan"], content)
        self.assertEqual(data["requirements"], [])


class PlanningToCodingHandoffTests(unittest.TestCase):
    def test_create_plan_hands_nonempty_plan_downstream(self):
        content = (
            "## Plan\nWrite a function and a test.\n\n"
            "## Requirements\n- add function\n- add test\n"
        )
        agent = PlanningAgent(FakeModelManager(content))
        result = agent.create_plan("build a thing")

        self.assertTrue(result["success"])
        # engine.process_request forwards result["plan"]/["research"] to the
        # coding agent and result["requirements"] to the checking agent.
        self.assertTrue(result["plan"].strip(), "coding agent must get a real plan")
        self.assertEqual(result["plan"], "Write a function and a test.")
        self.assertEqual(result["requirements"], ["add function", "add test"])

    def test_create_plan_freeform_response_still_yields_a_plan(self):
        content = "Just prose, no headers, no json."
        agent = PlanningAgent(FakeModelManager(content))
        result = agent.create_plan("build a thing")

        self.assertTrue(result["success"])
        self.assertEqual(result["plan"], content)


if __name__ == "__main__":
    unittest.main()
