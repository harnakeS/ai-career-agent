# An AI-powered career agent that continuously monitors software engineering opportunities, ranks them using a hybrid matching engine, and recommends the highest-value applications based on a structured candidate profile.

## Current Status

The personal-use backend can currently:

- Collect live job postings
- Normalize jobs into a shared model
- Store and update postings without duplicates
- Parse a PDF resume into structured skills, education, experience, and project data
- Distinguish internship experience from full-time experience
- Generate a candidate profile directly from the resume
- Load personal job-search preferences from JSON
- Score jobs using a deterministic matching engine
- Structured, LLM-ready job requirement extraction with validated output and explainable deterministic scoring

The automated test suite currently contains 94 passing tests.

The next development phase focuses on richer experience, education, certification, and work-authorization scoring before adding more company collectors.