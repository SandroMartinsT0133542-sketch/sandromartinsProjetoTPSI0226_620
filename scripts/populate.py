"""Populate script for local testing.

Creates one test user, prints credentials to terminal, and inserts
sample progress records for that user.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from random import randint, uniform

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.services.auth_service import authenticate, initialize_auth, register_user
from src.services.progress_service import create_record, initialize_service, save_state


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a test user and seed progress records.")
    parser.add_argument("--count", type=int, default=200, help="Number of records to create (default: 200).")
    return parser


def _make_credentials() -> tuple[str, str, str, str]:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"seed_{stamp}"
    password = f"Seed@{stamp[-6:]}"
    email = f"{username}@example.local"
    phone = f"+3519{randint(10000000, 99999999)}"
    return username, password, email, phone


def _create_records(count: int) -> None:
    start_date = datetime.now() - timedelta(days=count)
    weight = uniform(72.0, 96.0)
    body_fat = uniform(17.0, 32.0)

    for offset in range(count):
        day = start_date + timedelta(days=offset)

        # Simulate mild fluctuations with a gradual trend.
        weight += uniform(-0.35, 0.25)
        body_fat += uniform(-0.08, 0.04)

        weight = max(58.0, min(140.0, weight))
        body_fat = max(8.0, min(55.0, body_fat))
        calories = randint(1700, 2900)

        create_record(
            {
                "record_date": day.strftime("%d-%m-%Y"),
                "weight_kg": round(weight, 1),
                "body_fat_pct": round(body_fat, 1),
                "daily_calories": calories,
                "notes": f"Seeded record #{offset + 1}",
            }
        )


def main() -> int:
    args = _build_parser().parse_args()
    if args.count <= 0:
        print("[Error] --count must be greater than 0.")
        return 1

    initialize_auth()
    initialize_service()

    username, password, email, phone = _make_credentials()
    ok, message = register_user(
        username=username,
        display_name=f"Seed User {username[-6:]}",
        password=password,
        email=email,
        phone=phone,
    )
    if not ok:
        print(f"[Error] Could not create test user: {message}")
        return 1

    if not authenticate(username, password):
        print("[Error] Created user could not authenticate.")
        return 1

    _create_records(args.count)
    if not save_state():
        print("[Error] Records were created in memory but could not be saved.")
        return 1

    print("Test user created successfully.")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Records inserted: {args.count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())