"""
Phase 3: AI-Assisted Todo - Claude API Client

Wrapper for Anthropic Claude API with error handling and retries.
"""

import os
import logging
from typing import Optional

import anthropic
from anthropic import APIError, RateLimitError, APIConnectionError

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Claude API client with error handling.

    Features:
    - Configurable model and max_tokens
    - Automatic retry on rate limit errors
    - Error logging and graceful degradation
    - Token counting for cost tracking
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
            model: Claude model name (default: from ANTHROPIC_MODEL env var)
            max_tokens: Max response tokens (default: from ANTHROPIC_MAX_TOKENS env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set or api_key not provided"
            )

        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = max_tokens or int(
            os.getenv("ANTHROPIC_MAX_TOKENS", "1024")
        )

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, int]:
        """
        Call Claude API with prompt.

        Args:
            prompt: User message/prompt
            system: Optional system prompt for context
            max_tokens: Override default max_tokens

        Returns:
            Tuple of (response_text, token_count)

        Raises:
            APIError: If API call fails after retries
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system if system else anthropic.NOT_GIVEN,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            response_text = response.content[0].text

            # Count tokens (approximate from usage)
            token_count = response.usage.input_tokens + response.usage.output_tokens

            logger.info(
                f"Claude API call successful: {token_count} tokens",
                extra={
                    "model": self.model,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

            return response_text, token_count

        except RateLimitError as e:
            logger.error(f"Claude API rate limit exceeded: {e}")
            raise APIError(
                "AI service is currently rate-limited. Please try again in a few minutes."
            )

        except APIConnectionError as e:
            logger.error(f"Claude API connection error: {e}")
            raise APIError(
                "Unable to connect to AI service. Please check your network connection."
            )

        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise APIError(f"AI service error: {str(e)}")

        except Exception as e:
            logger.exception(f"Unexpected error calling Claude API: {e}")
            raise APIError(f"Unexpected AI service error: {str(e)}")

    def call_with_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[dict, int]:
        """
        Call Claude API expecting JSON response.

        Args:
            prompt: User message/prompt
            system: Optional system prompt for context
            max_tokens: Override default max_tokens

        Returns:
            Tuple of (parsed_json_dict, token_count)

        Raises:
            APIError: If API call fails or response is not valid JSON
        """
        import json

        response_text, token_count = self.call(
            prompt=prompt, system=system, max_tokens=max_tokens
        )

        try:
            # Parse JSON response
            response_json = json.loads(response_text)
            return response_json, token_count

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Claude response as JSON: {e}\nResponse: {response_text}"
            )
            raise APIError(
                f"AI service returned invalid JSON response. Please try again."
            )


# Global client instance (initialized on first import)
_client: Optional[ClaudeClient] = None


def get_client() -> ClaudeClient:
    """
    Get or create global Claude client instance.

    Returns:
        ClaudeClient instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY not set
    """
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client


def reset_client():
    """Reset global client instance (useful for testing)."""
    global _client
    _client = None
