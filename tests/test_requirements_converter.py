from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.converter import (
    convert_extracted_requirements,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)


def test_converter_preserves_dynamic_requirement_values() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.CERTIFICATION,
                importance=RequirementImportance.REQUIRED,
                value="Registered Nurse License",
                source_text="An active Registered Nurse License is required.",
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert len(result.requirements) == 1
    assert result.requirements[0].value == "Registered Nurse License"


def test_converter_trims_requirement_whitespace() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="  Financial Modeling  ",
                source_text="  Financial modeling experience is preferred.  ",
            )
        ]
    )

    result = convert_extracted_requirements(extracted)
    requirement = result.requirements[0]

    assert requirement.value == "Financial Modeling"
    assert (
        requirement.source_text
        == "Financial modeling experience is preferred."
    )


def test_converter_removes_case_insensitive_duplicates() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Patient Care",
            ),
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="patient care",
            ),
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert len(result.requirements) == 1
    assert result.requirements[0].value == "Patient Care"


def test_converter_keeps_strongest_duplicate_importance() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Forklift Operation",
                source_text="Forklift operation experience is preferred.",
            ),
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="forklift operation",
                source_text="Forklift operation experience is required.",
            ),
        ]
    )

    result = convert_extracted_requirements(extracted)
    requirement = result.requirements[0]

    assert len(result.requirements) == 1
    assert requirement.importance == RequirementImportance.REQUIRED
    assert requirement.source_text == (
        "Forklift operation experience is required."
    )


def test_converter_preserves_job_level_metadata() -> None:
    extracted = ExtractedJobRequirements(
        minimum_experience_months=24,
        entry_level=False,
        work_authorization_required=True,
        sponsorship_available=False,
    )

    result = convert_extracted_requirements(extracted)

    assert result.minimum_experience_months == 24
    assert result.entry_level is False
    assert result.work_authorization_required is True
    assert result.sponsorship_available is False

def test_converter_derives_experience_months_from_requirement_text() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.EXPERIENCE,
                importance=RequirementImportance.REQUIRED,
                value="At least one year of acute-care nursing experience",
                source_text=(
                    "At least one year of acute-care nursing experience "
                    "is required."
                ),
            )
        ],
        minimum_experience_months=None,
    )

    result = convert_extracted_requirements(extracted)

    assert result.minimum_experience_months == 12

def test_converter_preserves_explicit_experience_months() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.EXPERIENCE,
                importance=RequirementImportance.REQUIRED,
                value="At least 5 years of experience",
            )
        ],
        minimum_experience_months=24,
    )

    result = convert_extracted_requirements(extracted)

    assert result.minimum_experience_months == 24

def test_converter_preserves_requirement_alternatives() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="SQL",
                alternatives=["Python", "R"],
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert result.requirements[0].alternatives == [
        "Python",
        "R",
    ]


def test_converter_trims_and_deduplicates_alternatives() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="SQL",
                alternatives=[
                    " Python ",
                    "python",
                    " SQL ",
                    "",
                    "R",
                ],
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert result.requirements[0].alternatives == [
        "Python",
        "R",
    ]

def test_converter_separates_degree_from_fields_of_study() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.EDUCATION,
                importance=RequirementImportance.REQUIRED,
                value="Bachelor's degree",
                alternatives=[
                    "Finance",
                    "Accounting",
                    "Business",
                    "Economics",
                    "Computer Science",
                ],
                source_text=(
                    "Bachelor's degree in finance, accounting, "
                    "business, economics, or computer science."
                ),
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert len(result.requirements) == 2

    degree = result.requirements[0]
    field = result.requirements[1]

    assert degree.value == "Bachelor's degree"
    assert degree.alternatives == []

    assert field.value == "Finance"
    assert field.alternatives == [
        "Accounting",
        "Business",
        "Economics",
        "Computer Science",
    ]


def test_converter_preserves_alternative_degree_levels() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.EDUCATION,
                importance=RequirementImportance.REQUIRED,
                value="Bachelor's degree",
                alternatives=[
                    "Master's degree",
                    "Doctoral degree",
                ],
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert len(result.requirements) == 1
    assert result.requirements[0].alternatives == [
        "Master's degree",
        "Doctoral degree",
    ]


def test_converter_does_not_split_noneducation_alternatives() -> None:
    extracted = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="SQL",
                alternatives=["Python", "R"],
            )
        ]
    )

    result = convert_extracted_requirements(extracted)

    assert len(result.requirements) == 1
    assert result.requirements[0].value == "SQL"
    assert result.requirements[0].alternatives == [
        "Python",
        "R",
    ]