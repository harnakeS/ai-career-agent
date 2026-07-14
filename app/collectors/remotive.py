import requests

from app.collectors.base import JobCollector
from app.models.job import JobPosting
from datetime import datetime


class RemotiveCollector(JobCollector):
    """Collect software jobs from the Remotive public jobs API."""

    API_URL = "https://remotive.com/api/remote-jobs"

    def collect_jobs(self) -> list[JobPosting]:
        response = requests.get(
            self.API_URL,
            params={"category": "software-dev"},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        jobs: list[JobPosting] = []

        for item in data.get("jobs", []):
            jobs.append(
                JobPosting(
                    company=item["company_name"],
                    requisition_id=str(item["id"]),
                    title=item["title"],
                    location=item.get("candidate_required_location"),
                    description=item["description"],
                    application_url=item["url"],
                    date_posted=(
                                datetime.fromisoformat(item["publication_date"]).date()
                                if item.get("publication_date")
                                else None
                            ),
                )
            )

        return jobs