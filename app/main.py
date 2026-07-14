from app.collectors.remotive import RemotiveCollector


def main() -> None:
    collector = RemotiveCollector()
    jobs = collector.collect_jobs()

    print(f"Collected {len(jobs)} jobs.")

    for job in jobs[:5]:
        print(
            f"{job.company} | "
            f"{job.title} | "
            f"{job.location} | "
            f"{job.application_url}"
        )


if __name__ == "__main__":
    main()