# AI Job Scout

AI Job Scout monitors selected company career sites, stores active job postings, and provides a foundation for evidence-based job matching, application tracking, resume tailoring, and cover-letter generation.

## Current Status

The application currently supports:

- Resume parsing into structured candidate data
- Structured job-requirement extraction
- Deterministic and vocabulary-aware evidence matching
- Selected-company configuration
- Greenhouse job collection
- Job normalization and validation
- SQLite persistence and duplicate prevention
- Active and inactive posting reconciliation
- Transactional per-company updates
- A Streamlit dashboard
- Manual selected-company scans
- Job search and company filtering
- Active and inactive job visibility
- Direct links to official job postings

The current selected-company configuration monitors Datadog as the first live Greenhouse integration. The architecture is designed to expand to ten selected companies through reusable ATS providers.

The automated test suite currently contains 265 passing tests.

## Local Setup

Use standalone CPython 3.12. The project’s pinned package versions avoid a native-library conflict encountered when Streamlit was run through an Anaconda-based environment on macOS.

Create and activate the environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate