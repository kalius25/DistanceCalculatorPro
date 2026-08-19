# Sprint 3.7A — Test alignment

Three presentation tests were still based on the pre-VietBanDo provider UI.

Updates:

- Provider selector now expects four entries, including VietBanDo.
- The synthetic foundation-only provider advertises Driving so validation
  reaches the intended foundation branch instead of the unsupported-mode guard.
- The missing-travel-mode test clears the combo with signals blocked and then
  calls validation directly. This tests the empty-mode branch without the new
  provider-mode synchronization immediately repopulating the selector.

Production code is unchanged by this fix.
