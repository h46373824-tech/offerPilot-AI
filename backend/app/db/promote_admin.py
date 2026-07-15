import argparse

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote a local OfferPilot user to admin")
    parser.add_argument("email", help="Existing user email")
    args = parser.parse_args()
    email = args.email.strip().lower()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            raise SystemExit(f"User does not exist: {email}")
        user.is_admin = True
        db.commit()
    print(f"Local admin enabled: {email}")


if __name__ == "__main__":
    main()
