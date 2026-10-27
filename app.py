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


def student_names() -> list[str]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM class_survey.student ORDER BY name"
            )
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


@app.get("/")
def index():
    names = student_names()
    return render_template("students.html", names=names)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
