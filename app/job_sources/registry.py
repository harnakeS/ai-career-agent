from collections.abc import Mapping

from app.job_sources.errors import (
    DuplicateJobSourceError,
    InvalidJobSourceImplementationError,
    JobSourceNotRegisteredError,
)
from app.job_sources.models import JobSourceProvider
from app.job_sources.protocol import JobSource


class JobSourceRegistry:
    """Store and resolve job-source implementations by provider."""

    def __init__(
        self,
        sources: Mapping[
            JobSourceProvider,
            JobSource,
        ] | None = None,
    ) -> None:
        self._sources: dict[
            JobSourceProvider,
            JobSource,
        ] = {}

        for provider, source in (sources or {}).items():
            self.register(
                provider=provider,
                source=source,
            )

    def register(
        self,
        provider: JobSourceProvider,
        source: JobSource,
    ) -> None:
        """Register one implementation for a job-source provider."""

        if not isinstance(source, JobSource):
            raise InvalidJobSourceImplementationError(
                f"Implementation registered for "
                f"'{provider.value}' does not satisfy JobSource."
            )

        if provider in self._sources:
            raise DuplicateJobSourceError(
                f"A job source is already registered for "
                f"'{provider.value}'."
            )

        self._sources[provider] = source

    def get(
        self,
        provider: JobSourceProvider,
    ) -> JobSource:
        """Return the implementation registered for a provider."""

        source = self._sources.get(provider)

        if source is None:
            raise JobSourceNotRegisteredError(
                f"No job source is registered for "
                f"'{provider.value}'."
            )

        return source

    def contains(
        self,
        provider: JobSourceProvider,
    ) -> bool:
        """Return whether an implementation is registered."""

        return provider in self._sources

    @property
    def registered_providers(
        self,
    ) -> tuple[JobSourceProvider, ...]:
        """Return registered providers in registration order."""

        return tuple(self._sources)