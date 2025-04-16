#!/usr/bin/env python3
"""
Main entry point for the AI Agent application.
"""
import sys
import os
import logging
from ui.simple_interface import SimpleInterface
from core.engine import AgentEngine

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger("main")
    logger.info("Starting AI Agent application...")
    
    # Initialize the core engine
    engine = AgentEngine()
    
    # Start the UI
    app = SimpleInterface(engine)
    app.run()

if __name__ == "__main__":
    main()