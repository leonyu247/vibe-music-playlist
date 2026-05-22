import json
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from groq import Groq

# NOTE: The Groq API key in use is a permanent key with no expiry date.

_PROMPT_TEMPLATE = """You are a music expert and playlist curator. A user described a vibe: "{vibe}"

First, determine if this is a recognizable mood, scene, activity, or atmosphere suitable for a playlist.
If the input is gibberish, random characters, or completely uninterpretable, return:
{{"error": "not_a_vibe", "message": "That doesn't look like a vibe. Try describing a mood, scene, or feeling."}}

Otherwise, create a playlist that perfectly captures this vibe. Return a JSON object with exactly these fields:
- playlist_name: creative, short playlist name (max 40 characters)
- description: one evocative sentence describing the vibe
- tracks: array of exactly 20 objects, each with:
  - title: exact song title as it appears on Spotify
  - artist: exact primary artist name as it appears on Spotify

Rules:
- Choose only real, existing songs available on Spotify
- Vary the artists — do not repeat the same artist more than twice
- Match the mood, energy, tempo, and atmosphere of the vibe closely
- Mix well-known tracks with deeper cuts for variety
"""

_TIMEOUT_SECONDS = 30


def get_playlist_from_vibe(vibe: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompt = _PROMPT_TEMPLATE.format(vibe=vibe)

    def _call():
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_call)
        try:
            result = future.result(timeout=_TIMEOUT_SECONDS)
        except FuturesTimeoutError:
            raise TimeoutError(f"Playlist generation timed out after {_TIMEOUT_SECONDS} seconds. Please try again.")

    if result.get("error") == "not_a_vibe":
        raise ValueError(result.get("message", "That doesn't look like a vibe. Try describing a mood, scene, or feeling."))

    return result
