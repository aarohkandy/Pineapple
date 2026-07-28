"""
Utilities for parsing and analyzing code.
"""

import ast
import logging
import re


class CodeParser:
    """
    Provides utilities for parsing and analyzing code structures.
    """

    def __init__(self) -> None:
        """Initialize the code parser."""
        self.logger = logging.getLogger("code_parser")

    def extract_code_blocks(self, text: str) -> list:
        """
        Extract code blocks from markdown-formatted text.

        Args:
            text (str): Text containing markdown code blocks

        Returns:
            list: List of dicts with language and code content
        """
        code_block_pattern = r"```(\w*)\n([\s\S]*?)\n```"
        matches = re.findall(code_block_pattern, text)

        code_blocks = []
        for language, code in matches:
            code_blocks.append(
                {"language": language if language else "text", "code": code}
            )

        return code_blocks

    def extract_imports(self, python_code: str) -> list:
        """
        Extract import statements from Python code.

        Args:
            python_code (str): Python code

        Returns:
            list: List of imported modules
        """
        try:
            tree = ast.parse(python_code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)

            return imports
        except SyntaxError:
            self.logger.warning(
                "Could not parse Python code for imports due to syntax errors"
            )
            return []

    def extract_functions(self, python_code: str) -> list:
        """
        Extract function names and signatures from Python code.

        Args:
            python_code (str): Python code

        Returns:
            list: List of dicts with function name, args, and docstring
        """
        try:
            tree = ast.parse(python_code)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    args = [arg.arg for arg in node.args.args]

                    functions.append(
                        {
                            "name": node.name,
                            "args": args,
                            "docstring": docstring if docstring else "",
                        }
                    )

            return functions
        except SyntaxError:
            self.logger.warning(
                "Could not parse Python code for functions due to syntax errors"
            )
            return []

    def extract_classes(self, python_code: str) -> list:
        """
        Extract class names, methods, and inheritance from Python code.

        Args:
            python_code (str): Python code

        Returns:
            list: List of dicts with class information
        """
        try:
            tree = ast.parse(python_code)
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    bases = [
                        base.id for base in node.bases if isinstance(base, ast.Name)
                    ]

                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            methods.append(child.name)

                    classes.append(
                        {
                            "name": node.name,
                            "bases": bases,
                            "methods": methods,
                            "docstring": docstring if docstring else "",
                        }
                    )

            return classes
        except SyntaxError:
            self.logger.warning(
                "Could not parse Python code for classes due to syntax errors"
            )
            return []

    def analyze_code_complexity(self, python_code: str) -> dict:
        """
        Simple analysis of code complexity.

        Args:
            python_code (str): Python code

        Returns:
            dict: Complexity metrics
        """
        try:
            tree = ast.parse(python_code)

            # Count various code constructs
            functions = 0
            classes = 0
            loops = 0
            conditionals = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                elif isinstance(node, (ast.For, ast.While)):
                    loops += 1
                elif isinstance(node, (ast.If, ast.IfExp)):
                    conditionals += 1

            return {
                "functions": functions,
                "classes": classes,
                "loops": loops,
                "conditionals": conditionals,
                "lines": len(python_code.split("\n")),
            }
        except SyntaxError:
            self.logger.warning(
                "Could not analyze code complexity due to syntax errors"
            )
            return {
                "functions": 0,
                "classes": 0,
                "loops": 0,
                "conditionals": 0,
                "lines": len(python_code.split("\n")),
            }
