# Architecture Decisions

## ADR-001: Use Python

**Status:** Accepted

### Decision

Use Python as the primary programming language.

### Reason

Python provides strong support for:

- Web requests and scraping
- Data processing
- Machine learning
- LLM integrations
- Database access
- Rapid prototyping

It also aligns with the project's future AI-engineering goals.

---

## ADR-002: Use a Standardized Job Model

**Status:** Accepted

### Decision

Convert every collected job into a shared `JobPosting` model.

### Reason

Career sites return inconsistent data formats. A shared model allows the database, filtering, matching, notification, and dashboard layers to work independently of the original source.

---

## ADR-003: Use a Collector Interface

**Status:** Accepted

### Decision

Require every job collector to implement the `JobCollector` interface.

### Reason

This provides a consistent contract for Workday, Greenhouse, Lever, custom websites, and public APIs.

It also makes collectors interchangeable and easier to test.

---

## ADR-004: Use SQLite for the Initial Version

**Status:** Accepted

### Decision

Use SQLite during early development.

### Reason

SQLite requires no external server, is easy to inspect locally, and is sufficient for the initial ten-company version.

A future production version may migrate to PostgreSQL.

---

## ADR-005: Use a Repository Layer

**Status:** Accepted

### Decision

Place database access inside `JobRepository`.

### Reason

This keeps SQLAlchemy logic out of collectors, processing code, and the application entry point.

It also makes future database changes easier.

---

## ADR-006: Use Company and Requisition ID for Deduplication

**Status:** Accepted

### Decision

Treat the combination of company and requisition ID as unique.

### Reason

Requisition IDs are usually stable identifiers within a company. Combining them with the company prevents collisions across employers.

---

## ADR-007: Apply Deterministic Filters Before AI Scoring

**Status:** Accepted

### Decision

Use rule-based filters to remove clearly unsuitable jobs before using embeddings or an LLM.

### Reason

Deterministic filters are faster, cheaper, and easier to explain.

They reduce unnecessary AI calls for roles that are clearly too senior or require excessive experience.

---

## ADR-008: Keep Collectors Separate from Processing and Storage

**Status:** Accepted

### Decision

Collectors only retrieve and normalize job data.

They do not:

- Save jobs
- Score jobs
- Send notifications
- Apply application-status logic

### Reason

This separation of concerns makes each component easier to test, replace, and maintain.


## ADR-009: Use a Deterministic Matching Baseline

**Status:** Accepted

### Decision

Implement a deterministic rule-based matching engine before introducing embeddings or LLM reasoning.

### Reason

A deterministic baseline provides:

- Explainable recommendations
- Low-cost evaluation
- Fast execution
- A benchmark for future AI models

Semantic embeddings and LLM evaluation will be layered on top of this baseline rather than replacing it.

---

## ADR-010: Separate Matching Categories into Independent Components

**Status:** Accepted

### Decision

Implement technical, role, location, and early-career scoring as independent components coordinated by the main rule matcher.

### Reason

Separating the scoring categories:

- Keeps the main matching function small
- Makes individual scoring rules easier to test
- Allows categories to evolve independently
- Simplifies adding education, experience, certification, and AI-based scores later
- Produces more explainable recommendation results

### Alternatives Considered

Keeping all scoring logic inside one function was simpler initially, but it would become difficult to maintain as additional matching categories were introduced.

---

## ADR-011: Prioritize a Personal-Use MVP Before SaaS Features

**Status:** Accepted

### Decision

Build and validate the application as a reliable single-user job recommendation tool before introducing multi-user or commercial SaaS functionality.

### Reason

The immediate objectives are to:

- Use the application during an active job search
- Validate the quality of its recommendations
- Build a complete portfolio-ready project
- Avoid delaying core functionality with premature infrastructure

### Deferred Work

The following features are intentionally postponed:

- Authentication
- Multi-user data isolation
- Subscription billing
- Usage-based pricing
- Enterprise-scale infrastructure
- Production frontend development

---

## ADR-012: Use Deterministic Resume Parsing Before LLM Extraction

**Status:** Accepted

### Decision

Implement the initial resume parser using PDF text extraction, section headings, and deterministic parsing rules before introducing LLM-based extraction.

### Reason

A deterministic parser provides:

- Predictable behavior
- Low execution cost
- Fast local processing
- Easy unit testing
- A clear baseline for future AI-assisted extraction

The current resume format contains consistent headings and structured skill categories, making deterministic parsing appropriate for the first version.

### Alternatives Considered

Using an LLM for the entire extraction process would support more resume formats, but it would introduce additional cost, latency, nondeterminism, and validation requirements before the core workflow is proven.

---

## ADR-015: Generate the Candidate Profile from Parsed Resume Data

**Status:** Accepted

### Decision

Build the active `CandidateProfile` from the structured `ParsedResume` rather than maintaining candidate skills, education, and experience in Python configuration.

### Reason

Using the resume as the source of truth:

- Eliminates duplicated candidate data
- Prevents profile information from becoming inconsistent with the resume
- Allows updated resumes to affect job matching without source-code changes
- Creates the foundation for resume uploads and multiple resume versions
- Makes the matching workflow more representative of the intended product

User preferences that cannot be safely inferred, such as preferred locations, relocation willingness, and work authorization, remain explicitly configured.

### Alternatives Considered

Keeping a fully hardcoded candidate profile was simpler during early matching development, but it required manual maintenance and prevented the uploaded resume from driving recommendations.

---

## ADR-016: Track Experience by Employment Type and Duration

**Status:** Accepted

### Decision

Represent experience as separate month totals for full-time, internship, co-op, part-time, and contract work.

### Reason

A single `years_experience` value would overstate candidates whose experience consists primarily of internships or short-term roles.

Separating experience categories allows the matching engine to distinguish between:

- Full-time professional experience
- Internship experience
- Co-op experience
- Part-time experience
- Contract experience

This produces more accurate eligibility and seniority judgments.

---

## ADR-015: Generate Candidate Profiles from Parsed Resume Data

**Status:** Accepted

### Decision

Generate the active `CandidateProfile` from a structured `ParsedResume` rather than maintaining resume-derived candidate information in Python configuration.

### Reason

Using the resume as the source of truth:

- Eliminates duplicated candidate data
- Reduces the risk of the profile becoming inconsistent with the resume
- Allows resume updates to change job matching without code changes
- Creates a foundation for resume uploads and multiple resume versions
- Makes the live pipeline reflect the intended product workflow

### Alternatives Considered

Maintaining a hardcoded profile was simpler during early matching development, but it required manual updates and prevented the uploaded resume from driving recommendations.

---

## ADR-016: Track Experience by Employment Type and Duration

**Status:** Accepted

### Decision

Track experience separately in months for:

- Full-time employment
- Internships
- Co-ops
- Part-time employment
- Contract work

### Reason

A single years-of-experience field can overstate candidates whose relevant experience consists of internships or short-term roles.

Separating employment categories allows the matching engine to make more accurate entry-level and seniority judgments.

### Alternatives Considered

A single `years_experience` field was simpler but discarded important context and incorrectly represented internship experience as equivalent to full-time employment.

---

## ADR-017: Separate Resume-Derived Facts from Candidate Preferences

**Status:** Accepted

### Decision

Store resume-derived facts in `CandidateProfile` while loading non-resume preferences from `config/preferences.json`.

### Reason

The resume can provide skills, education, certifications, projects, and experience, but it cannot reliably determine:

- Preferred locations
- Willingness to relocate
- Citizenship or work authorization

Keeping these values separate:

- Avoids unsupported inference
- Allows preference changes without editing source code
- Prepares the application for a future settings interface
- Keeps candidate generation deterministic and transparent

### Alternatives Considered

Hardcoding preferences in `main.py` worked temporarily but mixed application configuration with orchestration logic.

---

## Use LLM-Based Requirement Extraction

### Decision

Use a language model to extract skills and other requirements dynamically from job descriptions instead of relying on a fixed, manually maintained skill vocabulary.

### Rationale

A fixed vocabulary would require continuous updates and could fail to recognize new, niche, or uncommon technologies. An LLM can interpret arbitrary job descriptions and return structured requirements without limiting extraction to a predefined list.

The LLM will only extract and classify requirements. Deterministic application code will continue to handle validation, deduplication, evidence matching, weighting, and final score calculation.

### Consequences

- The extractor can support technologies not previously known to the application.
- LLM outputs must be validated through Pydantic schemas.
- Extraction should remain provider-independent.
- Tests should rely on mocked structured outputs rather than live API calls.
- A lightweight normalization layer may still be added later for aliases and duplicates.