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