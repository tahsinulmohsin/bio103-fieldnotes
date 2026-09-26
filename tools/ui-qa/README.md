# UI QA

Browser checks for the app, kept apart from the app's own dependencies.

```sh
cd tools/ui-qa
npm install
npx playwright install chromium
BASE_URL=http://localhost:3103 npm run capture      # screenshots + results.json (overflow, text size, targets, axe)
BASE_URL=http://localhost:3103 npm run measure      # Read spread fits above the bar at laptop and phone sizes
BASE_URL=http://localhost:3103 npm run screenshots  # regenerate docs/screenshots for the README
```

Start the app first (`npm run build && npm start` in the repository root). `CHROMIUM_PATH` points Playwright at a specific Chromium build if the bundled one is not installed. `review-capture.mjs` expects the Fall 2026 "cells" and "circulation" lectures.
