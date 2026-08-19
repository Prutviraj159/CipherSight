from dataclasses import dataclass

import structlog


logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    multiplier: float = 2.0
    max_delay_seconds: float = 30.0

    def next_delay(self, failed_attempts: int) -> float | None:
        if failed_attempts < 1 or failed_attempts >= self.max_attempts:
            logger.info("enrichment_retry_exhausted", failed_attempts=failed_attempts, max_attempts=self.max_attempts)
            return None
        delay = min(self.initial_delay_seconds * self.multiplier ** (failed_attempts - 1), self.max_delay_seconds)
        logger.info("enrichment_retry_scheduled", failed_attempts=failed_attempts, delay_seconds=delay)
        return delay
