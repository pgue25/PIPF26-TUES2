#!/usr/bin/env python3
"""Apply schema.sql and load class_dataset.csv into DATABASE_URL."""

from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "class_dataset.csv"
SCHEMA_PATH = ROOT / "schema.sql"


def split_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def parse_submitted_at(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def apply_schema(cur) -> None:
    cur.execute("DROP SCHEMA IF EXISTS class_survey CASCADE")
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cur.execute(sql)


def load_rows(cur) -> tuple[int, int, int]:
    cur.execute("SET search_path TO class_survey, public")

    students = 0
    tools = 0

    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            cur.execute(
                """
                INSERT INTO student (
                    netid, name, school_year, intro_programming,
                    availability, working_style, interests,
                    semester_goal, submitted_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row["netid"],
                    row["name"],
                    row["school_year"],
                    row["intro_programming"],
                    split_list(row["availability"]),
                    row["working_style"],
                    row["interests"],
                    row["semester_goal"],
                    parse_submitted_at(row["submitted_at"]),
                ),
            )
            cur.execute(
                """
                INSERT INTO skills (
                    netid, skill_programming, skill_data_stats,
                    skill_frontend_design, skill_business_pitch
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    row["netid"],
                    int(row["skill_programming"]),
                    int(row["skill_data_stats"]),
                    int(row["skill_frontend_design"]),
                    int(row["skill_business_pitch"]),
                ),
            )
            for tool_name in split_list(row["tools"]):
                cur.execute(
                    """
                    INSERT INTO tools (netid, tool_name)
                    VALUES (%s, %s)
                    """,
                    (row["netid"], tool_name),
                )
                tools += 1
            students += 1

    return students, students, tools


def main() -> None:
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                apply_schema(cur)
                n_students, n_skills, n_tools = load_rows(cur)
                cur.execute("SET search_path TO class_survey, public")
                cur.execute("SELECT COUNT(*) FROM student")
                student_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM skills")
                skills_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM tools")
                tools_count = cur.fetchone()[0]
        print(
            f"Loaded {n_students} students, {n_skills} skills rows, {n_tools} tools. "
            f"Verified counts: student={student_count}, skills={skills_count}, tools={tools_count}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
