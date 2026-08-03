# Sprint 2.4.4 — Production Diagnostics & Support Bundle

Adds privacy-safe support bundle export from **Help → Export Support Bundle...**.

The bundle contains a manifest, runtime information, sanitized text logs and
sanitized diagnostics JSON/text. Source workbooks are never collected. HTML and
screenshots are excluded by default because they can contain customer routes or
other sensitive visual data.

Default limits:

- 25 MiB final ZIP size
- 2 MiB per source artifact
- 100 collected artifacts

All writes use a temporary archive followed by atomic replacement. Failed or
cancelled exports do not leave partial ZIP files behind.
