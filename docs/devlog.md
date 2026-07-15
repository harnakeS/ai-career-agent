# Development Log

---

## 2026-07-14

### Milestone

Established the core backend architecture for the AI Career Agent.

### Features Implemented

- Created a standardized `JobPosting` model using Pydantic.
- Implemented a reusable `JobCollector` interface for future ATS integrations.
- Built the first live collector using the Remotive Jobs API.
- Designed the initial SQLite database schema with SQLAlchemy.
- Implemented the repository pattern for database access.
- Added duplicate detection using the combination of company and requisition ID.
- Built the initial job processing pipeline.
- Implemented deterministic eligibility filters.
- Added unit tests for the filtering layer.
- Created the initial `CandidateProfile` model.
- Built the first version of the deterministic rule-based matcher.

### Architecture Decisions

- Separated data collection from persistence using a repository layer.
- Standardized all job postings into a common model regardless of source.
- Introduced a processing pipeline to coordinate collection, filtering, and storage.
- Chose SQLite for rapid local development.
- Began designing the matching system as a hybrid architecture consisting of:
  - Rule-based filtering
  - Semantic embeddings (planned)
  - LLM reasoning (planned)

### Challenges

- Learned how to normalize external job data into a consistent schema.
- Fixed date parsing issues caused by API timestamps.
- Fixed false-positive skill matching caused by substring comparisons (e.g., matching "C" inside other words).
- Established unit testing early to reduce future regressions.

### Next Milestones

- Improve deterministic matching with category weighting.
- Integrate the rule matcher into the processing pipeline.
- Begin semantic embedding-based similarity scoring.
- Support additional ATS platforms.


## 2026-07-14 (Continued)

### Implemented

- Added the initial candidate profile.
- Built the first deterministic job matcher.
- Integrated match scoring into the processing pipeline.
- Stored match scores in SQLite.

### Lessons Learned

- Simple keyword matching produces conservative scores.
- False-positive substring matching required more robust token matching.
- A deterministic baseline will provide a useful benchmark before adding embeddings and LLM reasoning.

### Next

- Improve rule weighting.
- Introduce semantic embeddings.
- Support multiple collectors.

---

## 2026-07-15

### Implemented

- Refactored deterministic scoring into reusable matching components.
- Added separate technical, role, location, and early-career scores.
- Preserved the overall matching behavior after the refactor.
- Added tests for category-level scores and partial relocation scoring.
- Increased the test suite to 10 passing tests.

### Lessons Learned

- Splitting scoring categories makes the matching engine easier to extend and test.
- Category-level scores provide better explainability than a single overall number.
- Regression tests allowed the internal architecture to change without altering expected behavior.

### Next

- Add experience alignment as a matching category.
- Add education and certification matching.
- Persist detailed category scores and explanations.

---

## 2026-07-15 — Resume Parser Foundation

### Implemented

- Added PDF resume text extraction using PyMuPDF.
- Added validation for missing and unsupported files.
- Normalized spacing, line breaks, and hyphenated words.
- Split resume content into header, education, skills, work experience, and projects.
- Parsed programming languages, frameworks, tools, concepts, and certifications.
- Created a reusable `ParsedResume` service that coordinates the full parsing workflow.
- Increased the automated test suite to 22 passing tests.

### Challenges

- PDF extraction preserved layout-related line breaks that required normalization.
- Words split across lines with hyphens needed to be reconstructed.
- Resume parsing required stable section boundaries before structured fields could be extracted.

### Lessons Learned

- Deterministic parsing is effective when resume sections follow consistent headings.
- Separating extraction, cleanup, section parsing, and field parsing makes each stage easier to test.
- A reusable orchestration service keeps parsing logic out of the application entry point.

### Next

- Parse education into structured fields.
- Parse work experience and projects.
- Generate a `CandidateProfile` directly from the uploaded resume.