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

---

## 2026-07-16 — Resume-Generated Candidate Profiles

### Implemented

- Expanded `CandidateProfile` to track experience by employment type.
- Replaced the single years-of-experience field with month-based full-time, internship, co-op, part-time, and contract totals.
- Built a candidate-profile builder using structured resume data.
- Added candidate-name extraction.
- Added experience aggregation by employment category.
- Added deterministic target-role inference from skills, certifications, and projects.
- Updated the live job pipeline to use the resume-generated candidate profile.
- Removed the pipeline's dependency on the hardcoded candidate configuration.
- Increased the automated test suite to 51 passing tests.

### Lessons Learned

- Internship experience should not be represented as full-time professional experience.
- Resume-derived facts and user preferences should remain separate.
- Passing the candidate profile into the pipeline makes the matching engine easier to test and adapt.
- Structured resume parsing becomes valuable when downstream systems directly consume the resulting data.

### Next

- Move personal preferences out of `main.py` into configuration.
- Add experience, education, certification, and work-authorization scoring.
- Persist richer matching explanations and category scores.
- Begin support for multiple job collectors.

---

## 2026-07-16 — Resume-Generated Candidate Profiles and Preferences

### Implemented

- Expanded `CandidateProfile` to track experience by employment type.
- Replaced the single years-of-experience field with month-based totals for full-time, internship, co-op, part-time, and contract work.
- Built a `CandidateProfile` builder using structured resume data.
- Added candidate-name extraction.
- Added experience aggregation by employment category.
- Added deterministic desired-role inference from skills, certifications, and project technologies.
- Updated `JobPipeline` to receive a candidate profile through dependency injection.
- Removed the live pipeline's dependency on a hardcoded global candidate.
- Added a validated `CandidatePreferences` model.
- Added JSON-based loading for preferred locations, relocation willingness, and work authorization.
- Added validation and error handling for missing, malformed, and incomplete preference files.
- Increased the automated test suite to 55 passing tests.

### Challenges

- Resume-derived facts had to remain separate from personal preferences that cannot be safely inferred.
- Internship experience needed to be represented independently from full-time professional experience.
- The application required a clean transition away from the temporary hardcoded candidate profile.
- Configuration data and Python configuration modules needed clearly separated locations.

### Lessons Learned

- The resume should be the source of truth for education, skills, certifications, projects, and experience.
- User preferences should be explicit rather than inferred.
- Dependency injection makes the matching pipeline easier to adapt and test.
- Month-based experience totals preserve more useful information than a single rounded year count.
- Configuration files make personal settings editable without changing application code.

### Next

- Add experience alignment scoring.
- Add education, certification, and work-authorization scoring.
- Improve category weighting and recommendation explanations.
- Persist richer score breakdowns.

---

## Job Requirements Engine Foundation

- Added structured `Requirement` and `JobRequirements` models.
- Added requirement categories for skills, education, experience, certifications, location, language, clearance, and authorization.
- Added required, preferred, and optional importance levels.
- Added filtering helpers for retrieving requirements by category and importance.
- Reorganized requirement parsing into `app/parsing/requirements/`.
- Added deterministic requirement-importance classification.
- Added real job-description fixtures across backend, AI, cloud, data, and IT roles.
- Added validated schemas for future LLM-based requirement extraction.
- Chose an LLM-driven skill extraction approach instead of maintaining a fixed skill vocabulary.
- Test suite increased to 94 passing tests.

---

## 2026-07-18 - Requirement Extraction Quality Improvements

- Added `LICENSE` and `SCHEDULE` requirement categories.
- Improved the LLM extraction prompt with profession-independent category definitions.
- Verified that the extractor correctly distinguishes professional licenses from education and schedule constraints from skills.
- Added deterministic experience-duration parsing.
- Added support for numeric and written durations such as `1 year`, `1.5 years`, `6 months`, and `one year`.
- Updated the converter to derive `minimum_experience_months` when the LLM omits it.
- Preserved explicit LLM-provided duration metadata when available.
- Increased the automated test suite to 127 passing tests.

### Live Extraction Result

The Ollama extraction pipeline correctly classified:

- New Jersey RN license as `license`
- Weekend availability as `schedule`
- BLS and ACLS as `certification`
- Acute-care nursing experience as `experience`

The experience duration was normalized deterministically to avoid relying entirely on LLM consistency.

---

## 2026-07-20 - Dynamic Vocabulary Foundation

Implemented a category-aware vocabulary layer for requirement and evidence normalization.

### Completed

- Added `VocabularyCategory` to separate vocabulary concepts by domain.
- Added `VocabularyConcept` for canonical values and aliases.
- Added the `VocabularyRepository` protocol.
- Added `InMemoryVocabularyRepository` for development and testing.
- Added runtime vocabulary registration.
- Added category-aware concept resolution.
- Added conflict detection for aliases mapped to different concepts within the same category.
- Allowed the same alias to exist in separate categories.
- Moved generic text cleanup into `app/vocabulary/text.py`.
- Updated `RequirementNormalizer` to use an injected vocabulary repository.
- Removed embedded domain vocabulary from the normalizer.
- Preserved fallback behavior for unknown terms.
- Verified that new vocabulary concepts can be added without changing normalization or matching source code.

### Architectural Decisions

The normalizer does not own a static vocabulary.

Generic formatting rules remain in code because they apply universally. Domain-specific aliases are supplied through a repository so they can later be loaded from persistent storage.

Vocabulary resolution is category-aware because the same abbreviation may represent different concepts in different contexts.

Example:
BA → Bachelor of Arts
BA → Business Analyst

Categories prevent those meanings from being merged accidentally.

### Validation

- Increased the automated test suite to 170 passing tests.

### Next

- Integrate vocabulary resolution with candidate evidence matching.


---

## 2026-07-20 - Canonical Evidence Matching and Greenhouse Integration

### Implemented

- Integrated category-aware vocabulary resolution into `EvidenceMatcher`.
- Preserved normalized direct-value matching.
- Added explainable reasons for direct and vocabulary-resolved matches.
- Added category isolation during evidence matching.
- Added deterministic experience-duration comparison.
- Added support for combining explicit duration evidence.
- Preserved ordinary normalized matching for experience requirements without durations.
- Added provider-neutral `CompanySource` and `RawJobPosting` models.
- Added the runtime-checkable `JobSource` protocol.
- Added job-source domain exceptions.
- Added an injectable JSON HTTP client boundary.
- Implemented the Greenhouse Job Board API integration.
- Added validation for Greenhouse response payloads.
- Added support for disabled company sources.
- Added incompatible-provider validation.
- Added a manual Greenhouse integration script.
- Increased the automated test suite to 203 passing tests.

### Live Integration Result

The Greenhouse source successfully collected 415 published jobs from Datadog's public job board.

The collected postings included:

- Provider job identifiers
- Job titles
- Locations
- Update timestamps
- Full job descriptions
- Official Datadog application links

### Architectural Decisions

- Provider-specific responses are converted into `RawJobPosting` objects before entering the rest of the application.
- Network access is isolated behind an injectable HTTP-client protocol.
- Live network checks remain outside the permanent unit-test suite.
- Provider implementations expose the same `JobSource` contract.
- Company sources can be disabled without modifying provider code.

### Known Limitations

- Greenhouse collection is not yet connected to the existing processing pipeline.
- `RawJobPosting.posted_at` temporarily stores Greenhouse's `updated_at` value.
- Experience-duration matching does not yet detect overlapping or duplicated employment periods.

### Next

- Convert `RawJobPosting` into the canonical `JobPosting` model.
- Separate publication, update, discovery, and collection timestamps.
- Normalize HTML job descriptions before persistence and matching.
- Integrate selected-company sources with the existing processing pipeline.


---

## 2026-07-20 - Canonical Job Posting Conversion

### Implemented

- Separated raw publication and update timestamps.
- Updated the Greenhouse source to store `updated_at` correctly.
- Prevented Greenhouse update timestamps from being treated as publication dates.
- Added provider-neutral HTML job-description normalization.
- Added support for decoding nested HTML entities.
- Preserved paragraph and list boundaries during description cleanup.
- Added the `JobPostingConverter`.
- Added deterministic ISO publication-timestamp parsing.
- Added raw-to-canonical field mapping.
- Added explicit conversion errors for invalid timestamps, blank descriptions, and canonical validation failures.
- Updated the live Greenhouse integration script to convert every collected posting.
- Increased the automated test suite to 213 passing tests.

### Live Integration Result

The Greenhouse source collected 414 raw postings from Datadog's public job board.

All 414 raw postings were successfully converted into canonical `JobPosting` objects.

The converted postings contained:

- Canonical requisition identifiers
- Company names
- Job titles
- Locations
- Normalized plain-text descriptions
- Official application URLs
- Verified publication dates when available

Zero Datadog postings received an original publication date because the Greenhouse job-list response supplied `updated_at` rather than `published_at`.

The change from 415 postings during the previous check to 414 postings during this check reflects normal changes to the live job board.

### Architectural Decisions

- Publication and update timestamps represent different facts and must not be substituted for one another.
- Raw provider timestamps remain strings until canonical conversion.
- Canonical timestamp parsing is deterministic.
- Description normalization is provider-neutral and reusable across future sources.
- Invalid raw data is rejected before reaching persistence or matching.
- Live provider validation remains separate from deterministic unit tests.

### Validation

- Converted 414 of 414 live Datadog postings.
- Completed 213 automated tests successfully.

### Next

- Add a job-source registry.
- Select provider implementations through company configuration.
- Build a multi-company collection service.
- Connect canonical Greenhouse postings to persistence without duplicating existing jobs.


---

## 2026-07-20 - Job Source Registry and Multi-Company Collection

### Implemented

- Added the `JobSourceRegistry`.
- Added provider-to-implementation registration.
- Added provider implementation resolution.
- Added duplicate-registration prevention.
- Added missing-provider error handling.
- Added invalid source-implementation validation.
- Added `CompanyCollectionFailure`.
- Added `CompanyCollectionResult`.
- Added `CompanyJobCollectionService`.
- Added disabled-company handling.
- Added multiple-provider resolution.
- Added per-company failure isolation.
- Added atomic company-level conversion.
- Preserved unexpected programming-error propagation.
- Updated the Greenhouse integration script to use the registry and collection service.
- Increased the automated test suite to 231 passing tests.

### Live Integration Result

The complete selected-company orchestration path was tested against Datadog's public Greenhouse board.

The live run reported:

- One successful company source
- Zero skipped sources
- Zero collection failures
- 415 canonical job postings
- Zero original publication dates

All collected postings passed canonical conversion.

### Architectural Decisions

- Provider selection is handled by a registry rather than conditional logic in the application entry point.
- Provider implementations are constructed outside the registry and registered explicitly.
- Disabled company configurations are skipped before provider resolution.
- Expected job-source failures are isolated by company.
- Unexpected programming errors are allowed to propagate.
- Company-level conversion is atomic.
- An incomplete company snapshot is not returned as a successful collection.

### Validation

- Completed the live Greenhouse orchestration path successfully.
- Completed 231 automated tests successfully.

### Next

- Connect `CompanyJobCollectionService` to job persistence.
- Preserve duplicate detection through the existing repository.
- Produce a structured persistence summary for each collection run.
- Verify that running the same Greenhouse collection twice does not create duplicate database rows.


---

## 2026-07-21 - Transactional Company Job Persistence

### Implemented

- Refactored `JobRepository` so callers control commit and rollback behavior.
- Replaced per-job commits with transaction-safe session flushing.
- Added repository tests for insertion, updates, duplicate prevention, reactivation, discovery-time preservation, and rollback.
- Added `CompanyJobSnapshot`.
- Preserved the relationship between each company source and its canonical jobs.
- Added compatibility views for combined jobs and successful sources.
- Added `CompanyPersistenceSummary`.
- Added `CompanyPersistenceFailure`.
- Added `CompanyPersistenceResult`.
- Added `CompanyJobPersistenceService`.
- Added one database transaction per company snapshot.
- Added expected database-failure isolation.
- Added rollback behavior for unexpected programming errors.
- Added structured new-job and updated-job counts.
- Updated the live Greenhouse check to verify persistence in a temporary database.
- Increased the automated test suite to 242 passing tests.

### Live Integration Result

The complete Greenhouse collection, conversion, and persistence path was tested against Datadog's public job board.

The live run collected 420 canonical postings.

The first persistence pass reported:

- 420 new jobs
- Zero updated jobs
- 420 database rows

The second persistence pass reported:

- Zero new jobs
- 420 updated jobs
- 420 database rows

The unchanged database row count verified duplicate prevention.

### Architectural Decisions

- Collection results preserve company-level job snapshots.
- Empty successful snapshots remain distinct from collection failures.
- Repositories prepare database changes but do not own transaction boundaries.
- Each company snapshot is persisted atomically.
- A database failure for one company does not roll back previously committed companies.
- Unexpected persistence errors are rolled back and re-raised.
- Live persistence validation uses an in-memory database and does not modify development data.

### Validation

- Verified duplicate prevention against 420 live postings.
- Verified insert and update counts across repeated persistence passes.
- Completed 242 automated tests successfully.

### Next

- Connect collection and persistence through a scheduled application pipeline.
- Load selected companies from configuration rather than command-line arguments.
- Add persistence summaries to the pipeline output.
- Add safe closed-job detection using only successful company snapshots.