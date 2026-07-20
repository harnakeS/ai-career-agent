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

Selected-company monitoring is being developed through a separate provider-neutral source layer:

CompanySource
    ↓
Provider-Specific JobSource
    ↓
RawJobPosting
    ↓
Canonical Job Conversion
    ↓
Existing Processing Pipeline

The Greenhouse implementation currently reaches the `RawJobPosting` stage. Canonical conversion and pipeline integration are the next steps.

---

## Project Structure

app/
├── collectors/
│   ├── base.py
│   └── remotive.py
│
├── job_sources/
│   ├── errors.py
│   ├── greenhouse.py
│   ├── http.py
│   ├── models.py
│   └── protocol.py
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
|
├── parsing/
│   ├── candidate_builder.py
│   ├── education_parser.py
│   ├── experience_parser.py
│   ├── pdf_parser.py
│   ├── project_parser.py
│   ├── resume_parser.py
│   ├── section_parser.py
│   └── skills_parser.py
│
├── pipeline/
│   └── job_pipeline.py
│
├── processing/
│   └── filters.py
|
├── resume/
│   ├── pdf_parser.py
│   ├── section_parser.py
│   ├── skills_parser.py
│   └── resume_parser.py
│
└── main.py

Additional folders include:

tests/       Unit tests
data/        Local SQLite database
docs/        Architecture and development documentation
logs/        Future application logs
scripts/      Manual integration and development checks

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

#### Current Integrations

- Remotive public jobs API
- Greenhouse public Job Board API

The Remotive collector returns canonical `JobPosting` objects and is integrated with the existing processing pipeline.

The Greenhouse source returns provider-neutral `RawJobPosting` objects. It has been verified against a live public job board but is not yet connected to canonical job conversion or persistence.

#### Planned Integrations

- Lever
- Workday
- Ashby
- SmartRecruiters
- Company-specific custom sources

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

## Candidate Profile Generation

The active `CandidateProfile` is generated from the parsed resume rather than maintained manually in Python code.

Resume-derived fields include:

- Candidate name
- Degree
- Major and minor
- Graduation year
- Programming languages
- Frameworks and libraries
- Tools and technologies
- Concepts
- Certifications
- Licenses
- Schedule
- Clearances
- Authorization
- Languages
- Full-time experience months
- Internship experience months
- Co-op experience months
- Part-time experience months
- Contract experience months
- Inferred desired roles

User preferences that cannot be safely inferred from a resume are loaded from a separate JSON configuration file.

These include:

- Preferred locations
- Willingness to relocate
- U.S. citizenship and work authorization

### Runtime Flow

Resume PDF
    ↓
PDF Text Extraction
    ↓
Text Normalization
    ↓
Section Parsers
    ↓
ParsedResume
    ↓
CandidateProfile Builder
    ↓
Resume-Derived Candidate Data
            +
Candidate Preferences JSON
    ↓
CandidateProfile
    ↓
JobPipeline
    ↓
Matching Engine

---

### Resume Parsing

The resume parsing layer converts a PDF resume into structured data that can later be used to build a `CandidateProfile`.

The current parsing workflow is:

Resume PDF
    ↓
PDF Text Extraction
    ↓
Text Normalization
    ↓
Section Parsing
    ↓
Skills Parsing
    ↓
ParsedResume

---

### Candidate Profile Builder

The candidate-profile builder transforms a `ParsedResume` into the normalized `CandidateProfile` consumed by the matching engine.

It currently:

- Extracts the candidate's name from the resume header
- Maps structured education and skills into candidate fields
- Separately aggregates internship, full-time, co-op, part-time, and contract experience
- Infers reasonable target roles from skills, certifications, and project technologies
- Combines resume-derived data with user-provided preferences

Current runtime flow:

Resume PDF
    ↓
ParsedResume
    ↓
CandidateProfile Builder
    ↓
CandidateProfile
    ↓
JobPipeline
    ↓
Rule Matcher

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

Test Count: 203

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
- PDF validation and missing-file handling
- Resume text cleanup
- Section extraction
- Skills-category extraction
- End-to-end resume parsing orchestration
- Candidate-name extraction
- Experience aggregation by employment type
- Target-role inference
- Candidate-profile generation
- Resume-generated profile integration with the job pipeline
- Candidate-name extraction
- Experience aggregation by employment type
- Target-role inference
- Candidate-profile generation
- Candidate-preferences validation
- Missing and malformed preference-file handling
- Resume-generated profile integration with the job pipeline
- Dynamic vocabulary resolution
- Vocabulary alias-conflict detection
- Vocabulary-aware evidence matching
- Experience-duration evidence matching
- Job-source model validation
- Job-source protocol conformance
- Greenhouse payload conversion
- Disabled and incompatible source handling
- Greenhouse payload-error handling

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

- The existing processing pipeline currently uses only the Remotive collector.
- The Greenhouse source has been verified independently but is not yet connected to canonical job conversion, persistence, or matching.
- Location, relocation, and work-authorization preferences are still supplied in `main.py`.
- Target-role inference currently uses deterministic keyword rules.
- The original rule matcher still relies primarily on exact term matching.
- The new evidence matcher supports canonical vocabulary resolution but is not yet integrated into final job scoring.
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

---

## Job Requirements Extraction

Job descriptions are converted into structured requirements before matching.

JobPosting
    ↓
LLM Requirement Extractor
    ↓
ExtractedJobRequirements
    ↓
Validation and Normalization
    ↓
JobRequirements
    ↓
Requirement Evidence Matcher

- [x] Define structured requirement models
- [x] Add requirement importance classification
- [x] Add real job-description fixtures
- [x] Define validated LLM extraction schema
- [ ] Create provider-independent LLM extractor interface
- [ ] Implement first LLM provider adapter
- [ ] Convert extracted output into `JobRequirements`
- [ ] Add deduplication and normalization
- [ ] Match requirements against candidate evidence
- [ ] Integrate requirement-based scoring into the pipeline

---

## Requirement Extraction Pipeline

Job descriptions are converted into structured requirements through a provider-independent extraction pipeline:

1. `RequirementsExtractor` extracts structured requirement data.
2. The extracted output is validated using `ExtractedJobRequirements`.
3. `RequirementConverter` converts the validated output into the canonical `JobRequirements` model.
4. Deterministic normalization fills or corrects structured metadata when possible.

The LLM is responsible for semantic interpretation and identifying requirements. Deterministic application code is responsible for validation, deduplication, normalization, and scoring.

### Experience Duration Normalization

The extraction pipeline does not rely solely on the LLM to populate `minimum_experience_months`.

When the LLM leaves this field empty, the converter examines extracted experience requirements and converts durations into months.

Examples:

- `1 year` → `12`
- `1.5 years` → `18`
- `2 years` → `24`
- `6 months` → `6`
- `one year` → `12`

An explicit value returned by the extractor takes priority over the deterministic fallback.

---

## Dynamic Vocabulary and Requirement Normalization

Job postings and resumes may describe the same concept using different wording.

Examples include:

- `JS` and `JavaScript`
- `AWS` and `Amazon Web Services`
- `Bachelor of Arts` and `Bachelor's Degree`
- `K8s` and `Kubernetes`

The system separates generic text normalization from domain-specific concept resolution.

Raw Requirement or Evidence Value
        ↓
Generic Text Normalization
        ↓
Category-Aware Vocabulary Repository
        ↓
Canonical Concept
        ↓
Evidence Matching


The vocabulary repository resolves aliases within a specific category.

This prevents ambiguous aliases from matching across unrelated domains. For example, `BA` may represent either `Bachelor of Arts` or `Business Analyst`, depending on the vocabulary category.

The `RequirementNormalizer` performs generic text cleanup before requesting canonical concept resolution from the repository.

The normalizer contains no hardcoded technology, education, certification, or role aliases.

---

## Vocabulary-Aware Evidence Matching

The `EvidenceMatcher` compares structured job requirements with structured candidate evidence.

Job Requirement
    ↓
Category-Aware Normalization
    ↓
Canonical Vocabulary Concept
    ↓
Compatible Candidate Evidence
    ↓
RequirementMatch

The matcher:

- Selects candidate evidence from the compatible category
- Supports normalized direct-value matches
- Supports vocabulary-resolved alias matches
- Preserves category isolation
- Returns the evidence supporting each match
- Produces human-readable match reasons
- Reports unsupported requirement categories explicitly

Duration-based experience requirements are converted into months and compared deterministically.

Experience Requirement
    ↓
Required Months
            +
Candidate Experience Evidence
    ↓
Available Months
    ↓
RequirementMatch

Explicit duration evidence is currently combined when evaluating total experience.

The matcher does not yet detect overlapping employment periods, duplicated timeline evidence, or concurrent positions. Date-aware experience aggregation will be introduced later.

---

## Selected-Company Job Sources

The selected-company source layer provides a common interface for retrieving jobs from different recruiting platforms.

A `CompanySource` contains:

- Company name
- Source provider
- Provider-specific source identifier
- Public careers URL
- Enabled status

Every provider implementation satisfies the `JobSource` protocol:

collect(source: CompanySource) -> list[RawJobPosting]

This lets future collection workflows use Greenhouse, Lever, Workday, and other providers without depending on their internal response formats.

### HTTP Boundary

Network access is separated from provider conversion through the `JsonHttpClient` protocol.

The production `UrllibJsonHttpClient`:

- Requests JSON over HTTP
- Applies a request timeout
- Supplies explicit request headers
- Validates that the response is a JSON object
- Converts transport failures into job-source exceptions
- Converts invalid JSON into job-source payload errors

Provider tests inject a deterministic HTTP stub instead of making live network requests.

### Greenhouse Job Source

The `GreenhouseJobSource` uses a configured Greenhouse board token to retrieve published jobs from the public Greenhouse Job Board API.

CompanySource
    ↓
Greenhouse Board Token
    ↓
Greenhouse Job Board API
    ↓
Payload Validation
    ↓
RawJobPosting Objects

The source:

- Skips disabled company configurations
- Rejects configurations for incompatible providers
- Requests complete job-description content
- Validates required provider fields
- Preserves the official application URL
- Converts provider failures into job-source domain errors

The integration was manually verified against Datadog's public Greenhouse board and collected 415 published postings.

Greenhouse currently supplies `updated_at` through the job-list endpoint. This value is temporarily stored in `RawJobPosting.posted_at`. Canonical job conversion will later distinguish publication, update, discovery, and collection timestamps.