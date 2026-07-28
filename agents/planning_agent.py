"""
Planning agent responsible for breaking down tasks, researching, and creating a plan.
"""

from __future__ import annotations

import json
import logging

from utils.prompt_templates import PLANNING_PROMPT_TEMPLATE, PLANNING_SYSTEM_PROMPT


class PlanningAgent:
    """
    Specialized agent that handles the planning phase, including task decomposition,
    research, and creating a structured plan for the coding agent.
    """

    def __init__(self, model_manager) -> None:
        """
        Initialize the planning agent.

        Args:
            model_manager: Model manager instance for making API calls
        """
        self.logger = logging.getLogger("planning_agent")
        self.model_manager = model_manager

    def create_plan(self, user_prompt: str) -> dict:
        """
        Create a detailed plan based on the user's request.

        Args:
            user_prompt (str): The original user request

        Returns:
            dict: Planning results including plan, research, and requirements
        """
        self.logger.info("Creating plan for user request")

        # Format the planning prompt
        planning_prompt = PLANNING_PROMPT_TEMPLATE.format(user_prompt=user_prompt)

        # Call the planning model
        response = self.model_manager.call_model(
            model_type="planning",
            prompt=planning_prompt,
            system_prompt=PLANNING_SYSTEM_PROMPT,
        )

        if not response["success"]:
            self.logger.error(
                "Planning failed: " + response.get("error", "Unknown error")
            )
            return {"success": False, "error": response.get("error", "Planning failed")}

        # Parse the response
        try:
            # Extract JSON from the model response
            # The response should have clear delimiters for JSON data
            content = response["content"]

            # Extract JSON blocks from the response
            plan_data = self._extract_planning_data(content)

            if not plan_data:
                self.logger.warning(
                    "Could not parse planning response as JSON, using raw text"
                )
                return {
                    "success": True,
                    "raw_plan": content,
                    "plan": content,
                    "research": "",
                    "requirements": [],
                    "task_breakdown": [],
                }

            self.logger.info("Successfully created plan with task breakdown")
            return {"success": True, "raw_plan": content, **plan_data}

        except Exception as e:
            self.logger.error(f"Error parsing planning response: {str(e)}")
            return {
                "success": True,  # Still return true since we have raw content
                "raw_plan": response["content"],
                "plan": response["content"],
                "research": "",
                "requirements": [],
                "task_breakdown": [],
            }

    def _extract_planning_data(self, content: str) -> dict | None:
        """
        Extract structured planning data from the model's response.

        Args:
            content (str): Raw model response

        Returns:
            dict: Extracted planning data
        """
        # Look for JSON blocks in the response
        try:
            # Find JSON blocks between markers like ```json and ```
            import re

            json_matches = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", content)

            if json_matches:
                # Try each match until we find valid JSON
                for match in json_matches:
                    try:
                        data = json.loads(match)
                        return data
                    except Exception:
                        continue

            # If we can't find JSON blocks, look for sections
            plan_section = re.search(r"## Plan([\s\S]*?)(?=##|$)", content)
            research_section = re.search(r"## Research([\s\S]*?)(?=##|$)", content)
            requirements_section = re.search(
                r"## Requirements([\s\S]*?)(?=##|$)", content
            )
            tasks_section = re.search(r"## Tasks([\s\S]*?)(?=##|$)", content)

            result = {
                "plan": plan_section.group(1).strip() if plan_section else "",
                "research": (
                    research_section.group(1).strip() if research_section else ""
                ),
                "requirements": self._extract_list(
                    requirements_section.group(1) if requirements_section else ""
                ),
                "task_breakdown": self._extract_list(
                    tasks_section.group(1) if tasks_section else ""
                ),
            }

            return result

        except Exception as e:
            self.logger.warning(f"Error extracting planning data: {str(e)}")
            return None

    def _extract_list(self, text: str) -> list:
        """
        Extract a list of items from text, typically from bullet points.

        Args:
            text (str): Text with list items

        Returns:
            list: Extracted items
        """
        if not text:
            return []

        # Split by lines and filter empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Extract items from bullet points, numbers, etc.
        items = []
        for line in lines:
            # Remove bullet points, numbers, etc.
            clean_line = re.sub(r"^[\s-*•\d.]+\s*", "", line)
            if clean_line:
                items.append(clean_line)

        return items
