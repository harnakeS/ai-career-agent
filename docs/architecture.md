# Architecture

## Overview

AI Career Agent is a modular job discovery, filtering, and recommendation system.

The application currently:

1. Collects live job postings from external sources.
2. Converts each posting into a standardized `JobPosting` model.
3. Applies deterministic eligibility filters.
4. Scores qualifying jobs against a structured candidate profile.
5. Stores new jobs in a SQLite database.
6. Updates previously seen jobs without creating duplicates.
7. Persists match scores for later ranking and analysis.

The long-term goal is to support multiple company career platforms, semantic resume-to-job matching, LLM-based recommendations, automated alerts, and an application-tracking dashboard.

---

## Current Data Flow

Job Source
    ↓
Job Collector
    ↓
JobPosting Model
    ↓
Job Processing Pipeline
    ↓
Eligibility Filters
    ↓
Deterministic Rule Matcher
    ↓
Job Repository
    ↓
SQLite Database

The processing pipeline coordinates the workflow. Individual components remain separate so that collectors, matching methods, databases, and notification systems can be replaced or expanded independently.

---

## Project Structure

app/
├── collectors/
│   ├── base.py
│   └── remotive.py
│
├── config/
│   └── candidate.py
│
├── database/
│   ├── database.py
│   ├── models.py
│   └── repository.py
│
├── matching/
│   └── rule_matcher.py
│
├── models/
│   ├── candidate.py
│   └── job.py
│
├── pipeline/
│   └── job_pipeline.py
│
├── processing/
│   └── filters.py
│
└── main.py

Additional folders include:

tests/       Unit tests
data/        Local SQLite database
docs/        Architecture and development documentation
logs/        Future application logs

---

## Main Components

### Collectors

Collectors retrieve job postings from external APIs or career sites.

Every collector implements the shared `JobCollector` interface:

class JobCollector(ABC):
    @abstractmethod
    def collect_jobs(self) -> list[JobPosting]:
        ...

This gives every source the same contract, regardless of whether the data comes from:

- A public API
- Greenhouse
- Lever
- Workday
- Ashby
- SmartRecruiters
- A custom company career site

Collectors are only responsible for retrieving and normalizing job data.

They do not:

- Save jobs
- Score jobs
- Apply candidate-specific recommendations
- Send notifications
- Track application status

#### Current Collector

- Remotive public jobs API

#### Planned Collectors

- Greenhouse
- Lever
- Workday
- Ashby
- SmartRecruiters
- Company-specific custom collectors

---

### JobPosting Model

The `JobPosting` Pydantic model provides a standardized representation of a job collected from any source.

It currently includes:

- Company
- Requisition ID
- Job title
- Location
- Description
- Application URL
- Posting date
- Discovery timestamp

Pydantic validates incoming data before it enters the processing pipeline.

This prevents malformed or incomplete external data from reaching the database and matching layers.

---

### CandidateProfile Model

The `CandidateProfile` model stores the structured candidate information used for job matching.

It currently includes:

- Education
- Graduation year
- Years of experience
- Programming languages
- Technical skills
- Frameworks and libraries
- Tools
- Certifications
- Preferred locations
- Relocation preference
- Work authorization
- Desired job types

The current profile is defined manually in configuration.

A future version will generate candidate profiles automatically from uploaded resumes and support multiple resume variants.

---

### Job Processing Pipeline

The `JobPipeline` coordinates the application workflow.

Its current responsibilities are:

1. Retrieve jobs from a collector.
2. Apply eligibility filters.
3. Score qualifying jobs using the deterministic matcher.
4. Save new jobs.
5. Update existing jobs.
6. Persist match scores.
7. Print a summary of the processing run.

The pipeline keeps orchestration logic out of `main.py`.

The entry point only creates the required components and starts the pipeline.

Current pipeline summary fields include:

- Collected jobs
- Scored jobs
- New jobs
- Updated jobs
- Skipped jobs

Future pipeline responsibilities will include:

- Semantic embedding similarity
- LLM evaluation
- Notification thresholds
- Closed-job detection
- Multi-collector execution
- Error handling and retries
- Structured logging

---

### Eligibility Filters

The eligibility layer removes clearly unsuitable jobs before more expensive matching is performed.

Current filters detect:

- Senior-level titles
- Roles requesting excessive minimum experience

Examples of excluded seniority terms include:

- Senior
- Staff
- Principal
- Director
- Vice President
- Manager
- Architect
- Lead Engineer

The experience parser uses regular expressions to identify phrases such as:

- `5+ years of experience`
- `at least 5 years`
- `minimum of 5 years`

Jobs that pass the eligibility layer continue to candidate-specific scoring.

This reduces unnecessary processing and will later reduce embedding and LLM costs.

---

### Matching

The current matching engine uses deterministic rules to estimate how well a job aligns with the candidate profile.

Current scoring considers:

- Technical skill overlap
- Desired-role alignment
- Preferred-location alignment
- Relocation flexibility
- Early-career language

The matcher returns a structured `MatchResult` containing:

- Overall score
- Technical score
- Role-alignment score
- Location score
- Early-career score
- Matched skills
- Matched role categories
- Location-match status
- Human-readable reasons

The matcher uses complete-term matching rather than simple substring matching.

For example:

- `C` matches an explicit reference to the C programming language.
- `C` does not match the letter inside a word such as `applications`.

The current deterministic system is intentionally conservative. It serves as an explainable baseline before semantic embeddings and LLM reasoning are introduced.

The deterministic matcher is divided into reusable category-scoring components:

- Technical skill alignment
- Desired-role alignment
- Location alignment
- Early-career alignment

Each component returns an independent score and explanation. The main rule matcher combines these category results into the overall score.

This structure allows future categories, such as education, experience, certification, and work authorization, to be added without turning the main matching function into a single large scoring method.

#### Planned Hybrid Matching Architecture

Deterministic Rules
        ↓
Semantic Embedding Similarity
        ↓
LLM Evaluation
        ↓
Final Recommendation

The future matching system will combine:

- Hard eligibility requirements
- Category-weighted scoring
- Semantic similarity
- Evidence-grounded LLM reasoning
- Confidence values
- Apply, Consider, or Skip recommendations

---

### Database

SQLite is currently used for local development.

The database file is stored at:

data/jobs.db

The `jobs` table currently stores:

- Internal database ID
- Company
- Requisition ID
- Job title
- Location
- Full description
- Application URL
- Date posted
- Date discovered
- Last-seen timestamp
- Active status
- Alert status
- Match score
- Application status

The combination of `company` and `requisition_id` is unique.

This prevents duplicate records when the same posting appears in repeated collection runs.

A future production version may migrate to PostgreSQL and pgvector.

---

### Repository

The `JobRepository` separates persistence logic from the rest of the application.

It currently supports:

- Looking up jobs by company and requisition ID
- Inserting newly discovered jobs
- Updating previously seen jobs
- Refreshing last-seen timestamps
- Reactivating jobs that reappear
- Preventing duplicate database rows

The repository returns whether a job was newly created or updated.

This lets the pipeline track new and existing jobs without containing SQLAlchemy-specific query logic.

Future repository methods may include:

- Retrieve unscored jobs
- Retrieve high-match jobs
- Mark alerts as sent
- Update application status
- Mark missing jobs inactive
- Retrieve jobs by company, score, location, or date

---

### Application Entry Point

`app/main.py` is intentionally small.

Its responsibilities are:

1. Initialize the database.
2. Create the collector.
3. Create the processing pipeline.
4. Run the pipeline.

It does not contain collection, filtering, matching, or persistence logic.

This keeps the application entry point easy to understand and prevents it from becoming tightly coupled to implementation details.

---

## Testing

The project currently uses `pytest`.

Existing tests cover:

- Senior-title filtering
- Experience-requirement extraction
- Entry-level eligibility
- Rejection of high-experience roles
- Complete-term technology matching
- Prevention of false-positive `C` matches
- Multiword role matching
- High-scoring relevant jobs
- Low-scoring unrelated jobs

Tests are added before major features are integrated into the live pipeline.

Planned test coverage includes:

- Repository insert and update behavior
- Database constraints
- Collector response parsing
- Closed-job detection
- Multi-collector execution
- Embedding scoring
- LLM output validation
- Notification deduplication

---

## Current Limitations

The current version has several known limitations:

- It only supports one live job source.
- The candidate profile is hardcoded.
- Job scoring relies on exact term matching.
- Only jobs that pass eligibility filtering receive match scores.
- Jobs that are skipped do not yet store an eligibility reason.
- The application does not yet detect closed postings.
- There are no alerts or dashboard.
- Match scores are not yet category weighted.
- Semantic similarity is not yet implemented.
- LLM-based recommendations are not yet implemented.

These limitations are intentional for the current development phase. The deterministic implementation provides a stable baseline for future AI evaluation.

---

## Planned Architecture

Multiple Company Career Sites
            ↓
ATS-Specific Collectors
            ↓
Standardized JobPosting Objects
            ↓
Normalization and Validation
            ↓
Eligibility Filters
            ↓
Deterministic Category Scoring
            ↓
Semantic Embedding Similarity
            ↓
LLM Evidence-Based Evaluation
            ↓
Final Match Score and Recommendation
            ↓
PostgreSQL and Vector Storage
            ↓
Email Alerts and Streamlit Dashboard

---

## Future Deployment Architecture

The planned production deployment may use:

Scheduled Azure Function
        ↓
Job Collection Pipeline
        ↓
PostgreSQL + pgvector
        ↓
Embedding and LLM Services
        ↓
Notification Service
        ↓
Streamlit or Web Dashboard

Potential Azure services include:

- Azure Functions for scheduled collection
- Azure Database for PostgreSQL
- Azure Container Apps for the dashboard
- Azure Key Vault for secret management
- Application Insights for logging and monitoring

The local SQLite implementation will remain available for development and testing.