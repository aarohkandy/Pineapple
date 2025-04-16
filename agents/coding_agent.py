"""
Coding agent responsible for generating code based on planning inputs.
"""
import logging
import re
from utils.prompt_templates import CODING_SYSTEM_PROMPT, CODING_PROMPT_TEMPLATE

class CodingAgent:
    """
    Specialized agent that handles code generation based on the plan
    created by the planning agent.
    """
    
    def __init__(self, model_manager):
        """
        Initialize the coding agent.
        
        Args:
            model_manager: Model manager instance for making API calls
        """
        self.logger = logging.getLogger("coding_agent")
        self.model_manager = model_manager
    
    def generate_code(self, user_prompt, plan, research):
        """
        Generate code based on the user's request and planning results.
        
        Args:
            user_prompt (str): The original user request
            plan (str): The plan created by the planning agent
            research (str): Research information from the planning agent
            
        Returns:
            dict: Code generation results including code and explanations
        """
        self.logger.info("Generating code based on planning results")
        
        # Format the coding prompt
        coding_prompt = CODING_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt,
            plan=plan,
            research=research
        )
        
        # Call the coding model
        response = self.model_manager.call_model(
            model_type="coding",
            prompt=coding_prompt,
            system_prompt=CODING_SYSTEM_PROMPT
        )
        
        if not response["success"]:
            self.logger.error("Code generation failed: " + response.get("error", "Unknown error"))
            return {
                "success": False,
                "error": response.get("error", "Code generation failed")
            }
        
        # Extract code and explanations from the response
        code_blocks = self._extract_code_blocks(response["content"])
        
        if not code_blocks:
            self.logger.warning("No code blocks found in the response")
            return {
                "success": True,
                "code": response["content"],  # Return the raw content if no code blocks found
                "explanation": "",
                "file_structure": {}
            }
        
        # Process the extracted code
        file_structure = self._process_code_blocks(code_blocks)
        
        # Extract explanation
        explanation = self._extract_explanation(response["content"])
        
        self.logger.info(f"Successfully generated code with {len(file_structure)} files")
        return {
            "success": True,
            "code": response["content"],
            "explanation": explanation,
            "file_structure": file_structure
        }
    
    def _extract_code_blocks(self, content):
        """
        Extract code blocks from the model's response.
        
        Args:
            content (str): Raw model response
            
        Returns:
            list: Extracted code blocks with language and content
        """
        # Look for code blocks in markdown format: ```language\ncode\n```
        import re
        code_block_pattern = r'```(\w*)\n([\s\S]*?)\n```'
        matches = re.findall(code_block_pattern, content)
        
        code_blocks = []
        for language, code in matches:
            # Default to python if language is not specified
            if not language:
                language = "python"
                
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
    
    def _process_code_blocks(self, code_blocks):
        """
        Process code blocks to extract file information.
        
        Args:
            code_blocks (list): List of code blocks
            
        Returns:
            dict: File structure with filenames as keys and code as values
        """
        file_structure = {}
        
        # Attempt to identify filenames in the code blocks
        for i, block in enumerate(code_blocks):
            # Look for filename comments like "# filename.py" or "// filename.js"
            filename_pattern = r'(?:^|\n)(?:#|//)\s*([\w./]+\.[\w]+)'
            filename_match = re.search(filename_pattern, block["code"])
            
            if filename_match:
                filename = filename_match.group(1)
                # Remove the filename comment from the code
                code = re.sub(filename_pattern, '', block["code"], count=1).strip()
            else:
                # If no filename is found, generate one based on the language
                ext = self._get_extension_for_language(block["language"])
                filename = f"file_{i+1}{ext}"
                code = block["code"]
            
            file_structure[filename] = code
        
        return file_structure
    
    def _get_extension_for_language(self, language):
        """
        Get the file extension for a programming language.
        
        Args:
            language (str): Programming language
            
        Returns:
            str: File extension
        """
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "markdown": ".md",
            "bash": ".sh",
            "shell": ".sh",
            "ruby": ".rb",
            "go": ".go",
            "rust": ".rs",
            "java": ".java",
            "c": ".c",
            "cpp": ".cpp",
            "csharp": ".cs",
            "php": ".php"
        }
        
        return extensions.get(language.lower(), ".txt")
    
    def _extract_explanation(self, content):
        """
        Extract explanation text from the model's response.
        
        Args:
            content (str): Raw model response
            
        Returns:
            str: Extracted explanation
        """
        # Remove code blocks to get the explanation
        import re
        explanation = re.sub(r'```(\w*)\n[\s\S]*?\n```', '', content)
        
        # Clean up the explanation
        explanation = explanation.strip()
        
        return explanation