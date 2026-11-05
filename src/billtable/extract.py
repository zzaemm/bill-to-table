"""Photo of a bill -> validated Bill, using Gemini's structured (schema-constrained) output."""
import io
import os

from PIL import Image

from .schema import Bill

PROMPT = (
    "Extract this bill/receipt into the given schema. Copy numbers exactly as printed. "
    "Use null for anything you cannot read; never invent values. One entry per line item."
)


def prepare_image(data: bytes, max_side: int = 1600) -> bytes:
    """Downscale big phone photos and re-encode as JPEG to keep requests small and fast."""
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=88)
    return out.getvalue()


def extract_bill(image_bytes: bytes, call_model=None) -> Bill:
    call_model = call_model or _gemini
    raw_json = call_model(prepare_image(image_bytes))
    return Bill.model_validate_json(raw_json)


def _gemini(jpeg: bytes) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[types.Part.from_bytes(data=jpeg, mime_type="image/jpeg"), PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json", response_schema=Bill, temperature=0
        ),
    )
    return resp.text
