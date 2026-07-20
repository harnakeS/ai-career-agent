from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)
from app.job_sources.protocol import JobSource


def test_protocol_uses_structural_typing() -> None:
    class MinimalJobSource:
        def collect(
            self,
            source: CompanySource,
        ) -> list[RawJobPosting]:
            return []

    collector = MinimalJobSource()

    assert isinstance(collector, JobSource)


def test_object_without_collect_does_not_satisfy_protocol() -> None:
    class InvalidSource:
        pass

    collector = InvalidSource()

    assert not isinstance(collector, JobSource)