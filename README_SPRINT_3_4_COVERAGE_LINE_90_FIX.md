# Sprint 3.4 — Coverage line 90 fix

Adds one focused unit test for the blank-line branch in
`route_text_parser._summary_line()`.

Target:
- `app/parsers/route_text_parser.py`
- uncovered branch at the `for raw_line in text.splitlines()` loop / blank-line
  `continue` path around line 90.

No production logic changed.
