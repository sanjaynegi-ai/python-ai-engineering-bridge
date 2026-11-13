"""Domain objects: tickets, rejections and configuration.

Workbook Milestone 2: define three frozen dataclasses here.

Ticket
    Fields, in this order: id, title, team, priority, status, age_hours,
    assignee (default None), tags (a tuple of strings, default empty).
    - Ticket.from_record(record): a classmethod that builds a normalised Ticket
      from a raw record that has already passed validation. It does what your
      Session 02 normalise_ticket did, but tags become a tuple.
    - is_open: a read-only property, True unless status is in CLOSED_STATUSES.
    - is_breached(sla_hours): True if open and older than the SLA for its priority.

Rejection
    Fields: file, record (index or None), id (or None), problems (a tuple of messages).
    - to_dict(): a JSON-ready dict with the same keys; problems as a list.

Config
    Fields: input_dir (Path), output_file (Path), sla_hours (dict of str to int).
"""

CLOSED_STATUSES = frozenset({"resolved", "closed"})
