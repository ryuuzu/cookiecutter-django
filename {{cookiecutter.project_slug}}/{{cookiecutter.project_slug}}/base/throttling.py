import json
from dataclasses import dataclass
import logging

from django.core.cache import cache
from django.utils import timezone
from rest_framework.throttling import BaseThrottle

logger = logging.getLogger(__name__)


@dataclass
class ThrottleInfo:
    previously_throttled: bool
    request_count: int
    total_request_count: int
    total_times_throttled: int
    first_request_timestamp: float | None
    throttled_timestamp: float | None

    def __eq__(self, other):
        return (
            self.request_count == other.request_count
            and self.previously_throttled == other.previously_throttled
        )

    def __gt__(self, other):
        return self.request_count > other.request_count

    def __lt__(self, other):
        return self.request_count < other.request_count

    @classmethod
    def from_dict(cls, data: dict) -> "ThrottleInfo":
        return cls(
            previously_throttled=data.get("previously_throttled", False),
            request_count=data.get("request_count", 0),
            total_request_count=data.get("total_request_count", 0),
            total_times_throttled=data.get("total_times_throttled", 0),
            first_request_timestamp=data.get("first_request_timestamp"),
            throttled_timestamp=data.get("throttled_timestamp"),
        )

    def to_dict(self) -> dict:
        return {
            "previously_throttled": self.previously_throttled,
            "request_count": self.request_count,
            "total_request_count": self.total_request_count,
            "total_times_throttled": self.total_times_throttled,
            "first_request_timestamp": self.first_request_timestamp,
            "throttled_timestamp": self.throttled_timestamp,
        }


class ThrottleCache:
    # throttle_wait_time = [5, 10, 20, 40, 80]
    throttle_wait_time = [60, 120, 240, 480, 960]

    def __init__(self, ident: str, cache_scope: str, timeout=60, request_limit=5):
        self.ident = ident
        self.cache_key = f"throttle_{cache_scope}_{ident}"
        self.timeout = timeout
        self.request_limit = request_limit
        self.throttle_data = self._get_data_from_cache()

    def _get_data_from_cache(self) -> ThrottleInfo:
        """
        Get the throttle data from cache
        """
        data = cache.get(self.cache_key)
        if not data:
            return ThrottleInfo(
                previously_throttled=False,
                request_count=0,
                total_request_count=0,
                total_times_throttled=0,
                first_request_timestamp=None,
                throttled_timestamp=None,
            )

        return ThrottleInfo.from_dict(json.loads(data))

    def _update_data_to_cache(self):
        """
        Update the throttle data to cache
        """
        logger.info("Updating throttle data to cache for %s", self.cache_key)
        cache.set(
            self.cache_key,
            json.dumps(self.throttle_data.to_dict()),
            self.timeout + self.wait_time,
        )

    def reset_throttle_data(self):
        """
        Reset the throttle data
        """
        self.throttle_data.total_request_count += self.throttle_data.request_count
        self.throttle_data.total_times_throttled += 1
        self.throttle_data.request_count = 0
        self.throttle_data.previously_throttled = True
        self.throttle_data.first_request_timestamp = None
        self.throttle_data.throttled_timestamp = None
        self._update_data_to_cache()

    def register_request(self):
        """
        Register the request in cache
        """
        logger.info("Registering request for %s", self.cache_key)
        self.throttle_data.request_count += 1

        if not self.throttle_data.first_request_timestamp:
            self.throttle_data.first_request_timestamp = timezone.now().timestamp()

        self._update_data_to_cache()

    def should_throttle_request(self):
        """
        Check if the request should be throttled
        """
        request_limit_reached = self.throttle_data.request_count >= self.request_limit

        if request_limit_reached and not self.throttle_data.throttled_timestamp:
            self.throttle_data.throttled_timestamp = timezone.now().timestamp()

        if request_limit_reached:
            if self.throttle_data.previously_throttled:
                logger.warning(
                    "Request limit reached for %s. Violation Count: %d",
                    self.cache_key,
                    self.throttle_data.total_times_throttled,
                )
            else:
                logger.info("Request limit reached for %s", self.cache_key)

        return request_limit_reached

    @property
    def wait_time(self):
        """
        Punishes the user by increasing the wait time exponentially
        """
        try:
            return self.throttle_wait_time[self.throttle_data.total_times_throttled]
        except IndexError:
            return self.throttle_wait_time[-1]

    @property
    def allow_request_after(self):
        """
        Returns the time in seconds after which the request will be allowed
        """
        current_timestamp = timezone.now().timestamp()
        return (
            (
                self.throttle_data.throttled_timestamp
                + self.wait_time
                - current_timestamp
            )
            if self.throttle_data.throttled_timestamp
            else 0
        )


class AnonymousRequestThrottles(BaseThrottle):
    throttle_cache: ThrottleCache
    scope = "anonymous"

    def allow_request(self, request, view):
        ident = self.get_ident(request)
        self.throttle_cache = ThrottleCache(ident, self.scope)

        should_throttle_request = self.throttle_cache.should_throttle_request()

        self.throttle_cache.register_request()

        if (should_throttle_request and self.throttle_cache.allow_request_after < 0) or request.user.is_authenticated:
            self.throttle_cache.reset_throttle_data()
            return True

        return not should_throttle_request

    def wait(self):
        if not self.throttle_cache:
            return 0

        return self.throttle_cache.allow_request_after
