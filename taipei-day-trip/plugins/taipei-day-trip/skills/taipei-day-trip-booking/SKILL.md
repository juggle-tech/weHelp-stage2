---
name: taipei-day-trip-booking
description: "Search Taipei attractions by keyword and, after confirmation, add a selected attraction to the authenticated user's cart. Use for Taipei attraction discovery and booking requests."
---

# Taipei Daytrip

Use this skill when the user wants to search Taipei attractions or book an attraction tour.

## Search attractions

1. Ask the user to provide a search keyword if they have not already provided one.
2. Call the `搜尋台北市景點` tool with the user's keyword.
3. Render the returned attractions clearly. Include at least each attraction's `id` and `name`; include `description` when available.
4. If no attractions are returned, tell the user and ask for another keyword.

## Create a booking

1. Ask the user whether they would like to book one of the displayed attractions. Do not create a booking without an affirmative answer.
2. Collect these required values through natural-language conversation:
   - Attraction ID
   - Date
   - Time
3. Normalize the collected values before calling the tool:
   - `id`: integer, for example `12`
   - `date`: `YYYY-MM-DD`, for example `2026-09-20`
   - `time`: either `早上` or `下午`
4. If the user gives a date such as “明天” or “下週日”, convert it to an exact `YYYY-MM-DD` date. Ask for clarification if the date cannot be determined safely.
5. Convert equivalent time expressions to the supported values:
   - morning / 上午 → `早上`
   - afternoon / 下午 → `下午`
6. Before creating the booking, show the normalized attraction ID, date, and time, and ask the user to confirm them.
7. After confirmation, call `預訂景點導覽行程` with `id`, `date`, and `time`.
8. On success, tell the user the booking was added to the cart and provide the link to complete ordering.
9. On failure, report that the booking could not be created. Do not claim it was successful.
