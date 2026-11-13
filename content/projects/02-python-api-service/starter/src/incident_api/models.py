"""Pydantic models: incoming tickets, rejections, and the report.

Workbook Milestones 2, 4 and 5. Every model below is described in the workbook.
"""

from typing import Literal

Priority = Literal["P1", "P2", "P3", "P4"]
CLOSED_STATUSES = frozenset({"resolved", "closed"})

# Milestone 2: class Ticket(BaseModel)
#   Fields, validation and cleaning rules: see the workbook's table.
#   Keep is_open (a property) and is_breached(sla_hours) from Project 01.

# Milestone 4: class Rejection(BaseModel)
#   file, record (default None), id (default None), problems (list of str),
#   and the classmethod from_validation_error(error, *, file, record, raw).

# Milestone 5: the report models
#   Totals, TeamStats, Breach, TagCount and Report, with the same field names
#   as the Project 01 report.
