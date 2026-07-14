from abc import ABC, abstractmethod

from app.models.job import JobPosting


class JobCollector(ABC):
    """Base interface for all job collectors."""

    @abstractmethod
    def collect_jobs(self) -> list[JobPosting]:
        """Retrieve active job postings from a career site."""
        raise NotImplementedError