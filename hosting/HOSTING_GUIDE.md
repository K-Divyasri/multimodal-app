# Publishing VisionQA

This project has two things worth showing the world, and hosting means both. First, a
**GitHub repo a recruiter can open and immediately get** — clean README, a little green
checkmark proving the tests pass on every push. Second — the fun part — an actual **live
web app** anyone can open in a browser: upload a picture, watch the offline features
appear, ask it a question, flip a switch to try a real vision model. No install, no key,
just a URL.

Here's the whole plan, so you know where this is going:

1. **A GitHub repo** — your code, online, public, with a README that lands the project fast.
2. **CI** — GitHub automatically runs your 35 tests on every push. Green check = it works.
3. **A live app** — the Streamlit demo, hosted free, with a public URL you can paste onto a CV.
   It runs keyless by default, so the public demo costs nothing and needs no API key.

One thing about CI that's genuinely rare for an "AI project" and worth calling out up
front: **the whole test suite runs offline, including the tests that exercise the "real"
vision-model code path.** A `conftest.py` fixture installs a fake `litellm` module in
`sys.modules` that returns a fixed, made-up answer — so tests can check that the prompt
gets built correctly, the image gets base64-encoded, and a malformed JSON reply doesn't
crash `extract-table`, all without a real network call. That means CI needs **no API
key, no secrets, and doesn't even need `litellm` installed** to go green. Say so in your
README; it's a selling point. Most "AI projects" can't be tested in CI at all because
they need a paid key. Yours can, honestly, every push.

The real code lives in the `build_from_scratch/` folder. Like the other projects on this
roadmap, the repo root is the **whole project folder** (`20-multimodal-app`), and the
code — package, tests, `app.py`, `requirements.txt` — sits one level down in
`build_from_scratch/`. That's why several paths below carry a `build_from_scratch/`
prefix. This project keeps the Streamlit app directly inside `build_from_scratch/app.py`
(not under a `hosting/streamlit_app/` folder) — so wherever you see `app.py` below, that's
where it lives; there's no separate copy to keep in sync.

---

## Step 0 — Install Git and make a GitHub account

Git is the program that tracks versions of your files. GitHub is the website that stores
a copy online so other people (and recruiters) can see it. Git is the filing system;
GitHub is the shelf you put the folder on so others can reach it.

### Install Git

1. Go to https://git-scm.com/download/win. The download starts on its own.
2. Run the installer. Click Next through every screen — the defaults are fine.
3. Open a **new** PowerShell window (it has to be new so it picks up the install) and check:

```powershell
git --version
```

If you see something like `git version 2.45.0`, you're done.

### Make a GitHub account

1. Go to https://github.com and sign up. Use your real email
   (`mathuransada@gmail.com` is the one on file). Verify it.
2. Pick a username you'd be happy putting on a CV — recruiters see it.

### Tell Git who you are

Do this once per machine:

```powershell
git config --global user.name "Your Name"
git config --global user.email "mathuransada@gmail.com"
```

---

## Step 1 — Know what goes in the repo and what must NOT

Some files belong on GitHub. Some must never leave your laptop. The line between them is
a file called `.gitignore` — a plain-text list of things Git pretends don't exist.
`build_from_scratch/` already ships one. Add a root-level `.gitignore` too (there isn't
one yet, since the repo root is the whole project folder, not `build_from_scratch/`):

```
# 20-multimodal-app/.gitignore (repo root)
.env
build_from_scratch/.env
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/
```

`build_from_scratch/.gitignore` already covers `.env`, `__pycache__/`, `*.pyc`,
`.pytest_cache/`, `.venv/`, `venv/`, `*.egg-info/`, `build/`, `dist/` — confirm it does
before you push.

Here's what matters and why:

- **`.env`** — this is the important one. If you turn on `--real`, your `.env` holds a
  Gemini or Anthropic key. **A key is a password.** Commit it and it's on the public
  internet forever — bots scrape GitHub for leaked keys within minutes of a push, and
  someone else runs up a bill on your account. `.env` never gets committed, ever. The repo
  ships `build_from_scratch/.env.example` instead — variable names, blank values, safe to
  commit, meant to be committed.
- **`data/*.png`** — unlike a generated database, this project's sample images are small
  (six PNGs, a few KB each) and deterministic. You can commit them so the repo works the
  instant someone clones it, or leave them out and have people run `python generate_data.py`
  once (it's one command, and it's already step 2 of the root README). Either is fine;
  just be consistent with what you tell people in your README. This guide assumes you
  commit them, since they're tiny and it means a fresh clone has working sample images
  with zero extra steps.
- **`__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`** — junk Python and pytest
  create as they run. Nobody needs to see it.
- **`.venv/`, `venv/`** — your virtual environment, hundreds of megabytes of installed
  packages specific to your machine. Other people rebuild it from `requirements.txt`.

The rule of thumb: **source code, config, docs, sample data, and tests go in. Secrets and
machine-specific junk stay out.**

---

## Step 2 — Make the local repo and commit

The repo root is the **project folder**, `20-multimodal-app/` — the one that contains
`build_from_scratch/`, `knowledge/`, `notebooks/`, `labs/`, and this `hosting/` folder.
Open PowerShell *there*.

```powershell
git init
git add .
git commit -m "Initial commit: VisionQA -- offline pixel features, real vision Q&A, table-to-CSV stretch goal, Streamlit demo"
```

Then check:

```powershell
git status
git ls-files
```

`git status` should say `nothing to commit, working tree clean`. Scan `git ls-files` and
confirm `.env` is **nowhere** in the list (`.env.example` is fine and expected). If `.env`
shows up, you committed your secret — see the troubleshooting section at the bottom before
you push anything.

---

## Step 3 — Make the empty repo on GitHub and push

### 3a. Create the empty repo

1. Go to github.com, signed in.
2. Top-right, click **+** then **New repository**.
3. Name it `multimodal-app` (or `visionqa`) — lowercase, hyphens, no spaces.
4. Add a one-line description: *"A from-scratch multimodal vision app -- offline pixel
   features and a real vision LLM behind one interface, plus a screenshot-to-CSV table
   extractor."*
5. Leave it **Public**.
6. Do **not** tick "Add a README", "Add .gitignore", or "Add a license" — you need the
   repo completely empty, or your first push collides with what GitHub adds.
7. Click **Create repository**.

### 3b. Connect your local repo to GitHub and push

```powershell
git branch -M main
git remote add origin https://github.com/YOURNAME/multimodal-app.git
git push -u origin main
```

The first push pops up a browser sign-in. Do it. Refresh your GitHub repo page — your
files are there.

---

## Step 4 — Write a README a recruiter will actually read

You've already got the root `README.md` in this folder's parent, written to sell the
project fast: the hook, the offline/real split, the exact run commands, the folder tour,
and a closing line of what you'll be able to say in an interview. Once you deploy (Step
6), come back and add the live URL near the top:

```markdown
**Live demo:** https://YOURNAME-visionqa.streamlit.app
```

### 4a. Add a screenshot — genuinely high value here

A picture proves the app is real and running. Start it locally, upload
`build_from_scratch/data/bright_sky.png`, ask "what color is this?", and capture the
offline metrics tiles plus the answer:

```powershell
cd build_from_scratch
streamlit run app.py
```

Press **Win + Shift + S**, drag a box around the browser window showing the metric tiles
(Size, Orientation, Brightness, Dominant color) and the answer text, paste into Paint,
save as `docs/app_screenshot.png`. Embed it in the root README with:

```markdown
![VisionQA: offline features and an answer for bright_sky.png](docs/app_screenshot.png)
```

That single image — pale blue sky, offline features, the answer "white" sitting right
there — tells the whole story of the project before anyone reads a line of your README.

---

## Step 5 — Add CI so the tests run on every push

CI proves your 35 tests pass on a clean machine too, every time you push, not just on
your laptop. GitHub shows a green checkmark next to commits when they pass.

This project's genuine selling point, worth repeating in your README: **the tests run
offline, including the ones that exercise the real-model code path**, because
`build_from_scratch/conftest.py` installs a fake `litellm` module for those tests. CI
doesn't need `litellm` installed at all, let alone an API key.

Copy the ready-made workflow from this folder into the right spot:

```powershell
mkdir .github\workflows
copy hosting\github_actions\ci.yml .github\workflows\ci.yml
git add .github\workflows\ci.yml
git commit -m "Add GitHub Actions CI to run the 35 tests offline on every push"
git push
```

Open your repo's **Actions** tab. Watch the run: checkout, install Python, install
dependencies, run pytest. Green check means all 35 tests passed on GitHub's machine, with
nothing installed but `Pillow`, `numpy`, and `pytest`, and no API key configured anywhere.

Once it's green, grab the status badge: on the workflow's Actions page, the `...` menu has
**Create status badge** — paste the markdown it gives you at the top of your root
`README.md`.

---

## Step 6 — Deploy the offline Streamlit app

This is the payoff. `build_from_scratch/app.py` already runs keyless by default — it
computes the offline features locally and only calls a real model if you tick the sidebar
checkbox and paste in a key for that session. That's exactly what makes it free and safe
to host publicly: a stranger opening your link can play with the whole offline experience
— upload an image, see the metrics, ask a question, try the table extractor — and never
cost you a cent, because nothing calls out to a paid API unless *they* supply their own
key in the sidebar.

**Try it locally first.** If it runs on your laptop, it'll run hosted:

```powershell
cd build_from_scratch
pip install -r requirements.txt
streamlit run app.py
```

It opens a browser tab at `http://localhost:8501`. Upload one of the sample PNGs from
`data/` and confirm the metrics and the "Ask" button both work before you deploy.

### 6a. Streamlit Community Cloud (easiest, since your code is already on GitHub)

1. Go to https://docs.streamlit.io/deploy/streamlit-community-cloud and sign in with
   GitHub (or go straight to https://share.streamlit.io).
2. Click **New app**, then **Deploy a public app from GitHub**.
3. Pick your `multimodal-app` repo and the `main` branch.
4. Set **Main file path** to `build_from_scratch/app.py` — this is the field people get
   wrong most often. The app lives one level down, not at the repo root.
5. Click **Deploy**. Streamlit reads `build_from_scratch/requirements.txt` automatically,
   installs `Pillow`, `numpy`, and `streamlit`, builds, and gives you a public
   `*.streamlit.app` URL.

That URL is your live app. Because it's offline by default, it works for any visitor
instantly — no key, no setup.

**The one gotcha worth understanding — imports.** `app.py` does `from visionqa import qa,
tables`, so Python has to find the `visionqa` package. The app itself already handles
this: its first real line is

```python
sys.path.insert(0, str(Path(__file__).parent))
```

which adds the app's own folder — `build_from_scratch/` — to the import path, right where
`visionqa/` sits next to `app.py`. Since you pointed Streamlit Cloud at
`build_from_scratch/app.py`, this resolves cleanly with no extra work on your part.

**One dependency note.** `build_from_scratch/requirements.txt` lists `litellm` as an
optional, commented-out line (only needed for `--real`). If you never uncomment it,
Streamlit Cloud simply won't have `litellm` installed — which is fine, because the sidebar
checkbox only sets `GEMINI_API_KEY`/routes through `qa.ask(..., offline=False)`, and if
you ever *do* want the hosted app's real-model toggle to work, uncomment `litellm>=1.0` in
`requirements.txt` before deploying (or after — Streamlit Cloud rebuilds automatically
when you push a change).

### 6b. Or — Hugging Face Spaces

Hugging Face **Spaces** also hosts Streamlit apps free.

1. Make a free account at https://huggingface.co.
2. Click **New Space**. Name it `visionqa`, pick **Streamlit** as the SDK, leave it public.
3. A Space *is* a Git repo. A Space expects the app at a top-level `app.py` and a
   top-level `requirements.txt`. The simplest way to fit that shape without duplicating
   your app: at the Space's root, add a tiny one-line entry point and a
   `requirements.txt`:

   ```python
   # app.py -- entry point for Hugging Face Spaces; runs the real app.
   import runpy, sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent / "build_from_scratch"))
   runpy.run_path("build_from_scratch/app.py", run_name="__main__")
   ```

   and a top-level `requirements.txt` with at least `streamlit`, `Pillow`, `numpy` (copy
   the non-comment lines from `build_from_scratch/requirements.txt`).

4. Push your project to the Space's Git remote (it gives you the URL), or use the web UI
   to upload the files. The Space builds and gives you a public URL like
   `https://huggingface.co/spaces/YOURNAME/visionqa`.

Streamlit Cloud (6a) is less fiddly because it points straight at
`build_from_scratch/app.py` and needs no wrapper file. Use it unless you specifically want
a Space.

### 6c. If you want the hosted app to call a REAL model by default

The safe default needs no secret — a visitor supplies their own key in the sidebar if they
want to try `--real` there. If instead *you* want the hosted app to have a working key of
your own (so, say, a recruiter can try the real path without owning a Gemini account),
add it as a host **Secret** — never in code, never in the repo.

- **Streamlit Cloud:** open the app's **Settings → Secrets**:

  ```toml
  GEMINI_API_KEY = "AIzaSyD-your-actual-secret-key-here"
  ```

- **Hugging Face:** the Space's **Settings → Secrets and variables**, add `GEMINI_API_KEY`.

Either way, `os.environ` picks it up at runtime — `visionqa.qa.has_api_key()` checks
`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, and `OPENAI_API_KEY` — and your
public repo never contains the key.

**A word on cost.** Get a free Gemini key in about 30 seconds at
https://aistudio.google.com/apikey — the free tier is plenty for a public demo. If you
switch `VISION_MODEL` to Claude, `anthropic/claude-haiku-4-5` ($1/$5 per 1M tokens) is the
cheap option; `anthropic/claude-opus-4-8` ($5/$25 per 1M) is the best vision quality but
not what you want a stranger's clicks running up. Think carefully before putting a real
key in a public app's Secrets at all — every visitor who ticks the sidebar box and doesn't
supply their own key would spend *your* key's quota. For a portfolio demo, the honest
default (a visitor brings their own key, or just explores the offline half) is usually the
right call.

### 6d. Link the demo from your README

Once it's live:

```markdown
**Live demo:** https://YOURNAME-visionqa.streamlit.app
```

A clickable app that turns a pale blue picture into an offline "white" and a real "light
blue" side by side, plus a green CI badge, is a genuinely strong portfolio page.

---

## Step 7 — Pin the repo on your profile

1. Go to your profile page (`github.com/YOURNAME`).
2. Find **Customize your pins** (or **Pin** on a repo card).
3. Tick `multimodal-app`. Save.

---

## Common Git mistakes (troubleshooting)

**You committed `.env` by accident.** Treat the key as compromised — revoke/rotate it at
the provider (Google AI Studio or Anthropic console) — then:

```powershell
git rm --cached build_from_scratch\.env
git commit -m "Remove committed .env"
git push
```

Confirm `.env` is in both `.gitignore` files so it doesn't come back. `git rm --cached`
only stops future tracking — the key still sits in Git history, which is exactly why you
rotate it rather than relying on deletion.

**`error: failed to push` / push rejected.** The remote has commits your local repo
doesn't — usually because you let GitHub add a README when creating the repo.

```powershell
git pull origin main --rebase
git push
```

Next time, create the repo completely empty.

**Authentication fails on push.** GitHub no longer accepts your account password in the
terminal. Easiest fix: install the GitHub CLI from https://cli.github.com, run
`gh auth login`, follow the browser prompts. Or generate a Personal Access Token
(**Settings → Developer settings → Personal access tokens**) and paste it as the password.

**CI is red but the tests pass on my laptop.** Read the Actions log bottom-up. The usual
cause is a dependency you have installed locally but forgot to list in
`build_from_scratch/requirements.txt`. It won't be a missing API key — the tests are
offline by design, with a fake `litellm` standing in where needed.

**The deployed app shows `ModuleNotFoundError: visionqa`.** Make sure the **Main file
path** on Streamlit Cloud is `build_from_scratch/app.py`, not just `app.py`, so the app's
own folder — where `visionqa/` lives — lands on the import path.

**The deployed app can't find sample images.** That's expected if you didn't commit
`build_from_scratch/data/`. Either commit the six PNGs (they're small — see Step 1), or
tell visitors to upload their own image; the app works either way since it only ever reads
whatever file the uploader gives it.
