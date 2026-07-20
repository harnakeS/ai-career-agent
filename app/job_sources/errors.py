class JobSourceError(RuntimeError):
    """Base exception for job-source collection failures."""


class InvalidJobSourceError(JobSourceError):
    """Raised when a collector receives incompatible source configuration."""


class JobSourceRequestError(JobSourceError):
    """Raised when a job-source request cannot be completed."""


class JobSourcePayloadError(JobSourceError):
    """Raised when a provider returns an invalid or unexpected payload."""