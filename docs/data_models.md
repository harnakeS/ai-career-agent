# Data Models

## CandidateProfile

### Purpose

Represents the normalized candidate data consumed by the job-matching engine.

### Fields

- `name`
- `graduation_year`
- `education`
- `majors`
- `minors`
- `programming_languages`
- `frameworks`
- `tools`
- `skills`
- `certifications`
- `full_time_experience_months`
- `internship_experience_months`
- `co_op_experience_months`
- `part_time_experience_months`
- `contract_experience_months`
- `preferred_locations`
- `willing_to_relocate`
- `us_citizen`
- `desired_roles`

### Sources

Resume-derived fields come from `ParsedResume`.

Personal preferences come from `CandidatePreferences`.

---

## CandidatePreferences

### Purpose

Stores user-provided information that should not be inferred from a resume.

### Fields

- `preferred_locations`
- `willing_to_relocate`
- `us_citizen`

### Storage

The personal-use version loads this model from:

```text
config/preferences.json