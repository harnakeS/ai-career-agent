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