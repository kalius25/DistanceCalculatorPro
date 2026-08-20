# Sprint 3.8 — Multi-Provider Regression & RC Integration

Sprint 3.8 freezes feature development and hardens v1.3 for release.

Changes:

- version promoted from `1.3.0-rc1` to `1.3.0-rc2`;
- deterministic provider regression matrix added;
- one-session GUI regression harness covers all 9 provider/mode cases;
- duration capability is validated per provider;
- VietBanDo error strings cannot count as successful distance values;
- RC2 live-regression PowerShell gate added;
- RC2 release checklist added.

The live regression is intentionally separate from `build_rc.ps1` because it
depends on external map websites and internet availability.
