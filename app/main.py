from app.config.candidate import candidate
from app.matching.rule_matcher import calculate_rule_match
from app.models.job import JobPosting


def main() -> None:
    job = JobPosting(
        company="Example Company",
        requisition_id="JR1001",
        title="Junior Software Engineer",
        location="New York, NY",
        description=(
            "Build software applications using Python, SQL, Git, "
            "Linux, and Azure. This is an entry-level opportunity."
        ),
        application_url="https://example.com/jobs/JR1001",
    )

    result = calculate_rule_match(candidate, job)

    print(f"Match score: {result.score}/100")
    print(f"Matched skills: {result.matched_skills}")
    print(f"Matched roles: {result.matched_roles}")
    print(f"Location match: {result.location_match}")

    for reason in result.reasons:
        print(f"- {reason}")


if __name__ == "__main__":
    main()