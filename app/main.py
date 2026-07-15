from app.resume.resume_parser import parse_resume


def main() -> None:
    resume = parse_resume("data/resume.pdf")

    print("Resume parsed successfully.")
    print("---------------------------")
    print(f"Programming languages: {resume.skills.programming_languages}")
    print(f"Frameworks: {resume.skills.frameworks}")
    print(f"Tools: {resume.skills.tools}")
    print(f"Concepts: {resume.skills.concepts}")
    print(f"Certifications: {resume.skills.certifications}")
    print()
    print("Education section:")
    print(resume.sections.education)


if __name__ == "__main__":
    main()