"""
Checking agent responsible for verifying code functionality and correctness.
"""
import logging

from core.virtual_executor import VirtualExecutor
from utils.prompt_templates import CHECKING_PROMPT_TEMPLATE, CHECKING_SYSTEM_PROMPT


class CheckingAgent:
    """
    Specialized agent that handles code verification and testing.
    """
    
    def __init__(self, model_manager):
        """
        Initialize the checking agent.
        
        Args:
            model_manager: Model manager instance for making API calls
        """
        self.logger = logging.getLogger("checking_agent")
        self.model_manager = model_manager
        self.executor = VirtualExecutor()
    
    def verify_code(self, code, requirements=None):
        """
        Verify the generated code against requirements and test for functionality.
        
        Args:
            code (str): The generated code or code structure
            requirements (list): List of requirements to check against
            
        Returns:
            dict: Verification results including success status and improvements
        """
        self.logger.info("Verifying generated code")
        
        # First, do a static analysis with the checking model
        verification_result = self._static_code_analysis(code, requirements)
        
        # If static analysis finds critical issues, return the result
        if not verification_result["success"]:
            self.logger.warning("Static analysis found critical issues")
            return verification_result
        
        # If the code seems good, try to execute it if it's Python code
        if isinstance(code, dict) and any(filename.endswith('.py') for filename in code.keys()):
            # Execute the main Python file if we can identify it
            main_file = self._find_main_file(code)
            if main_file:
                execution_result = self._execute_code(code[main_file])
                
                # Update the verification result with execution details
                verification_result.update({
                    "execution": execution_result,
                    "success": verification_result["success"] and execution_result["success"]
                })
            
        elif isinstance(code, str) and "```python" in code:
            # Try to extract Python code and execute it
            import re
            python_code_match = re.search(r'```python\s*([\s\S]*?)\s*```', code)
            if python_code_match:
                python_code = python_code_match.group(1)
                execution_result = self._execute_code(python_code)
                
                # Update the verification result with execution details
                verification_result.update({
                    "execution": execution_result,
                    "success": verification_result["success"] and execution_result["success"]
                })
        
        self.logger.info(f"Code verification complete. Success: {verification_result['success']}")
        return verification_result
    
    def _static_code_analysis(self, code, requirements=None):
        """
        Perform static analysis on the code using the checking model.
        
        Args:
            code (str or dict): The generated code
            requirements (list): Requirements to check against
            
        Returns:
            dict: Analysis results
        """
        # Format code for the prompt
        if isinstance(code, dict):
            formatted_code = "\n\n".join([f"### {filename}\n```{self._get_language(filename)}\n{content}\n```" 
                                         for filename, content in code.items()])
        else:
            formatted_code = code
        
        # Format requirements for the prompt
        if requirements:
            formatted_requirements = "\n".join([f"- {req}" for req in requirements])
        else:
            formatted_requirements = "No specific requirements provided."
        
        # Format the checking prompt
        checking_prompt = CHECKING_PROMPT_TEMPLATE.format(
            code=formatted_code,
            requirements=formatted_requirements
        )
        
        # Call the checking model
        response = self.model_manager.call_model(
            model_type="checking",
            prompt=checking_prompt,
            system_prompt=CHECKING_SYSTEM_PROMPT
        )
        
        if not response["success"]:
            self.logger.error("Code checking failed: " + response.get("error", "Unknown error"))
            return {
                "success": False,
                "error": response.get("error", "Code checking failed")
            }
        
        # Parse the checking response
        return self._parse_checking_response(response["content"])
    
    def _parse_checking_response(self, content):
        """
        Parse the checking model's response to extract verification results.
        
        Args:
            content (str): Raw model response
            
        Returns:
            dict: Parsed verification results
        """
        import re
        
        # Look for a verdict/conclusion
        verdict_match = re.search(r'(?:verdict|conclusion|summary)[\s:]*([^\n]+)', content, re.IGNORECASE)
        verdict = verdict_match.group(1).strip() if verdict_match else "No clear verdict provided."
        
        # Determine if the code passed the check
        success_indicators = ["pass", "succeed", "success", "good", "work", "acceptable", "operational"]
        success = any(indicator in verdict.lower() for indicator in success_indicators)
        
        # Extract issues
        issues_section = re.search(r'(?:issues|problems|bugs|errors):([\s\S]*?)(?=##|\Z)', content, re.IGNORECASE)
        issues = []
        if issues_section:
            issues_text = issues_section.group(1).strip()
            # Extract bullet points
            issues = [line.strip().lstrip('-*•').strip() for line in issues_text.split('\n') 
                     if line.strip() and any(line.strip().startswith(bullet) for bullet in ['-', '*', '•'])]
        
        # Extract improvements/suggestions
        improvements_section = re.search(r'(?:improvements|suggestions|recommendations):([\s\S]*?)(?=##|\Z)', content, re.IGNORECASE)
        improvements = []
        if improvements_section:
            improvements_text = improvements_section.group(1).strip()
            # Extract bullet points
            improvements = [line.strip().lstrip('-*•').strip() for line in improvements_text.split('\n') 
                     if line.strip() and any(line.strip().startswith(bullet) for bullet in ['-', '*', '•'])]
        
        # Extract improved code if provided
        improved_code_match = re.search(r'```(\w*)\n([\s\S]*?)\n```', content)
        improved_code = improved_code_match.group(2) if improved_code_match else None
        
        return {
            "success": success and not any(re.search(r'critical|severe|major', issue, re.IGNORECASE) for issue in issues),
            "verdict": verdict,
            "issues": issues,
            "improvements": improvements,
            "improved_code": improved_code,
            "raw_analysis": content
        }
    
    def _execute_code(self, code):
        """
        Execute code in the virtual executor to test functionality.
        
        Args:
            code (str): Code to execute
            
        Returns:
            dict: Execution results
        """
        self.logger.info("Executing code in virtual environment")
        
        # Use the virtual executor to run the code
        execution_result = self.executor.sandbox_execution(code)
        
        if execution_result["success"]:
            self.logger.info("Code executed successfully")
        else:
            self.logger.warning(f"Code execution failed: {execution_result.get('error', 'Unknown error')}")
        
        return execution_result
    
    def _find_main_file(self, code_files):
        """
        Find the main Python file in a collection of files.
        
        Args:
            code_files (dict): Dictionary of filename -> code
            
        Returns:
            str: Name of the main file, or None if not found
        """
        # Look for common main file patterns
        for filename in code_files:
            if filename == "main.py" or "main" in filename:
                return filename
                
        # Look for files with if __name__ == "__main__":
        for filename, content in code_files.items():
            if filename.endswith('.py') and '__name__ == "__main__"' in content:
                return filename
        
        # If no clear main file, return the first Python file
        for filename in code_files:
            if filename.endswith('.py'):
                return filename
                
        return None
    
    def _get_language(self, filename):
        """
        Get the language type based on file extension.
        
        Args:
            filename (str): Filename with extension
            
        Returns:
            str: Language identifier for markdown code blocks
        """
        extension = filename.split('.')[-1].lower()
        
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'md': 'markdown',
            'sh': 'bash',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'cs': 'csharp',
            'php': 'php'
        }
        
        return language_map.get(extension, '')