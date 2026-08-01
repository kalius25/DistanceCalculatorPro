# Sprint 1E.1 — URL-first Google Maps Batch Navigation

## Objective

Use a complete Google Maps directions URL and keep one browser alive for an entire batch.

## Flow

1. Start browser once.
2. Build `/maps/dir/{origin}/{destination}/`.
3. Create a new page for the request.
4. Navigate with `wait_until="domcontentloaded"`.
5. Wait for the first route card.
6. Parse routes.
7. Close the request page.
8. Close browser after the batch.
