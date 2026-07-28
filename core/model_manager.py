"""
Manages the connection to OpenRouter API and handles model selection and fallbacks.
"""

from __future__ import annotations

import logging
import os
import time

import requests

from config.models import CHECKING_MODELS, CODING_MODELS, PLANNING_MODELS


class ModelManager:
    """
    Handles API calls to AI models and implements fallback logic when
    a model is unavailable or reaches its rate limit.
    """

    def __init__(self) -> None:
        """Initialize the model manager with API credentials and model configurations."""
        self.logger = logging.getLogger("model_manager")

        # Get API key from environment or prompt user
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            self.api_key = input("Please enter your OpenRouter API key: ")

        self.base_url = "https://openrouter.ai/api/v1"
        self.request_timeouts = {}  # Track model request times for rate limiting

        self.logger.info("Model manager initialized")

    def select_model(
        self, model_type: str, previous_models: list[str] | None = None
    ) -> str:
        """
        Select an appropriate model for the task type, avoiding recently used models.

        Args:
            model_type (str): Type of model ('planning', 'coding', or 'checking')
            previous_models (list): Previously tried models to avoid

        Returns:
            str: Selected model identifier
        """
        if previous_models is None:
            previous_models = []

        if model_type == "planning":
            model_list = PLANNING_MODELS
        elif model_type == "coding":
            model_list = CODING_MODELS
        elif model_type == "checking":
            model_list = CHECKING_MODELS
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Filter out recently used models and those that hit rate limits
        current_time = time.time()
        available_models = [
            model
            for model in model_list
            if model not in previous_models
            and (
                model not in self.request_timeouts
                or current_time - self.request_timeouts.get(model, 0) > 60
            )
        ]

        if not available_models:
            # If all models are unavailable, take the least recently used one
            self.logger.warning("All models are busy. Using least recently used model.")
            return min(model_list, key=lambda m: self.request_timeouts.get(m, 0))

        # Return the first available model
        return available_models[0]

    def call_model(
        self,
        model_type: str,
        prompt: str,
        previous_models: list[str] | None = None,
        system_prompt: str | None = None,
    ) -> dict:
        """
        Make an API call to a selected model with fallback logic.

        Args:
            model_type (str): Type of model ('planning', 'coding', or 'checking')
            prompt (str): The user prompt to send to the model
            previous_models (list): Models that have been tried already
            system_prompt (str): Optional system prompt to guide the model

        Returns:
            dict: Response from the model API
        """
        if previous_models is None:
            previous_models = []

        # Select a model that hasn't been tried yet
        model = self.select_model(model_type, previous_models)

        try:
            self.logger.info(f"Calling {model} for {model_type} task")

            # Record request time for rate limiting
            self.request_timeouts[model] = time.time()

            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {"model": model, "messages": []}

            # Add system prompt if provided
            if system_prompt:
                payload["messages"].append({"role": "system", "content": system_prompt})

            # Add user prompt
            payload["messages"].append({"role": "user", "content": prompt})

            # Make the API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,  # 2-minute timeout
            )

            # Check for errors
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "model": model,
                "content": result["choices"][0]["message"]["content"],
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API call failed for {model}: {str(e)}")

            # Add the failed model to previous_models
            previous_models.append(model)

            # Try with the next model if we haven't exhausted all options
            if len(previous_models) < len(
                PLANNING_MODELS
                if model_type == "planning"
                else CODING_MODELS if model_type == "coding" else CHECKING_MODELS
            ):
                self.logger.info(f"Falling back to next available {model_type} model")
                return self.call_model(
                    model_type, prompt, previous_models, system_prompt
                )
            else:
                self.logger.critical("All models failed. Cannot complete request.")
                return {"success": False, "error": "All models failed to respond."}
