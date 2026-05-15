import json
import os

from google import genai

_VALID_GENRES = (
    "acoustic, afrobeat, alt-rock, alternative, ambient, anime, black-metal, bluegrass, "
    "blues, bossanova, brazil, breakbeat, british, cantopop, chicago-house, children, chill, "
    "classical, club, comedy, country, dance, dancehall, death-metal, deep-house, "
    "detroit-techno, disco, disney, drum-and-bass, dub, dubstep, edm, electro, electronic, "
    "emo, folk, forro, french, funk, garage, german, gospel, goth, grindcore, groove, "
    "grunge, guitar, happy, hard-rock, hardcore, hardstyle, heavy-metal, hip-hop, holidays, "
    "honky-tonk, house, idm, indian, indie, indie-pop, industrial, iranian, j-dance, j-idol, "
    "j-pop, j-rock, jazz, k-pop, kids, latin, latino, malay, mandopop, metal, metal-misc, "
    "metalcore, minimal-techno, movies, mpb, new-age, new-release, opera, pagode, party, "
    "philippines-opm, piano, pop, pop-film, post-dubstep, power-pop, progressive-house, "
    "psych-rock, punk, punk-rock, r-n-b, rainy-day, reggae, reggaeton, road-trip, rock, "
    "rock-n-roll, rockabilly, romance, sad, salsa, samba, sertanejo, show-tunes, "
    "singer-songwriter, ska, sleep, songwriter, soul, soundtracks, spanish, study, summer, "
    "swedish, synth-pop, tango, techno, trance, trip-hop, turkish, work-out, world-music"
)

_PROMPT_TEMPLATE = """You are a music curation expert. A user described a vibe: "{vibe}"

Map this vibe to Spotify audio parameters and return ONLY a valid JSON object — no markdown, no explanation.

Required fields:
- playlist_name: creative, short playlist name (max 40 characters)
- description: one evocative sentence describing the vibe
- seed_genres: array of 1–3 genre strings chosen ONLY from this list: {genres}
- target_energy: float 0.0–1.0 (0=calm, 1=intense)
- target_valence: float 0.0–1.0 (0=dark/sad, 1=bright/happy)
- target_danceability: float 0.0–1.0
- target_acousticness: float 0.0–1.0 (0=electronic, 1=acoustic/unplugged)
- target_instrumentalness: float 0.0–1.0 (0=lots of vocals, 1=fully instrumental)
- target_tempo: float in BPM (e.g. 70 for slow, 120 for moderate, 160 for fast)
- target_popularity: integer 0–100 (40–60 for a mix; higher for mainstream hits)
"""


def get_audio_features_from_vibe(vibe: str) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = _PROMPT_TEMPLATE.format(vibe=vibe, genres=_VALID_GENRES)
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )
    text = response.text.strip()
    # Strip markdown code fences if Gemini wraps the JSON
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return json.loads(text)
