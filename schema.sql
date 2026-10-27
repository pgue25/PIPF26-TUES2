-- PostgreSQL schema for class_dataset.csv
-- Three tables: student, skills, tools. No survey rows are loaded here.

BEGIN;

CREATE SCHEMA IF NOT EXISTS class_survey;
SET search_path TO class_survey, public;

CREATE TYPE school_year AS ENUM ('Sophomore', 'Junior', 'Senior');

CREATE TYPE intro_programming AS ENUM ('took_it', 'equivalent', 'neither');

CREATE DOMAIN skill_rating AS SMALLINT
  CHECK (VALUE BETWEEN 1 AND 5);

CREATE TABLE student (
  netid             VARCHAR(8) PRIMARY KEY
                    CHECK (netid ~ '^[A-Za-z]{1,3}[0-9]{4,5}$'),
  name              TEXT NOT NULL,
  school_year       school_year NOT NULL,
  intro_programming intro_programming NOT NULL,
  availability      TEXT[] NOT NULL,
  working_style     TEXT NOT NULL,
  interests         TEXT NOT NULL,
  semester_goal     TEXT NOT NULL,
  submitted_at      TIMESTAMPTZ NOT NULL
);

CREATE TABLE skills (
  netid                 VARCHAR(8) PRIMARY KEY
                        REFERENCES student (netid) ON DELETE CASCADE,
  skill_programming     skill_rating NOT NULL,
  skill_data_stats      skill_rating NOT NULL,
  skill_frontend_design skill_rating NOT NULL,
  skill_business_pitch  skill_rating NOT NULL
);

CREATE TABLE tools (
  netid     VARCHAR(8) NOT NULL
            REFERENCES student (netid) ON DELETE CASCADE,
  tool_name TEXT NOT NULL
            CHECK (tool_name IN (
              'Python',
              'JavaScript',
              'SQL',
              'Excel',
              'R',
              'none yet'
            )),
  PRIMARY KEY (netid, tool_name)
);

CREATE INDEX student_school_year_idx ON student (school_year);
CREATE INDEX student_submitted_at_idx ON student (submitted_at);
CREATE INDEX tools_tool_name_idx ON tools (tool_name);

COMMENT ON TABLE student IS
  'One row per survey response. Availability stays here as the CSV slot labels.';
COMMENT ON TABLE skills IS
  'One-to-one with student: the four 1–5 self-ratings from the CSV.';
COMMENT ON TABLE tools IS
  'One row per tool a student selected (semicolon-separated tools column).';

COMMIT;
