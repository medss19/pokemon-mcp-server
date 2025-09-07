# src/pokemon_mcp/utils/rate_limiter.py
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class RateLimitInfo:
    requests_made: int
    reset_time: float
    retry_after: Optional[float] = None

class TokenBucketRateLimiter:
    """Token bucket rate limiter for API requests"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60, burst_size: int = 10):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.burst_size = burst_size
        self.tokens = {}
        self.last_refill = {}
        
    async def is_allowed(self, identifier: str = "default") -> tuple[bool, RateLimitInfo]:
        """Check if request is allowed under rate limit"""
        now = time.time()
        
        # Initialize if first request for this identifier
        if identifier not in self.tokens:
            self.tokens[identifier] = self.burst_size
            self.last_refill[identifier] = now
            
        # Refill tokens based on time elapsed
        time_elapsed = now - self.last_refill[identifier]
        tokens_to_add = time_elapsed * (self.max_requests / self.window_seconds)
        self.tokens[identifier] = min(self.burst_size, self.tokens[identifier] + tokens_to_add)
        self.last_refill[identifier] = now
        
        info = RateLimitInfo(
            requests_made=int(self.max_requests - self.tokens[identifier]),
            reset_time=now + self.window_seconds
        )
        
        if self.tokens[identifier] >= 1:
            self.tokens[identifier] -= 1
            return True, info
        else:
            info.retry_after = 1.0 / (self.max_requests / self.window_seconds)
            return False, info

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    async def is_allowed(self, identifier: str = "default") -> tuple[bool, RateLimitInfo]:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests outside the window
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        current_requests = len(self.requests[identifier])
        
        info = RateLimitInfo(
            requests_made=current_requests,
            reset_time=self.requests[identifier][0] + self.window_seconds if self.requests[identifier] else now
        )
        
        if current_requests < self.max_requests:
            self.requests[identifier].append(now)
            return True, info
        else:
            # Calculate when next request can be made
            if self.requests[identifier]:
                info.retry_after = self.requests[identifier][0] + self.window_seconds - now
            return False, info

class CombinedRateLimiter:
    """Combines multiple rate limiting strategies"""
    
    def __init__(self, per_minute: int = 60, burst: int = 10):
        self.token_bucket = TokenBucketRateLimiter(per_minute, 60, burst)
        self.sliding_window = SlidingWindowRateLimiter(per_minute, 60)
        
    async def is_allowed(self, identifier: str = "default") -> tuple[bool, RateLimitInfo]:
        """Check both rate limiters"""
        token_allowed, token_info = await self.token_bucket.is_allowed(identifier)
        window_allowed, window_info = await self.sliding_window.is_allowed(identifier)
        
        # Both must allow the request
        allowed = token_allowed and window_allowed
        
        # Return the most restrictive information
        info = RateLimitInfo(
            requests_made=max(token_info.requests_made, window_info.requests_made),
            reset_time=max(token_info.reset_time, window_info.reset_time),
            retry_after=max(token_info.retry_after or 0, window_info.retry_after or 0) or None
        )
        
        return allowed, info
    
    async def wait_if_needed(self, identifier: str = "default") -> None:
        """Wait if rate limited"""
        allowed, info = await self.is_allowed(identifier)
        if not allowed and info.retry_after:
            await asyncio.sleep(info.retry_after)