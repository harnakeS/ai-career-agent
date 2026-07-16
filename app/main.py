from app.collectors.remotive import RemotiveCollector
from app.config.preferences import load_candidate_preferences
from app.database.database import create_database
from app.parsing.candidate_builder import build_candidate_profile
from app.parsing.resume_parser import parse_resume
from app.pipeline.job_pipeline import JobPipeline


def main() -> None:
    create_database()

    resume = parse_resume("data/resume.pdf")
    preferences = load_candidate_preferences(
        "config/preferences.json"
    )

    candidate = build_candidate_profile(
        resume,
        preferred_locations=preferences.preferred_locations,
        willing_to_relocate=preferences.willing_to_relocate,
        us_citizen=preferences.us_citizen,
    )

    collector = RemotiveCollector()

    pipeline = JobPipeline(
        collector=collector,
        candidate=candidate,
    )

    pipeline.run()


if __name__ == "__main__":
    main()