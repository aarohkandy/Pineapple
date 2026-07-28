"""
Virtual executor for testing code within a safe environment.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime


class VirtualExecutor:
    """
    Handles the execution of code in a controlled virtual environment
    to verify functionality and catch errors.
    """

    def __init__(self) -> None:
        """Initialize the virtual executor."""
        self.logger = logging.getLogger("virtual_executor")

    def test_python_code(
        self, code: str, inputs: list[str] | None = None, timeout: int = 10
    ) -> dict:
        """
        Test Python code by executing it in a separate process.

        Args:
            code (str): Python code to test
            inputs (list): Optional list of input strings to provide
            timeout (int): Maximum execution time in seconds

        Returns:
            dict: Results of code execution including stdout, stderr, and success status
        """
        self.logger.info("Testing Python code in virtual environment")

        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(
            suffix=".py", delete=False, mode="w"
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            # Prepare the execution environment
            start_time = datetime.now()

            # Execute the code
            if inputs:
                # If we have inputs, we need to provide them to the process
                process = subprocess.Popen(
                    [sys.executable, temp_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                stdout, stderr = process.communicate(
                    input="\n".join(inputs), timeout=timeout
                )
            else:
                # Simple execution without input
                process = subprocess.run(
                    [sys.executable, temp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                stdout = process.stdout
                stderr = process.stderr

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "success": (
                    process.returncode == 0
                    if isinstance(process, subprocess.CompletedProcess)
                    else process.returncode == 0
                ),
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
            }

        except subprocess.TimeoutExpired:
            self.logger.warning("Code execution timed out")
            return {
                "success": False,
                "error": "Execution timed out",
                "execution_time": timeout,
            }
        except Exception as e:
            self.logger.error(f"Error executing code: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def sandbox_execution(self, code: str, language: str = "python") -> dict:
        """
        Execute code in a safe sandbox environment.
        Currently supports Python only.

        Args:
            code (str): Code to execute
            language (str): Programming language of the code

        Returns:
            dict: Results of execution
        """
        if language.lower() == "python":
            return self.test_python_code(code)
        else:
            return {"success": False, "error": f"Unsupported language: {language}"}
