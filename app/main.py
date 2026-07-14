from app.collectors.base import JobCollector
from app.models.job import JobPosting


class ExampleCollector(JobCollector):
    """Temporary collector used to test the interface."""

    def collect_jobs(self) -> list[JobPosting]:
        return [
            JobPosting(
                company="Example Company",
                requisition_id="JR12345",
                title="Software Engineer I",
                location="New York, NY",
                description="Develop and maintain software applications.",
                application_url="https://example.com/jobs/JR12345",
            )
        ]


def main() -> None:
    collector = ExampleCollector()
    jobs = collector.collect_jobs()

    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()