"""Rate Limiting"""
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        current_count = len(self.requests[identifier])
        
        if current_count >= self.max_requests:
            return False, {
                'retry_after': int(self.requests[identifier][0] + self.window - now),
                'limit': self.max_requests,
                'remaining': 0
            }
        
        self.requests[identifier].append(now)
        
        return True, {
            'limit': self.max_requests,
            'remaining': self.max_requests - current_count - 1,
            'reset': int(now + self.window)
        }

if __name__ == "__main__":
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    for i in range(7):
        allowed, info = limiter.is_allowed("user_123")
        print(f"Request {i+1}: Allowed={allowed}, Remaining={info.get('remaining', 0)}")
