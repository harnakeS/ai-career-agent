from app.composition import (
    create_selected_company_pipeline,
)
from app.config.company_sources import (
    load_company_sources,
)
from app.database.database import create_database
from app.pipeline.selected_company_pipeline import (
    SelectedCompanyRunResult,
)


COMPANY_SOURCES_PATH = "config/company_sources.json"


def print_run_summary(
    result: SelectedCompanyRunResult,
) -> None:
    print()
    print("Selected Company Pipeline")
    print("-------------------------")
    print(
        f"Successful collections : "
        f"{result.successful_collections}"
    )
    print(
        f"Skipped sources        : "
        f"{result.skipped_sources}"
    )
    print(
        f"Collection failures    : "
        f"{result.collection_failures}"
    )
    print(
        f"Collected jobs         : "
        f"{result.collected_jobs}"
    )
    print(
        f"New jobs               : "
        f"{result.new_jobs}"
    )
    print(
        f"Updated jobs           : "
        f"{result.updated_jobs}"
    )
    print(
        f"Persistence failures   : "
        f"{result.persistence_failures}"
    )


def print_failures(
    result: SelectedCompanyRunResult,
) -> None:
    for failure in result.collection.failures:
        print()
        print("Collection Failure")
        print("------------------")
        print(f"Company    : {failure.company_name}")
        print(f"Provider   : {failure.provider.value}")
        print(f"Error type : {failure.error_type}")
        print(f"Message    : {failure.message}")

    for failure in result.persistence.failures:
        print()
        print("Persistence Failure")
        print("-------------------")
        print(
            f"Company    : "
            f"{failure.source.company_name}"
        )
        print(
            f"Provider   : "
            f"{failure.source.provider.value}"
        )
        print(f"Error type : {failure.error_type}")
        print(f"Message    : {failure.message}")


def main() -> None:
    create_database()

    configuration = load_company_sources(
        COMPANY_SOURCES_PATH
    )
    pipeline = create_selected_company_pipeline()

    result = pipeline.run(
        configuration.sources
    )

    print_run_summary(result)
    print_failures(result)

    if (
        result.collection_failures > 0
        or result.persistence_failures > 0
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()