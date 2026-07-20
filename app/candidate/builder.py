from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
    EvidenceConfidence,
    EvidenceSourceType,
)
from app.models.candidate import CandidateProfile


class CandidateEvidenceBuilder:
    """Build structured evidence from an existing CandidateProfile."""

    def build(
        self,
        profile: CandidateProfile,
    ) -> CandidateEvidenceCollection:
        evidence: list[CandidateEvidence] = []

        evidence.extend(self._build_skill_evidence(profile))
        evidence.extend(self._build_education_evidence(profile))
        evidence.extend(self._build_certification_evidence(profile))
        evidence.extend(self._build_experience_evidence(profile))

        return CandidateEvidenceCollection(evidence=evidence)

    def _build_skill_evidence(
        self,
        profile: CandidateProfile,
    ) -> list[CandidateEvidence]:
        evidence: list[CandidateEvidence] = []

        skill_groups = (
            ("Programming Languages", profile.programming_languages),
            ("Frameworks", profile.frameworks),
            ("Tools", profile.tools),
            ("Skills", profile.skills),
        )

        for source_name, values in skill_groups:
            for value in values:
                cleaned_value = value.strip()

                if not cleaned_value:
                    continue

                evidence.append(
                    CandidateEvidence(
                        category=EvidenceCategory.SKILL,
                        value=cleaned_value,
                        source_type=EvidenceSourceType.SKILLS,
                        source_name=source_name,
                        evidence_text=cleaned_value,
                        confidence=EvidenceConfidence.HIGH,
                    )
                )

        return evidence

    def _build_education_evidence(
        self,
        profile: CandidateProfile,
    ) -> list[CandidateEvidence]:
        evidence: list[CandidateEvidence] = []

        if profile.education.strip():
            evidence.append(
                CandidateEvidence(
                    category=EvidenceCategory.EDUCATION,
                    value=profile.education.strip(),
                    source_type=EvidenceSourceType.EDUCATION,
                    source_name="Education",
                    evidence_text=profile.education.strip(),
                    confidence=EvidenceConfidence.HIGH,
                )
            )

        for major in profile.majors:
            cleaned_major = major.strip()

            if not cleaned_major:
                continue

            evidence.append(
                CandidateEvidence(
                    category=EvidenceCategory.EDUCATION,
                    value=cleaned_major,
                    source_type=EvidenceSourceType.EDUCATION,
                    source_name="Major",
                    evidence_text=cleaned_major,
                    confidence=EvidenceConfidence.HIGH,
                )
            )

        for minor in profile.minors:
            cleaned_minor = minor.strip()

            if not cleaned_minor:
                continue

            evidence.append(
                CandidateEvidence(
                    category=EvidenceCategory.EDUCATION,
                    value=cleaned_minor,
                    source_type=EvidenceSourceType.EDUCATION,
                    source_name="Minor",
                    evidence_text=cleaned_minor,
                    confidence=EvidenceConfidence.HIGH,
                )
            )

        return evidence

    def _build_certification_evidence(
        self,
        profile: CandidateProfile,
    ) -> list[CandidateEvidence]:
        evidence: list[CandidateEvidence] = []

        for certification in profile.certifications:
            cleaned_certification = certification.strip()

            if not cleaned_certification:
                continue

            evidence.append(
                CandidateEvidence(
                    category=EvidenceCategory.CERTIFICATION,
                    value=cleaned_certification,
                    source_type=EvidenceSourceType.CERTIFICATION,
                    source_name="Certifications",
                    evidence_text=cleaned_certification,
                    confidence=EvidenceConfidence.HIGH,
                )
            )

        return evidence

    def _build_experience_evidence(
        self,
        profile: CandidateProfile,
    ) -> list[CandidateEvidence]:
        experience_fields = (
            (
                "Full-Time Experience",
                profile.full_time_experience_months,
            ),
            (
                "Internship Experience",
                profile.internship_experience_months,
            ),
            (
                "Co-op Experience",
                profile.co_op_experience_months,
            ),
            (
                "Part-Time Experience",
                profile.part_time_experience_months,
            ),
            (
                "Contract Experience",
                profile.contract_experience_months,
            ),
        )

        evidence: list[CandidateEvidence] = []

        for source_name, months in experience_fields:
            if months <= 0:
                continue

            evidence.append(
                CandidateEvidence(
                    category=EvidenceCategory.EXPERIENCE,
                    value=f"{months} months",
                    source_type=EvidenceSourceType.EXPERIENCE,
                    source_name=source_name,
                    evidence_text=f"{months} months of {source_name.lower()}",
                    confidence=EvidenceConfidence.HIGH,
                )
            )

        return evidence