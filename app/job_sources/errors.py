class JobSourceError(RuntimeError):
    """Base exception for job-source collection failures."""


class InvalidJobSourceError(JobSourceError):
    """Raised when a collector receives incompatible source configuration."""


class JobSourceRequestError(JobSourceError):
    """Raised when a job-source request cannot be completed."""


class JobSourcePayloadError(JobSourceError):
    """Raised when a provider returns an invalid or unexpected payload."""

class JobPostingConversionError(JobSourceError):
    """Raised when a raw posting cannot become a canonical job posting."""

class DuplicateJobSourceError(JobSourceError):
    """Raised when a provider is registered more than once."""


class JobSourceNotRegisteredError(JobSourceError):
    """Raised when no implementation is registered for a provider."""


class InvalidJobSourceImplementationError(JobSourceError):
    """Raised when a registered object does not satisfy JobSource."""