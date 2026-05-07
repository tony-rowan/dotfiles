"""
Gemini Image Generation Module
Pre-built module for the generate-image skill — handles session management,
multi-turn conversations, and output saving.

Session and outputs are stored under ~/.generate-image/.
File naming: generate-image_{stamp}_t{turn:02d}[_v{variety}].png
  stamp     — set once per session (YYYYMMDD_HHMMSS), shared across varieties
  turn      — increments with each generate() call in a session
  variety   — optional integer suffix for parallel variants of the same prompt
"""
import os
import json
import base64
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

GENERATE_IMAGE_DIR = Path.home() / ".generate-image"
SESSION_FILE = str(GENERATE_IMAGE_DIR / "session.json")
OUTPUT_DIR = str(GENERATE_IMAGE_DIR / "outputs")
DEFAULT_MODEL = "gemini-3-pro-image-preview"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_RESOLUTION = "1K"


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment.\n"
            "Add it to ~/.machine-config (sourced by your .zshrc):\n"
            "  export GEMINI_API_KEY=your_key_here\n"
            "Then run: source ~/.machine-config"
        )
    return genai.Client(api_key=api_key)


def _ensure_dirs():
    GENERATE_IMAGE_DIR.mkdir(exist_ok=True)
    Path(OUTPUT_DIR).mkdir(exist_ok=True)


def _load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"history": [], "outputs": [], "turn": 0, "session_stamp": None}


def _reconstruct_history(raw_history):
    """Convert serialised history back to types.Content objects."""
    reconstructed = []
    for item in raw_history:
        parts = []
        for part_data in item.get("parts", []):
            if "text" in part_data:
                kwargs = {"text": part_data["text"]}
                if "thought_signature" in part_data:
                    kwargs["thought_signature"] = base64.b64decode(part_data["thought_signature"])
                parts.append(types.Part(**kwargs))
            elif "inline_data" in part_data:
                blob = types.Blob(
                    mime_type=part_data["inline_data"]["mime_type"],
                    data=base64.b64decode(part_data["inline_data"]["data"]),
                )
                kwargs = {"inline_data": blob}
                if "thought_signature" in part_data:
                    kwargs["thought_signature"] = base64.b64decode(part_data["thought_signature"])
                parts.append(types.Part(**kwargs))
        reconstructed.append(types.Content(role=item.get("role"), parts=parts))
    return reconstructed


def _save_session(session):
    _ensure_dirs()
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f)


def _get_output_path(session, stamp=None, variety=None):
    _ensure_dirs()
    turn = session.get("turn", 0) + 1
    if stamp is None:
        stamp = session.get("session_stamp") or datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{OUTPUT_DIR}/generate-image_{stamp}_t{turn:02d}"
    if variety is not None:
        base += f"_v{variety}"
    return f"{base}.png"


def new_session():
    """Clear the current session and start fresh."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    print("Session cleared. Ready for new image generation.")
    return {"history": [], "outputs": [], "turn": 0, "session_stamp": None}


def session_info():
    """Display current session status."""
    session = _load_session()
    turn_count = session.get("turn", 0)
    outputs = session.get("outputs", [])

    if turn_count == 0:
        print("No active session.")
        return None

    stamp = session.get("session_stamp", "unknown")
    print(f"Session: {stamp} — {turn_count} turn(s)")
    print("Outputs:")
    for i, output in enumerate(outputs, 1):
        print(f"  {i}. {output}")

    return session


def revert(turns: int = 1):
    """Undo the last N turns from the current session."""
    session = _load_session()
    turn_count = session.get("turn", 0)

    if turn_count == 0:
        print("No active session to revert.")
        return None

    if turns > turn_count:
        print(f"Can only revert {turn_count} turn(s). Reverting all.")
        turns = turn_count

    session["history"] = session["history"][: -(turns * 2)]
    session["outputs"] = session["outputs"][:-turns]
    session["turn"] = turn_count - turns

    if session["turn"] == 0:
        session["session_stamp"] = None

    _save_session(session)

    if session["turn"] == 0:
        print(f"Reverted {turns} turn(s). Session is now empty.")
    else:
        print(f"Reverted {turns} turn(s). Now at turn {session['turn']}.")
        if session["outputs"]:
            print(f"Last output: {session['outputs'][-1]}")

    return session


def generate(
    prompt: str,
    reference_images: list = None,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    resolution: str = DEFAULT_RESOLUTION,
    model: str = DEFAULT_MODEL,
    stamp: str = None,
    variety: int = None,
) -> str:
    """
    Generate or refine an image. Automatically continues an existing session.

    Args:
        prompt:           Text description of what to generate or change.
        reference_images: Optional list of image file paths to use as references.
        aspect_ratio:     "1:1", "16:9", "9:16", "3:4", etc.
        resolution:       "1K", "2K", or "4K".
        model:            Gemini model name.
        stamp:            Override the session timestamp (use for variety batches so
                          all variants share the same stamp).
        variety:          Append _v{variety} to the output filename.

    Returns:
        Path to the saved image, or None if no image was returned.
    """
    client = _get_client()
    session = _load_session()

    if not session.get("session_stamp"):
        session["session_stamp"] = stamp or datetime.now().strftime("%Y%m%d_%H%M%S")

    content_parts = [prompt]

    if reference_images:
        from PIL import Image

        for img_path in reference_images:
            if os.path.exists(img_path):
                content_parts.append(Image.open(img_path))
            else:
                print(f"Warning: reference image not found: {img_path}")

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspectRatio=aspect_ratio),
    )

    if session["history"]:
        print(f"Continuing session (turn {session['turn'] + 1})...")
        chat = client.chats.create(
            model=model,
            config=config,
            history=_reconstruct_history(session["history"]),
        )
        response = chat.send_message(content_parts)
    else:
        print("Starting new session...")
        chat = client.chats.create(model=model, config=config)
        response = chat.send_message(content_parts)

    session["history"].append({"role": "user", "parts": [{"text": prompt}]})

    output_path = None
    response_parts = []

    for part in response.parts:
        if part.text is not None:
            print(f"Model: {part.text}")
            part_data = {"text": part.text}
            if hasattr(part, "thought_signature") and part.thought_signature:
                part_data["thought_signature"] = base64.b64encode(
                    part.thought_signature
                ).decode("utf-8")
            response_parts.append(part_data)
        elif part.inline_data is not None:
            output_path = _get_output_path(session, stamp=stamp, variety=variety)
            part.as_image().save(output_path)
            print(f"Saved: {output_path}")

            part_data = {
                "inline_data": {
                    "mime_type": part.inline_data.mime_type,
                    "data": base64.b64encode(part.inline_data.data).decode("utf-8"),
                }
            }
            if hasattr(part, "thought_signature") and part.thought_signature:
                part_data["thought_signature"] = base64.b64encode(
                    part.thought_signature
                ).decode("utf-8")
            response_parts.append(part_data)

    session["history"].append({"role": "model", "parts": response_parts})
    session["turn"] = session.get("turn", 0) + 1
    if output_path:
        session["outputs"].append(output_path)

    _save_session(session)
    return output_path


def gen(prompt, **kwargs):
    """Shorthand for generate()."""
    return generate(prompt, **kwargs)


if __name__ == "__main__":
    print("generate-image image_gen module loaded.")
    print("Functions: generate(), new_session(), session_info(), revert()")
