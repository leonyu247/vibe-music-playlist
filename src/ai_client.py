import json
import os

from groq import Groq

# NOTE: The Groq API key in use is a permanent key with no expiry date.

_PROMPT_TEMPLATE = """You are a music expert and playlist curator. A user described a vibe: "{vibe}"

Create a playlist that perfectly captures this vibe. Return a JSON object with exactly these fields:
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


def get_playlist_from_vibe(vibe: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompt = _PROMPT_TEMPLATE.format(vibe=vibe)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
