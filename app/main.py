from app.collectors.remotive import RemotiveCollector
from app.database.database import SessionLocal, create_database
from app.database.repository import JobRepository


def main() -> None:
    create_database()

    collector = RemotiveCollector()
    jobs = collector.collect_jobs()

    new_jobs = 0
    updated_jobs = 0

    with SessionLocal() as session:
        repository = JobRepository(session)

        for job in jobs:
            _, was_created = repository.save_or_update(job)

            if was_created:
                new_jobs += 1
            else:
                updated_jobs += 1

    print(f"Collected {len(jobs)} jobs.")
    print(f"New jobs: {new_jobs}")
    print(f"Updated jobs: {updated_jobs}")


if __name__ == "__main__":
    main()