# Slotwise — Exam Timetable Scheduler

A self-contained browser demo for exam timetable scheduling with conflict graphs.

## Run locally

Open `index.html` in a modern browser. No build step or dependencies are required.

## Publish with GitHub Pages

1. Create a new GitHub repository.
2. Upload the contents of this folder (`index.html` and `README.md`) to the repository root.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
5. GitHub will show the published site URL in the Pages section after deployment.

The exact branch-and-bound solver has an 8-second limit per run and reports when it cannot prove optimality within that limit.
