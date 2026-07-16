from app.collectors.remotive import RemotiveCollector
from app.database.database import create_database
from app.parsing.candidate_builder import build_candidate_profile
from app.parsing.resume_parser import parse_resume
from app.pipeline.job_pipeline import JobPipeline


def main() -> None:
    create_database()

    resume = parse_resume("data/resume.pdf")

    candidate = build_candidate_profile(
        resume,
        preferred_locations=[
            "New Jersey",
            "New York",
            "Philadelphia",
            "Remote",
        ],
        willing_to_relocate=True,
        us_citizen=True,
    )

    collector = RemotiveCollector()

    pipeline = JobPipeline(
        collector=collector,
        candidate=candidate,
    )

    pipeline.run()


if __name__ == "__main__":
    main()