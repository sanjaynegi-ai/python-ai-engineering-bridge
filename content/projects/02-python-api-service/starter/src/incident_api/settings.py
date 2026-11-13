"""Application settings, from INCIDENT_* environment variables and an optional .env file.

Workbook Milestone 3: define `class Settings(BaseSettings)`.

    input_dir    Path, default data/exports
    output_file  Path, default out/report.json
    sla_hours    dict of Priority to a positive int, default P1=4, P2=24, P3=72, P4=168

Read INCIDENT_INPUT_DIR, INCIDENT_OUTPUT_FILE and INCIDENT_SLA_HOURS (JSON) from the
environment and from ./.env; the environment wins. Instances are frozen.
A model validator rejects sla_hours unless it covers P1 to P4 and strictly
increases from P1 to P4.
"""
