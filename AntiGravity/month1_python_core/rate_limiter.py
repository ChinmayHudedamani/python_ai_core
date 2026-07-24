import time
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """
    Enterprise DDoS & Anti-Replay Rate Limiter.
    Limits intake requests per phone number / IP to prevent spam attacks and token exhaustion.
    Default Rule: Max 5 requests per 60 seconds per phone number.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests: int = max_requests
        self.window_seconds: int = window_seconds
        self.history: Dict[str, list] = {}

    def is_rate_limited(self, client_identifier: str) -> Tuple[bool, str]:
        """
        Evaluates whether a client identifier has exceeded request rate limits.
        Returns (True, refusal_msg) if rate limited; (False, "") if request allowed.
        """
        now: float = time.time()
        client_key: str = client_identifier.strip().lower()

        if client_key not in self.history:
            self.history[client_key] = []

        # Filter out timestamps outside current window
        window_start: float = now - self.window_seconds
        self.history[client_key] = [ts for ts in self.history[client_key] if ts > window_start]

        if len(self.history[client_key]) >= self.max_requests:
            return True, (
                "⚠️ **SECURITY ALERT: RATE LIMIT EXCEEDED** ⚠️\n\n"
                "You have exceeded the maximum request limit (5 requests / minute).\n"
                "Please wait 60 seconds before sending another message or contact clinic reception directly at +91-9988776655."
            )

        self.history[client_key].append(now)
        return False, ""


if __name__ == "__main__":
    limiter = TokenBucketRateLimiter(max_requests=3, window_seconds=60)
    client = "+91-9988776655"
    for i in range(1, 6):
        is_limited, msg = limiter.is_rate_limited(client)
        print(f"Request {i}: Limited={is_limited}")
