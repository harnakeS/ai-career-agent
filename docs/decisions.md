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