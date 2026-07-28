"""
Core engine that coordinates between the planning, coding, and checking agents.
"""

import logging

from agents.checking_agent import CheckingAgent
from agents.coding_agent import CodingAgent
from agents.planning_agent import PlanningAgent
from core.model_manager import ModelManager


class AgentEngine:
    """Main orchestrator for the AI Agent application."""

    def __init__(self):
        """Initialize the engine and its agent components."""
        self.logger = logging.getLogger("engine")
        self.model_manager = ModelManager()

        # Initialize the specialized agents
        self.planning_agent = PlanningAgent(self.model_manager)
        self.coding_agent = CodingAgent(self.model_manager)
        self.checking_agent = CheckingAgent(self.model_manager)

        self.logger.info("Agent engine initialized with all components")

    def process_request(self, user_prompt):
        """
        Process a user request through the complete pipeline:
        planning → coding → checking

        Args:
            user_prompt (str): The user's original request

        Returns:
            dict: Results including final code, explanations, and execution results
        """
        self.logger.info("Processing new user request")

        # Step 1: Planning phase
        self.logger.info("Starting planning phase")
        planning_result = self.planning_agent.create_plan(user_prompt)

        # Step 2: Coding phase
        self.logger.info("Starting coding phase")
        code_result = self.coding_agent.generate_code(
            user_prompt, planning_result["plan"], planning_result["research"]
        )

        # Step 3: Checking phase
        self.logger.info("Starting verification phase")
        verification_result = self.checking_agent.verify_code(
            code_result["code"], planning_result["requirements"]
        )

        # Return the complete result
        return {
            "plan": planning_result,
            "code": code_result,
            "verification": verification_result,
            "success": verification_result["success"],
            "final_code": verification_result.get("improved_code", code_result["code"]),
        }
