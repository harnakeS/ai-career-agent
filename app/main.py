from app.collectors.remotive import RemotiveCollector
from app.database.database import create_database
from app.pipeline.job_pipeline import JobPipeline


def main() -> None:
    create_database()

    collector = RemotiveCollector()
    pipeline = JobPipeline(collector)

    pipeline.run()


if __name__ == "__main__":
    main()