"""
Simple command-line interface for the AI Agent application.
"""

import logging
import os
import time


class SimpleInterface:
    """
    Implements a simple command-line interface for interacting with the AI agent.
    """

    def __init__(self, engine):
        """
        Initialize the interface.

        Args:
            engine: The agent engine instance
        """
        self.logger = logging.getLogger("interface")
        self.engine = engine

    def run(self):
        """Run the interface in interactive mode."""
        self.logger.info("Starting interactive mode")

        print("\n" + "=" * 60)
        print("  AI Agent - Powered by OpenRouter")
        print("=" * 60)
        print(
            "\nThis agent uses specialized models for planning, coding, and checking."
        )
        print(
            "Enter your coding or development request, and the agent will create a solution."
        )
        print("\nType 'exit' or 'quit' to exit.")
        print("Type 'save' after a result to save all files to the current directory.")
        print("-" * 60 + "\n")

        last_result = None

        while True:
            # Get user input
            user_input = input("\nYour request: ")

            if user_input.lower() in ("exit", "quit"):
                print("\nExiting AI Agent. Goodbye!")
                break

            elif user_input.lower() == "save" and last_result:
                self._save_files(last_result)
                continue

            # Process the request
            print("\nProcessing your request. This may take a few moments...\n")
            start_time = time.time()

            try:
                # Execute the pipeline
                result = self.engine.process_request(user_input)
                last_result = result

                # Display the result
                self._display_result(result)

                # Print execution time
                execution_time = time.time() - start_time
                print(f"\nRequest completed in {execution_time:.2f} seconds.")
                print(
                    "\nType 'save' to save the generated files to the current directory."
                )

            except Exception as e:
                self.logger.error(f"Error processing request: {str(e)}")
                print(f"\nAn error occurred: {str(e)}")

    def _display_result(self, result):
        """
        Display the result of processing a request.

        Args:
            result (dict): The result from the engine
        """
        # Display the plan summary
        if result.get("plan"):
            print("\n" + "=" * 60)
            print("PLANNING PHASE")
            print("=" * 60)

            if "raw_plan" in result["plan"]:
                print("\nPlan Overview:")
                plan_summary = result["plan"].get("plan", "")
                print(
                    plan_summary[:500] + "..."
                    if len(plan_summary) > 500
                    else plan_summary
                )

                if result["plan"].get("requirements"):
                    print("\nRequirements:")
                    for req in result["plan"]["requirements"][:5]:
                        print(f"- {req}")
                    if len(result["plan"]["requirements"]) > 5:
                        print(
                            f"- ...and {len(result['plan']['requirements']) - 5} more"
                        )

        # Display the code summary
        if result.get("code"):
            print("\n" + "=" * 60)
            print("CODING PHASE")
            print("=" * 60)

            if isinstance(result["code"], dict) and "file_structure" in result["code"]:
                print("\nGenerated Files:")
                for filename in result["code"]["file_structure"].keys():
                    print(f"- {filename}")

            # Show a snippet of explanation if available
            if result["code"].get("explanation"):
                explanation = result["code"]["explanation"]
                print("\nExplanation:")
                print(
                    explanation[:300] + "..." if len(explanation) > 300 else explanation
                )

        # Display verification results
        if result.get("verification"):
            print("\n" + "=" * 60)
            print("VERIFICATION PHASE")
            print("=" * 60)

            print(
                f"\nVerdict: {result['verification'].get('verdict', 'No verdict provided')}"
            )

            if result["verification"].get("issues"):
                print("\nIssues Found:")
                for issue in result["verification"]["issues"][:3]:
                    print(f"- {issue}")
                if len(result["verification"]["issues"]) > 3:
                    print(
                        f"- ...and {len(result['verification']['issues']) - 3} more issues"
                    )
            else:
                print("\nNo issues found.")

            # Show execution results if available
            if "execution" in result["verification"]:
                execution = result["verification"]["execution"]
                print("\nExecution Test:")
                if execution.get("success"):
                    print("✓ Code executed successfully")
                    if execution.get("stdout"):
                        print("\nOutput:")
                        output = execution["stdout"]
                        print(output[:200] + "..." if len(output) > 200 else output)
                else:
                    print("✗ Code execution failed")
                    if execution.get("error"):
                        print(f"Error: {execution['error']}")
                    elif execution.get("stderr"):
                        print(f"Error: {execution['stderr'][:200]}")

    def _save_files(self, result):
        """
        Save generated files to the current directory.

        Args:
            result (dict): The result containing generated code
        """
        if (
            not result
            or not result.get("code")
            or not result["code"].get("file_structure")
        ):
            print("No files to save.")
            return

        file_structure = result["code"]["file_structure"]
        output_dir = os.path.join(os.getcwd(), "aiagent_output")
        os.makedirs(output_dir, exist_ok=True)

        files_saved = 0

        for filename, content in file_structure.items():
            # Create directories if needed
            file_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                f.write(content)
            files_saved += 1

        print(f"\nSaved {files_saved} files to {output_dir}/")
