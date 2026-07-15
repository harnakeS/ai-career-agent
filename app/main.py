from app.parsing.resume_parser import parse_resume


def main() -> None:
    resume = parse_resume("data/resume.pdf")

    print("Projects parsed successfully.")
    print("-----------------------------")

    for project in resume.projects:
        print(f"Name: {project.name}")
        print(f"Duration: {project.duration_months} months")
        print(f"Technologies: {project.technologies}")
        print(f"Bullets: {len(project.bullets)}")
        print()


if __name__ == "__main__":
    main()