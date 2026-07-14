from app.database.database import create_database


def main() -> None:
    create_database()
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()