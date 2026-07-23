# AI Job Scout

AI Job Scout monitors selected company career sites, stores active job postings, and provides evidence-based candidate-to-job analysis through a hybrid deterministic and AI-assisted matching pipeline.

## Current Status

The application currently supports:

- Resume parsing into structured candidate data
- Resume-derived candidate evidence
- Explicit user-provided search preferences
- Structured job-requirement extraction
- OpenAI and local Ollama provider configuration
- Qualification-focused job-description extraction
- Deterministic and vocabulary-aware evidence matching
- Requirement alternatives
- Education-equivalency matching
- Experience-duration matching
- Explicit résumé-to-description overlap detection
- Separate required-gap and preferred-qualification reporting
- Explainable supporting evidence
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
- Selectable job-detail views
- Readable Markdown-formatted job descriptions
- In-memory PDF resume uploads
- Session-based candidate profiles
- Personalized candidate-to-job analysis
- Persistent AI-extracted requirement caching
- Visible cache-source status for personalized analysis
- Deterministic weighted requirement-coverage scoring

The current selected-company configuration monitors Datadog as the first live Greenhouse integration. The architecture is designed to expand to ten selected companies through reusable ATS providers.

The automated test suite currently contains 352 passing tests.

## Local Setup

Use standalone CPython 3.12. The project’s pinned package versions avoid a native-library conflict encountered when Streamlit was run through an Anaconda-based environment on macOS.

Create and activate the environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt