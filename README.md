# Multimodal App

A small multimodal (vision) app in plain Python. Upload an image, get an
offline description, ask it a question, or turn a screenshot of a table into
a CSV. No API key required for any of that.

## What's inside

```
visionqa/
  imaging.py    load an image file into a numpy array; encode one as base64 for an LLM
  features.py   pixel-level features: brightness, orientation, dominant color, edge density
  qa.py         answer a question -- offline (rule-based) or real (a vision LLM via LiteLLM)
  tables.py     the stretch goal: detect a table's grid offline, or transcribe it for real
  cli.py        `python -m visionqa ...`
tests/          35 pytest tests, all offline
data/           6 hand-built sample images (generate_data.py), numbers verified exactly
app.py          Streamlit demo
```

## Run it

```powershell
# from this folder
pip install -r requirements.txt
python generate_data.py                 # writes the 6 sample images to data/

python -m visionqa describe data\bright_sky.png
python -m visionqa ask data\forest_green.png "what color is this?"
python -m visionqa extract-table data\receipt_table.png
python -m visionqa extract-table data\receipt_table.png --out table.csv

streamlit run app.py                    # the web demo

pytest -q                               # 35 tests, no key, no network
```

## The lesson, in one image

`data/bright_sky.png` is a pale, light-blue rectangle. A person calls it "a
light blue sky." The offline backend calls it **white** -- because nearest-
palette color naming snaps pale colors to the closest saturated hue, and
white is genuinely the closest of the ten colors it knows. That is not a bug
we forgot to fix. It is the honest limit of pixel statistics, and it is
exactly the gap a real vision model closes:

```powershell
python -m visionqa ask data\bright_sky.png "what color is the sky?" --real
```

With a key set, the real backend actually looks at the picture and answers
correctly. Without one, `--real` prints a note and falls back to offline
rather than crashing.

## Going real

```powershell
copy .env.example .env      # then put a key in it (Gemini free tier is fine)
python -m visionqa ask data\receipt_table.png "what is the total?" --real
python -m visionqa extract-table data\receipt_table.png --real
```

`VISION_MODEL` picks the model: `gemini/gemini-1.5-flash` (free, default),
`anthropic/claude-opus-4-8` (best vision quality), or any LiteLLM-supported
vision-capable string.
