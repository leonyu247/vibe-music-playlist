# Vibe Music Playlist

Describe a mood or scene in plain English and get a Spotify playlist generated instantly using AI.

**Example vibes:**
- *"late night drive through a rainy city"*
- *"Sunday morning coffee, soft and introspective"*
- *"intense gym session, heavy and relentless"*

## How It Works

1. You type a vibe description
2. Google Gemini interprets it into Spotify audio parameters (energy, tempo, mood, etc.)
3. Spotify's recommendations engine finds matching tracks
4. You can save the playlist directly to your Spotify account

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| UI | Streamlit | Full-stack Python, no JavaScript needed |
| AI | Groq (Llama 3.3 70B) | Free tier (14,400 req/day), fast, reliable |
| Music API | Spotipy (Spotify Web API) | Python wrapper with built-in OAuth handling |
| Config | python-dotenv | API keys stay in `.env`, never in source code |

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/leonyu247/vibe-music-playlist.git
cd vibe-music-playlist
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get a free Groq API key

1. Sign up at [console.groq.com](https://console.groq.com)
2. Go to **API Keys** → **Create API key**
3. Copy the key

> **Note:** Temporary Groq keys expire after 90 days. Renew at [console.groq.com](https://console.groq.com) before expiry to avoid service interruption. The current key expires **2026-08-13**.

### 3. Create a Spotify app

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**
3. Set **Redirect URI** to: `http://localhost:8501`
4. Copy your **Client ID** and **Client Secret**

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
GROQ_API_KEY=your_groq_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8501
```

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Security Notes

- API keys are loaded from `.env` at runtime and never committed to git (`.gitignore` excludes `.env`)
- Spotify access tokens are stored only in Streamlit's in-memory session state — not written to any database
- The app requests the minimum required Spotify scopes: `playlist-modify-public` and `playlist-modify-private`
- Only your typed vibe text is sent to Gemini — no Spotify account data or listening history
