#!/usr/bin/env python3
"""Serve a page listing student names from the class survey database."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

app = Flask(__name__)


SKILL_COLUMNS = (
    ("Programming", "skill_programming"),
    ("Data and stats", "skill_data_stats"),
    ("Frontend design", "skill_frontend_design"),
    ("Business pitch", "skill_business_pitch"),
)


def connect():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(database_url)


def student_names() -> list[str]:
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM class_survey.student ORDER BY name"
            )
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def skill_averages() -> list[dict]:
    """Average each 1–5 skill rating across all survey responses."""
    select_list = ", ".join(
        f"ROUND(AVG({column})::numeric, 2)" for _, column in SKILL_COLUMNS
    )
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {select_list} FROM class_survey.skills")
            row = cur.fetchone()
    finally:
        conn.close()

    averages = []
    for (label, _), value in zip(SKILL_COLUMNS, row):
        averages.append(
            {
                "label": label,
                "average": None if value is None else float(value),
            }
        )
    return averages


@app.get("/")
def index():
    names = student_names()
    averages = skill_averages()
    return render_template(
        "students.html", names=names, skill_averages=averages
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(host="0.0.0.0", port=port)
