from app.models.job import JobPosting


def main() -> None:
    job = JobPosting(
        company="Example Company",
        requisition_id="JR12345",
        title="Software Engineer I",
        location="New York, NY",
        description="Develop and maintain software applications.",
        application_url="https://example.com/jobs/JR12345",
    )

    print(job)
    print(job.model_dump())


if __name__ == "__main__":
    main()