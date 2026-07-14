from app.collectors.base import JobCollector
from app.database.database import SessionLocal
from app.database.repository import JobRepository
from app.processing.filters import is_potential_match


class JobPipeline:
    """Coordinates the job collection process."""

    def __init__(self, collector: JobCollector):
        self.collector = collector

    def run(self) -> None:
        jobs = self.collector.collect_jobs()

        new_jobs = 0
        updated_jobs = 0
        skipped_jobs = 0

        with SessionLocal() as session:
            repository = JobRepository(session)

            for job in jobs:

                should_continue, reason = is_potential_match(job)

                if not should_continue:
                    skipped_jobs += 1
                    continue

                _, created = repository.save_or_update(job)

                if created:
                    new_jobs += 1
                else:
                    updated_jobs += 1

        print()
        print("Pipeline Summary")
        print("----------------")
        print(f"Collected : {len(jobs)}")
        print(f"New       : {new_jobs}")
        print(f"Updated   : {updated_jobs}")
        print(f"Skipped   : {skipped_jobs}")