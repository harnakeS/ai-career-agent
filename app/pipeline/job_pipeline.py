from app.collectors.base import JobCollector
from app.config.candidate import candidate
from app.database.database import SessionLocal
from app.database.repository import JobRepository
from app.matching.rule_matcher import calculate_rule_match
from app.processing.filters import is_potential_match


class JobPipeline:
    """Coordinates job collection, filtering, scoring, and storage."""

    def __init__(self, collector: JobCollector) -> None:
        self.collector = collector

    def run(self) -> None:
        jobs = self.collector.collect_jobs()

        new_jobs = 0
        updated_jobs = 0
        skipped_jobs = 0
        scored_jobs = 0

        with SessionLocal() as session:
            repository = JobRepository(session)

            for job in jobs:
                should_continue, _ = is_potential_match(job)

                if not should_continue:
                    skipped_jobs += 1
                    continue

                match_result = calculate_rule_match(candidate, job)

                record, created = repository.save_or_update(job)
                record.match_score = match_result.score

                session.commit()
                session.refresh(record)

                scored_jobs += 1

                if created:
                    new_jobs += 1
                else:
                    updated_jobs += 1

        print()
        print("Pipeline Summary")
        print("----------------")
        print(f"Collected : {len(jobs)}")
        print(f"Scored    : {scored_jobs}")
        print(f"New       : {new_jobs}")
        print(f"Updated   : {updated_jobs}")
        print(f"Skipped   : {skipped_jobs}")