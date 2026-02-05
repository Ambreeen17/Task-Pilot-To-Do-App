"""
Phase 3: AI-Assisted Todo - Rate Limiter

Token bucket rate limiter to prevent AI API abuse.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """
    Token bucket for rate limiting.

    Tokens refill at a constant rate up to capacity.
    Each request consumes one token.
    """

    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: datetime

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume (default 1)

        Returns:
            True if tokens available, False if rate limited
        """
        # Refill tokens based on time elapsed
        now = datetime.now()
        elapsed_seconds = (now - self.last_refill).total_seconds()
        self.tokens = min(
            self.capacity, self.tokens + elapsed_seconds * self.refill_rate
        )
        self.last_refill = now

        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        else:
            return False

    def time_until_available(self) -> float:
        """
        Get seconds until next token available.

        Returns:
            Seconds to wait (0 if tokens available now)
        """
        if self.tokens >= 1.0:
            return 0.0
        return (1.0 - self.tokens) / self.refill_rate


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Limits:
    - Default: 100 requests per 24 hours per user
    - Configurable via environment variables
    """

    def __init__(
        self,
        requests_per_day: Optional[int] = None,
        window_hours: Optional[int] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_day: Max requests per user per day
            window_hours: Time window for rate limit (default 24)
        """
        self.requests_per_day = requests_per_day or int(
            os.getenv("AI_RATE_LIMIT_REQUESTS", "100")
        )
        self.window_hours = window_hours or int(
            os.getenv("AI_RATE_LIMIT_WINDOW_HOURS", "24")
        )

        # Calculate refill rate (tokens per second)
        self.refill_rate = self.requests_per_day / (self.window_hours * 3600)

        # In-memory buckets per user
        self.buckets: Dict[uuid.UUID, TokenBucket] = {}

        logger.info(
            f"Rate limiter initialized: {self.requests_per_day} requests per {self.window_hours} hours"
        )

    def _get_bucket(self, user_id: uuid.UUID) -> TokenBucket:
        """
        Get or create bucket for user.

        Args:
            user_id: User UUID

        Returns:
            TokenBucket for user
        """
        if user_id not in self.buckets:
            self.buckets[user_id] = TokenBucket(
                capacity=self.requests_per_day,
                refill_rate=self.refill_rate,
                tokens=self.requests_per_day,  # Start with full bucket
                last_refill=datetime.now(),
            )
        return self.buckets[user_id]

    def check_limit(self, user_id: uuid.UUID) -> tuple[bool, Optional[float]]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User UUID

        Returns:
            Tuple of (allowed, retry_after_seconds)
            - allowed: True if request allowed, False if rate limited
            - retry_after_seconds: Seconds to wait if rate limited, None if allowed
        """
        bucket = self._get_bucket(user_id)

        if bucket.consume():
            logger.debug(
                f"Rate limit check passed for user {user_id}: {bucket.tokens:.1f} tokens remaining"
            )
            return True, None
        else:
            retry_after = bucket.time_until_available()
            logger.warning(
                f"Rate limit exceeded for user {user_id}: retry after {retry_after:.1f}s"
            )
            return False, retry_after

    def consume(self, user_id: uuid.UUID, tokens: int = 1) -> bool:
        """
        Consume tokens from user's bucket.

        Args:
            user_id: User UUID
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed successfully, False if rate limited
        """
        bucket = self._get_bucket(user_id)
        success = bucket.consume(tokens)

        if success:
            logger.info(
                f"Consumed {tokens} token(s) for user {user_id}: {bucket.tokens:.1f} remaining"
            )
        else:
            logger.warning(f"Rate limit exceeded for user {user_id}")

        return success

    def get_remaining(self, user_id: uuid.UUID) -> int:
        """
        Get remaining requests for user.

        Args:
            user_id: User UUID

        Returns:
            Number of requests remaining (rounded down)
        """
        bucket = self._get_bucket(user_id)
        # Force refill calculation
        bucket.consume(0)
        return int(bucket.tokens)

    def reset(self, user_id: uuid.UUID):
        """
        Reset rate limit for user (for testing or admin override).

        Args:
            user_id: User UUID
        """
        if user_id in self.buckets:
            del self.buckets[user_id]
            logger.info(f"Rate limit reset for user {user_id}")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get or create global rate limiter instance.

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def reset_rate_limiter():
    """Reset global rate limiter instance (useful for testing)."""
    global _rate_limiter
    _rate_limiter = None
