# Deploy checklist — VisionQA

This is the project's "definition of done." Walk it top to bottom. Don't tick a box you
haven't actually verified by running the command — "should work" isn't the same as "works."

## Runs locally

- [ ] Fresh virtual environment, dependencies installed cleanly (from the repo root):
      `python -m venv .venv ; .\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt`
- [ ] Sample data exists: `python generate_data.py` writes 6 PNGs to `data/`
      (`bright_sky.png`, `dark_night.png`, `forest_green.png`, `solid_orange.png`,
      `checkerboard.png`, `receipt_table.png`).
- [ ] The CLI works offline, no key:
      `python -m visionqa describe data\bright_sky.png` prints a summary calling it "white."
      `python -m visionqa ask data\forest_green.png "what color is this?"` says "green."
- [ ] The stretch goal works offline:
      `python -m visionqa extract-table data\receipt_table.png --out table.csv` detects a
      4-row by 3-column grid and writes `table.csv`.
- [ ] `--real` with no key soft-fails instead of crashing:
      `python -m visionqa ask data\bright_sky.png "what color is the sky?" --real` prints
      `[no API key found - falling back to offline mode]` and still answers.
- [ ] The Streamlit app runs offline in a browser:
      `streamlit run app.py` opens `http://localhost:8501`; uploading a sample image shows
      the four metric tiles (size, orientation, brightness, dominant color) and answers a
      question with no key set.
- [ ] (Optional) with a free Gemini key in `.env`, `--real` gives a genuinely different,
      correct answer on `bright_sky.png` ("light blue" instead of "white").

## Tests pass

- [ ] `pytest` run from the repo root is all green (35 tests, all offline, no key,
      no network — including the ones that exercise the `--real` code path via the fake
      `litellm` fixture in `conftest.py`).
- [ ] You ran it in the fresh venv, not just your everyday one, so you know the deps are complete.

## README is recruiter-ready

- [ ] The root `README.md` covers: the hook, the offline/real split, the exact run
      commands, the folder tour, and what you'll be able to say in an interview.
- [ ] A screenshot of the app (metric tiles + an answer, ideally on `bright_sky.png`) is
      embedded, e.g. `docs/app_screenshot.png`.
- [ ] The live demo URL is near the top (add it after deploying).
- [ ] The CI status badge is at the top.

## Secrets are clean

- [ ] The repo-root `.gitignore` contains `.env`, `.venv/`, `__pycache__/`,
      `.pytest_cache/`, `*.egg-info/`.
- [ ] `git status` shows `.env` is NOT tracked.
- [ ] `git ls-files` output contains NO `.env` (only `.env.example`). If it's there,
      remove it — see the hosting guide's troubleshooting section — and rotate the key.
- [ ] No API key is hardcoded anywhere in the source.

## Sample data generated and committed (or regenerated on deploy)

- [ ] Either: the 6 PNGs in `data/` are committed to the repo (they're
      small and deterministic, so this is the simplest choice for a working fresh clone), OR
      the README clearly tells anyone who clones to run `python generate_data.py` first.
- [ ] Whichever you chose, a fresh clone (or the deployed app) actually has working sample
      images — you verified this by testing with at least one, not just assuming it.

## Pushed to GitHub

- [ ] Repo created empty on github.com (no auto README/license), named `multimodal-app`
      (or `visionqa`), public.
- [ ] `git init` → `git add .` → `git commit` → `git branch -M main` →
      `git remote add origin ...` → `git push -u origin main` all done (from the project root).
- [ ] Files visible on the GitHub repo page after a refresh.

## CI is green

- [ ] `.github/workflows/ci.yml` (copied from `hosting/github_actions/ci.yml`) is
      committed and pushed.
- [ ] The Actions tab shows a completed run with a green checkmark.
- [ ] The run used NO secrets and did NOT install `litellm` or `streamlit` — confirm it
      passed with only `Pillow`, `numpy`, and `pytest` installed. That's a selling point;
      mention it in the README.
- [ ] If it was red, you read the log and fixed the cause, then re-ran to green.

## App tested with at least one sample image

- [ ] Deployed free to Streamlit Community Cloud (main file path
      `app.py`) or Hugging Face Spaces.
- [ ] Opening the public URL loads the page with no errors.
- [ ] You personally uploaded (or the app already has committed) at least one sample
      image — `bright_sky.png` is the best choice — and confirmed the metrics tiles and
      the "Ask" answer both render correctly for a stranger with no key.
- [ ] (Only if you enabled a hosted real-model key) it's set as a host **Secret**
      (`GEMINI_API_KEY`) — never in code — and you understand every visitor who ticks the
      sidebar box without their own key spends *your* quota.
- [ ] The live demo URL is added to the top of the README.

## Repo pinned

- [ ] `multimodal-app` is pinned on your GitHub profile so it shows up first.

When every box is ticked, the project is done and presentable. Send the repo link with
confidence.
