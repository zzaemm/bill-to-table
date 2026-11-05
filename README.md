# Bill to Table

Take a photo of a bill or receipt and get a clean, checked table you can download as CSV.

**Live demo:** _add your Streamlit Cloud link here after deploying_

## How it works

1. **Prepare:** the photo is downscaled and re-encoded as JPEG so phone pictures stay fast to upload.
2. **Extract:** Gemini reads the image with *schema-constrained output*. The Pydantic `Bill` model is passed as the response schema, so the model must return valid JSON in the exact shape (vendor, date, line items, subtotal, tax, total).
3. **Validate:** vision models sometimes misread digits, so the app checks the arithmetic and warns on mismatches:
   - quantity x unit price vs line amount
   - sum of line items vs subtotal
   - subtotal + tax vs total
4. **Export:** the table is shown on screen and downloadable as CSV.

```
photo -> resize -> Gemini (JSON schema) -> Pydantic validation -> arithmetic checks -> table + CSV
```

## Run it locally

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key      # free key from https://aistudio.google.com
streamlit run app.py
```

## Tests

```bash
pytest -q
```

Tests use a fake model call and generated images, so they need no API key. They cover schema rules, each arithmetic check, image preparation, malformed model output, and CSV export.

## Deploy free

Push to GitHub, create an app on [Streamlit Community Cloud](https://streamlit.io/cloud) pointing at `app.py`, and add `GEMINI_API_KEY` under *Secrets*.

## Design choices

- **Structured output instead of prompt-and-parse:** the schema is enforced, so there is no regex cleanup of free-form text.
- **Trust but verify:** extracted numbers are checked, and problems are shown to the user instead of hidden.
- **`null` over guessing:** the prompt tells the model to return null for unreadable fields.

## Limitations

- Handwritten or heavily crumpled bills lower accuracy; the validation warnings are there to catch this.
- Multi-page bills are processed one image at a time.

## License

MIT
