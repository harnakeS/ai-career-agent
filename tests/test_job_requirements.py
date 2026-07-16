from app.models.job_requirements import (
    JobRequirements,
    Requirement,
    RequirementCategory,
    RequirementImportance,
)


def test_job_requirements_uses_empty_defaults() -> None:
    requirements = JobRequirements()

    assert requirements.requirements == []
    assert requirements.minimum_experience_months is None
    assert requirements.entry_level is False
    assert requirements.work_authorization_required is False
    assert requirements.sponsorship_available is None


def test_requirement_stores_structured_values() -> None:
    requirement = Requirement(
        category=RequirementCategory.SKILL,
        importance=RequirementImportance.REQUIRED,
        value="Python",
        source_text="Python is required.",
    )

    assert requirement.category == RequirementCategory.SKILL
    assert requirement.importance == RequirementImportance.REQUIRED
    assert requirement.value == "Python"
    assert requirement.source_text == "Python is required."


def test_job_requirements_stores_multiple_requirement_types() -> None:
    requirements = JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
            ),
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Docker",
            ),
            Requirement(
                category=RequirementCategory.EDUCATION,
                importance=RequirementImportance.REQUIRED,
                value="Bachelor's degree",
            ),
            Requirement(
                category=RequirementCategory.CERTIFICATION,
                importance=RequirementImportance.PREFERRED,
                value="Security+",
            ),
        ],
        minimum_experience_months=24,
        entry_level=False,
        work_authorization_required=True,
        sponsorship_available=False,
    )

    assert len(requirements.requirements) == 4

    assert requirements.requirements[0].value == "Python"
    assert (
        requirements.requirements[0].importance
        == RequirementImportance.REQUIRED
    )

    assert requirements.requirements[1].value == "Docker"
    assert (
        requirements.requirements[1].importance
        == RequirementImportance.PREFERRED
    )

    assert (
        requirements.requirements[2].category
        == RequirementCategory.EDUCATION
    )

    assert (
        requirements.requirements[3].category
        == RequirementCategory.CERTIFICATION
    )

    assert requirements.minimum_experience_months == 24
    assert requirements.work_authorization_required is True
    assert requirements.sponsorship_available is False


def test_requirement_lists_are_not_shared() -> None:
    first = JobRequirements()
    second = JobRequirements()

    first.requirements.append(
        Requirement(
            category=RequirementCategory.SKILL,
            importance=RequirementImportance.REQUIRED,
            value="Python",
        )
    )

    assert len(first.requirements) == 1
    assert second.requirements == []

def test_get_requirements_filters_by_category() -> None:
    requirements = JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
            ),
            Requirement(
                category=RequirementCategory.EDUCATION,
                importance=RequirementImportance.REQUIRED,
                value="Bachelor's degree",
            ),
        ]
    )

    result = requirements.get_requirements(
        category=RequirementCategory.SKILL,
    )

    assert [requirement.value for requirement in result] == ["Python"]


def test_get_required_filters_by_importance_and_category() -> None:
    requirements = JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
            ),
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Docker",
            ),
            Requirement(
                category=RequirementCategory.EDUCATION,
                importance=RequirementImportance.REQUIRED,
                value="Bachelor's degree",
            ),
        ]
    )

    result = requirements.get_required(
        RequirementCategory.SKILL,
    )

    assert [requirement.value for requirement in result] == ["Python"]


def test_get_preferred_returns_all_preferred_requirements() -> None:
    requirements = JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Docker",
            ),
            Requirement(
                category=RequirementCategory.CERTIFICATION,
                importance=RequirementImportance.PREFERRED,
                value="Security+",
            ),
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
            ),
        ]
    )

    result = requirements.get_preferred()

    assert [requirement.value for requirement in result] == [
        "Docker",
        "Security+",
    ]