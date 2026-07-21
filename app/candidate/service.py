from dataclasses import dataclass

from app.candidate.builder import (
    CandidateEvidenceBuilder,
)
from app.models.candidate import CandidateProfile
from app.models.candidate_evidence import (
    CandidateEvidenceCollection,
)
from app.models.preferences import CandidatePreferences
from app.parsing.candidate_builder import (
    build_candidate_profile,
)
from app.parsing.resume_parser import (
    ParsedResume,
    parse_resume_bytes,
)


@dataclass(frozen=True)
class CandidateResumeResult:
    """Complete candidate data produced from one uploaded resume."""

    parsed_resume: ParsedResume
    profile: CandidateProfile
    evidence: CandidateEvidenceCollection


class CandidateResumeService:
    """Process an uploaded resume into candidate matching data."""

    def __init__(
        self,
        evidence_builder: CandidateEvidenceBuilder | None = None,
    ) -> None:
        self._evidence_builder = (
            evidence_builder
            or CandidateEvidenceBuilder()
        )

    def process(
        self,
        pdf_bytes: bytes,
        preferences: CandidatePreferences,
    ) -> CandidateResumeResult:
        """Parse a resume and build its profile and evidence."""

        parsed_resume = parse_resume_bytes(
            pdf_bytes
        )

        profile = build_candidate_profile(
            parsed_resume,
            preferred_locations=(
                preferences.preferred_locations
            ),
            willing_to_relocate=(
                preferences.willing_to_relocate
            ),
            us_citizen=preferences.us_citizen,
        )

        evidence = self._evidence_builder.build(
            profile
        )

        return CandidateResumeResult(
            parsed_resume=parsed_resume,
            profile=profile,
            evidence=evidence,
        )