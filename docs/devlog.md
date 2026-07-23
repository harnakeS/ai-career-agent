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


---

## 2026-07-21 - Configurable Selected-Company Pipeline

### Implemented

- Added `SelectedCompanyPipeline`.
- Added `SelectedCompanyRunResult`.
- Added one application-facing collection and persistence boundary.
- Added pipeline-owned database-session management.
- Added aggregate run-summary properties.
- Added validated company-source configuration.
- Added duplicate source-configuration detection.
- Added configuration validation for providers, URLs, required fields, and enabled status.
- Added `app/composition.py` for production dependency construction.
- Added the real selected-company command-line runner.
- Added project-root-relative configuration paths.
- Added Datadog as the first verified configured company source.
- Removed the local SQLite database from version control.
- Increased the automated test suite to 254 passing tests.

### Live Application Result

The selected-company pipeline was run twice against Datadog's live Greenhouse board and the local application database.

The first run reported:

- One successful company source
- 421 collected jobs
- 421 new jobs
- Zero updated jobs
- Zero collection failures
- Zero persistence failures

The second run reported:

- One successful company source
- 421 collected jobs
- Zero new jobs
- 421 updated jobs
- Zero collection failures
- Zero persistence failures

The second run verified duplicate prevention in the real local database.

### Architectural Decisions

- Company sources are editable data rather than hardcoded Python values.
- Provider implementations are assembled in one composition module.
- Command-line and frontend entry points will share the same pipeline.
- The pipeline returns structured results instead of printing internally.
- User-facing entry points decide how results are displayed.
- The local database is application state and is not committed to Git.

### Validation

- Verified configuration loading against the real Datadog source.
- Verified first-run insertion behavior.
- Verified second-run update behavior.
- Completed 254 automated tests successfully.

### Next

- Create the Streamlit application shell.
- Display configured companies and their enabled status.
- Add a button that runs `SelectedCompanyPipeline`.
- Display run summaries and failures.
- Add a read-only table of persisted jobs.

---

## 2026-07-21 - Active Job Reconciliation and Frontend Readiness

### Implemented

- Added read-only repository access for stored jobs.
- Added active-only job retrieval by default.
- Added optional retrieval of inactive jobs.
- Added deterministic missing-job deactivation.
- Scoped deactivation to the matching company.
- Connected deactivation to successful company snapshots.
- Added aggregate deactivation counts to persistence results.
- Added deactivation counts to selected-company pipeline results.
- Added deactivation counts to the command-line summary.
- Added transactional rollback for deactivation failures.
- Added the missing Ollama client dependency to `requirements.txt`.
- Increased the automated test suite to 260 passing tests.

### Live Application Result

The selected-company pipeline was run against Datadog's live Greenhouse board and the existing local database.

The run reported:

- One successful company source
- 421 collected jobs
- Zero new jobs
- 421 updated jobs
- Zero deactivated jobs
- Zero collection failures
- Zero persistence failures

The result confirmed that the existing 421 postings remained active and that reconciliation did not produce false deactivations.

### Architectural Decisions

- Only successful company snapshots may deactivate stored jobs.
- Collection failures cannot change active-job status.
- Job insertion, updates, and deactivation share one company-level transaction.
- A failure during reconciliation rolls back all pending changes for that company.
- Active jobs are returned by default for user-facing discovery.
- Inactive jobs remain stored for history rather than being deleted.
- Frontend entry points will read jobs through `JobRepository` rather than issuing direct database queries.

### Validation

- Verified active-only repository queries.
- Verified optional inactive-job retrieval.
- Verified company-isolated deactivation.
- Verified transactional rollback after a deactivation failure.
- Verified pipeline-level deactivation counts.
- Completed 260 automated tests successfully.
- Completed a live 421-job reconciliation without false deactivations.

### Next

- Create the Streamlit application shell.
- Display configured companies and enabled status.
- Add a manual selected-company scan action.
- Display structured scan results and failures.
- Display a read-only table of active jobs.

---

## 2026-07-21 - First Streamlit Dashboard

### Implemented

- Added the first Streamlit dashboard.
- Added selected-company configuration display.
- Added configured and enabled company metrics.
- Added a manual selected-company scan action.
- Added structured collection and persistence summaries.
- Added collection and persistence failure reporting.
- Added a read-only stored-job table.
- Added title, company, and location search.
- Added company filtering.
- Added active and inactive job visibility.
- Added direct links to official job postings.
- Added a selected-company default view.
- Added deterministic dashboard view-model conversion and filtering.
- Added five dashboard view-model tests.
- Increased the automated test suite to 265 passing tests.

### Live Application Result

The dashboard was run against the existing local database and live Datadog configuration.

The interface successfully:

- displayed the selected company
- displayed stored job postings
- ran the selected-company scan
- displayed scan results
- searched job postings
- filtered jobs by company
- toggled inactive-job visibility
- opened official job links

The database currently contains no inactive postings, so enabling inactive-job visibility correctly leaves the displayed count unchanged and shows an informational message.

### Runtime Compatibility

The original Anaconda-based environment caused Streamlit to terminate with exit code 139 during widget reruns.

The project environment was rebuilt with standalone CPython 3.12. Compatible NumPy, Pandas, PyArrow, Streamlit, and Tornado versions were pinned in `requirements.txt`.

After rebuilding the environment, all dashboard interactions completed without crashes.

### Architectural Decisions

- The dashboard reads jobs through `JobRepository`.
- Presentation conversion and filtering remain outside Streamlit rendering code.
- Dashboard view-model behavior is deterministic and independently tested.
- The command-line and dashboard entry points share the selected-company pipeline.
- Local database state remains outside version control.
- The first dashboard remains intentionally read-only except for initiating scans.

### Validation

- Completed 265 automated tests successfully.
- Verified all current dashboard interactions manually.
- Verified selected-company scanning through the dashboard.
- Verified active and inactive display behavior.
- Verified official application links.

### Next

- Add a job-detail view.
- Connect candidate evidence matching to persisted selected-company jobs.
- Display match scores, strengths, gaps, and supporting resume evidence.
- Add additional selected companies through reusable ATS integrations.

---

## 2026-07-21 - Selectable Job Details and Description Formatting

### Implemented

- Added repository lookup by database identifier.
- Added a dashboard-specific job-detail view model.
- Added single-row selection to the stored-job table.
- Added complete job-detail rendering.
- Added job metadata, status, dates, and application links.
- Added full job-description display.
- Replaced flattened description normalization with safe Markdown conversion.
- Preserved HTML paragraph boundaries.
- Preserved headings and explicit line breaks.
- Converted unordered and ordered HTML lists into Markdown.
- Preserved bold and italic emphasis.
- Preserved safe HTTP and HTTPS links.
- Ignored script, style, and unsupported presentation content.
- Increased the automated test suite to 272 passing tests.

### Live Application Result

The dashboard was refreshed using current Datadog postings.

The interface successfully:

- selected individual jobs from the stored-job table
- loaded the correct job by database identifier
- displayed complete job metadata
- displayed the official application link
- displayed complete job descriptions
- preserved paragraph spacing
- displayed headings and list items correctly
- changed the detail view when another job was selected

Existing stored descriptions were refreshed through a selected-company scan so they could be reconstructed from the original Greenhouse HTML.

### Architectural Decisions

- The dashboard retrieves individual jobs through `JobRepository`.
- Database records are converted before their sessions are closed.
- Stable database identifiers connect table selections to detail records.
- Provider HTML is not rendered directly in the frontend.
- Description formatting is normalized during ingestion.
- The canonical description remains readable outside Streamlit.
- Formatting conversion remains deterministic and independently tested.

### Validation

- Completed 272 automated tests successfully.
- Verified row-selection behavior manually.
- Verified multiple Datadog job descriptions.
- Verified headings, paragraphs, lists, emphasis, and links.
- Verified that existing dashboard filters continue to work.

### Next

- Add resume upload and candidate-evidence initialization to the dashboard.
- Connect structured requirement extraction to selected jobs.
- Match extracted requirements against resume evidence.
- Display match scores, strengths, gaps, and supporting evidence.

---

## 2026-07-21 - In-Memory Resume Upload and Candidate Initialization

### Implemented

- Added PDF text extraction from in-memory bytes.
- Preserved the existing file-based resume parser.
- Added shared resume-text parsing orchestration.
- Added `CandidateResumeService`.
- Connected resume parsing, candidate-profile generation, and evidence generation.
- Added PDF upload controls to the Streamlit sidebar.
- Added explicit resume processing and clearing actions.
- Stored processed candidate data in Streamlit session state.
- Added a candidate-profile summary.
- Displayed education, skills, certifications, experience, roles, locations, relocation preferences, and work authorization.
- Kept uploaded resumes out of the local database.
- Increased the automated test suite to 279 passing tests.

### Data Provenance

Candidate data is assembled from two separate sources.

Resume-derived information includes:

- education
- graduation year
- technical skills
- certifications
- work experience
- projects
- inferred target roles

User-provided preferences include:

- preferred locations
- willingness to relocate
- citizenship and work authorization

The application does not infer personal eligibility or relocation information from resume content.

### Architectural Decisions

- Uploaded resumes are processed directly from bytes.
- Resume uploads are not written to disk by the application.
- `CandidateResumeService` coordinates candidate initialization outside the dashboard.
- The dashboard does not directly coordinate individual resume parsers.
- Candidate data remains in session state for the current local application session.
- Resume-derived information and user preferences remain separate sources.
- Search preferences currently come from `config/preferences.json`.

### Validation

- Completed 279 automated tests successfully.
- Verified PDF upload through the Streamlit dashboard.
- Verified candidate-profile display.
- Verified candidate-evidence creation.
- Verified candidate data survives ordinary dashboard reruns.
- Verified the processed resume can be cleared.
- Verified existing job search and detail interactions continue working.

### Next

- Add dashboard controls for user-provided search preferences.
- Convert selected stored jobs into canonical `JobPosting` objects.
- Extract structured requirements for a selected job.
- Match requirements against the active candidate evidence.
- Display strengths, gaps, and supporting resume evidence.

---

## 2026-07-23 - Explainable AI-Assisted Candidate Matching

### Implemented

- Added validated AI-provider configuration.
- Added OpenAI and local Ollama composition.
- Added configurable Ollama timeouts and generation limits.
- Disabled Ollama thinking output for structured extraction.
- Added safe local-model unloading behavior.
- Added conversion from persisted job records to canonical `JobPosting` models.
- Added selected-job candidate matching orchestration.
- Added qualification-section isolation before AI extraction.
- Added structured requirement alternatives.
- Added deterministic education-level and field-of-study separation.
- Added a default canonical vocabulary for production matching.
- Added vocabulary-aware matching for degree equivalency.
- Added alternative-value evidence matching.
- Added explicit résumé-to-description overlap detection.
- Added complete-term overlap boundaries to prevent short-skill false positives.
- Added personalized analysis to the Streamlit job-detail view.
- Added supporting-evidence and explanation tables.
- Separated missing required qualifications from missing preferred or optional qualifications.
- Added explicit overlap display that remains independent of AI extraction variability.
- Increased the automated test suite to 338 passing tests.

### Live Application Result

Personalized analysis was verified with a live Datadog FP&A posting and an uploaded resume using local Ollama model `qwen3.5:4b`.

The dashboard successfully:

- extracted structured job requirements
- matched the bachelor’s-degree requirement through canonical vocabulary
- identified missing required qualifications
- separated missing preferred qualifications
- displayed Python and SQL as explicit résumé overlap
- displayed Computer Science and Economics as explicit education overlap
- preserved overlap evidence even when the local model omitted the corresponding SQL and Python requirement
- completed analysis without the excessive runtime and resource use encountered with the larger local model

### Architectural Decisions

- AI is responsible for interpreting unstructured qualification text.
- Structured model output is validated before entering the matching layer.
- Requirement matching remains deterministic.
- Explicit description overlap remains separate from requirement satisfaction.
- Missing preferred qualifications do not increase the required-gap count.
- User-provided preferences remain separate from resume-derived evidence.
- The local four-billion-parameter model is treated as a development provider rather than a source of deterministic truth.
- `qwen3.5:4b` is the current recommended local model for development on the 16 GB Mac.
- Larger local models are not used synchronously in the Streamlit request path.

### Known Limitations

- Local model extraction may omit qualifications or group them differently between runs.
- Analysis results are stored only in Streamlit session state.
- Reanalyzing a job currently invokes the model again.
- Requirement coverage is not yet a final weighted match score.
- Date-aware experience aggregation is not yet implemented.

### Validation

- Completed 338 automated tests successfully.
- Verified local Ollama analysis through Streamlit.
- Verified explicit Python, SQL, Computer Science, and Economics overlap.
- Verified bachelor’s-degree vocabulary matching.
- Verified separate required and preferred qualification counts.
- Verified supporting evidence and explanations in the dashboard.

### Next

- Persist and cache structured requirement extraction.
- Persist candidate-to-job analysis results.
- Add deterministic weighted job scoring.
- Rank stored jobs by personalized match quality.

---

## 2026-07-23 - Persistent Job Requirements Cache

### Implemented

- Added a SQLite model for cached job requirements.
- Added provider, model, and extractor-version cache identity.
- Added SHA-256 job-description digests.
- Added automatic cache invalidation when a posting changes.
- Added deterministic `JobRequirements` JSON serialization and validation.
- Added stale-result replacement without duplicate cache records.
- Added a cache-aware requirement extraction service.
- Prevented repeated AI calls for unchanged stored jobs.
- Preserved ordinary extraction behavior for jobs not stored locally.
- Avoided holding database sessions open during AI inference.
- Connected the persistent cache through production composition.
- Updated the default local Ollama model to `qwen3.5:4b`.
- Increased the automated test suite to 345 passing tests.

### Architectural Decisions

- Job requirements are cached independently from candidate evidence.
- Uploaded resume content is not persisted in the requirements cache.
- Cache validity depends on the job description, AI provider, model, and extractor version.
- AI inference runs outside database sessions.
- Database transaction ownership remains explicit.
- The first cache implementation uses the existing local SQLite database.

### Validation

- Completed 345 automated tests successfully.
- Verified requirement serialization and retrieval.
- Verified changed descriptions invalidate cached results.
- Verified stale entries are updated instead of duplicated.
- Verified different models and extractor versions do not share results.
- Verified repeated extraction invokes the AI extractor only once.
- Verified the cache table is created in the local application database.

### Next

- Expose cache usage in the Streamlit analysis interface.
- Verify that a repeated analysis completes without another Ollama call.
- Persist candidate-to-job match summaries.
- Add deterministic weighted job scoring.