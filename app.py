from datetime import datetime
import time
import feedparser
from google import genai
import requests
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Daily Intelligence Briefing",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS targeting the exact layout and elements in the reference image
st.markdown(
    """
    <style>
    /* Full Page Background with Earth from Space wallpaper and dark overlay */
    .stApp {
        background: linear-gradient(rgba(8, 12, 18, 0.82), rgba(8, 12, 18, 0.92)), 
                    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #E0E6ED;
    }

    /* Header Title with AI Globe Icon */
    .header-container {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-top: 0.1rem;
    }
    .header-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #2A4365, #1A365D);
        border: 1px solid rgba(88, 166, 255, 0.4);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 0 14px rgba(88, 166, 255, 0.25);
    }
    .header-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .header-subtitle {
        font-size: 0.88rem;
        color: #8B949E;
        margin-top: 0.15rem;
    }

    /* Weather Card Widget (Apple iOS Glassmorphism) */
    .weather-card {
        background: rgba(16, 22, 34, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.8rem 1.1rem;
        color: #FFFFFF;
        max-width: 290px;
        margin-left: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .weather-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .weather-city {
        font-size: 0.72rem;
        font-weight: 600;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .weather-main-temp {
        font-size: 1.6rem;
        font-weight: 400;
        line-height: 1.1;
        color: #FFFFFF;
    }
    .weather-condition {
        font-size: 0.8rem;
        font-weight: 500;
        color: #58A6FF;
        margin-top: 0.1rem;
    }
    .weather-details-row {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
        padding-top: 0.4rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 0.73rem;
        color: #9A9FA8;
    }

    /* EXACT CATEGORY BUTTON PILLS MATCHING SCREENSHOT */
    div[data-testid="stColumn"] .stButton > button {
        width: 100% !important;
        background: rgba(16, 22, 34, 0.55) !important;
        color: #8B949E !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 1rem !important;
        height: auto !important;
        box-shadow: none !important;
        text-align: center !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stColumn"] .stButton > button:hover {
        background: rgba(33, 38, 45, 0.8) !important;
        color: #C9D1D9 !important;
        border-color: rgba(88, 166, 255, 0.3) !important;
    }
    
    /* Active Category Pill Styling with Glow Effect */
    .active-cat-pill .stButton > button {
        background: linear-gradient(135deg, rgba(33, 40, 56, 0.9), rgba(20, 26, 38, 0.9)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(88, 166, 255, 0.6) !important;
        box-shadow: 0 0 12px rgba(88, 166, 255, 0.2) !important;
    }

    /* News Card Styles */
    .news-card-box {
        background-color: rgba(16, 22, 34, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem 1.5rem 0.8rem 1.5rem;
        margin-bottom: 0.3rem;
        transition: border-color 0.2s ease;
    }
    .news-card-box:hover {
        border-color: rgba(88, 166, 255, 0.3);
    }
    .card-meta {
        font-size: 0.75rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .source-badge {
        background: rgba(255, 255, 255, 0.08);
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
        color: #C9D1D9;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F0F6FC;
        margin-bottom: 0.4rem;
        line-height: 1.35;
    }
    .card-snippet {
        font-size: 0.85rem;
        color: #9A9FA8;
        line-height: 1.4;
    }
    .article-link {
        color: #58A6FF !important;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.85rem;
    }
    .article-link:hover {
        text-decoration: underline !important;
    }

    /* AI Summary Button Style */
    .ai-btn-wrap button {
        background: linear-gradient(135deg, rgba(33, 38, 45, 0.9), rgba(22, 27, 34, 0.9)) !important;
        color: #E0E6ED !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.9rem !important;
        float: right;
    }
    .ai-btn-wrap button:hover {
        border-color: #58A6FF !important;
        color: #58A6FF !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. Weather Fetcher Function
@st.cache_data(ttl=900)
def fetch_riga_weather():
  try:
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=56.9496&longitude=24.1052&current=temperature_2m,relative_humidity_2m,"
        "apparent_temperature,weather_code&daily=sunrise,sunset&timezone=Europe%2FRiga"
    )
    res = requests.get(url, timeout=5).json()

    curr = res["current"]
    daily = res["daily"]

    temp = round(curr["temperature_2m"])
    feels_like = round(curr["apparent_temperature"])
    humidity = curr["relative_humidity_2m"]
    code = curr["weather_code"]

    code_map = {
        0: ("Clear", "☀️"),
        1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        51: ("Light Drizzle", "🌧️"),
        61: ("Slight Rain", "🌧️"),
        63: ("Moderate Rain", "🌧️"),
        65: ("Heavy Rain", "🌧️"),
        71: ("Snowfall", "🌨️"),
        80: ("Rain Showers", "🌦️"),
        95: ("Thunderstorm", "⛈️"),
    }
    desc, icon = code_map.get(code, ("Mainly Clear", "🌤️"))

    now_ts = datetime.now().timestamp()
    sunrise_ts = datetime.fromisoformat(daily["sunrise"][0]).timestamp()
    sunset_ts = datetime.fromisoformat(daily["sunset"][0]).timestamp()

    if now_ts < sunrise_ts:
      diff_hours = round((sunrise_ts - now_ts) / 3600, 1)
      sun_info = f"🌅 Sunrise {diff_hours}h"
    elif now_ts < sunset_ts:
      diff_hours = round((sunset_ts - now_ts) / 3600, 1)
      sun_info = f"🌇 Sunset {diff_hours}h"
    else:
      next_sunrise_ts = datetime.fromisoformat(daily["sunrise"][1]).timestamp()
      diff_hours = round((next_sunrise_ts - now_ts) / 3600, 1)
      sun_info = f"🌅 Sunrise {diff_hours}h"

    return {
        "temp": temp,
        "feels_like": feels_like,
        "humidity": humidity,
        "desc": desc,
        "icon": icon,
        "sun_info": sun_info,
    }
  except Exception:
    return None


# 3. Setup Gemini AI Client
try:
  client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
  st.warning("Please configure your Gemini API key in Streamlit secrets.")
  client = None

# Header Section with Title & Weather Widget
h_col1, h_col2 = st.columns([2.3, 1])

with h_col1:
  st.markdown(
      """
        <div class="header-container">
            <div class="header-icon">🌐</div>
            <div>
                <div class="header-title">Daily Intelligence Briefing</div>
                <div class="header-subtitle">Automated RSS intelligence stream with on-demand Gemini summaries.</div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with h_col2:
  weather = fetch_riga_weather()
  if weather:
    st.markdown(
        f"""
            <div class="weather-card">
                <div class="weather-header">
                    <div>
                        <div class="weather-city">RIGA, LATVIA</div>
                        <div class="weather-main-temp">{weather['temp']}°C</div>
                    </div>
                    <div style="font-size: 1.7rem;">{weather['icon']}</div>
                </div>
                <div class="weather-condition">{weather['desc']}</div>
                <div class="weather-details-row">
                    <span>Feels {weather['feels_like']}°C</span>
                    <span>💧 {weather['humidity']}%</span>
                    <span>{weather['sun_info']}</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# 4. Strictly Distinct Feeds per Category
FEEDS = {
    "Latvian Major News": [
        "https://www.lsm.lv/rss/?lang=lv&catid=20",
        "https://www.delfi.lv/rss/latvija",
    ],
    "Latvian Sports": [
        "https://www.lsm.lv/rss/?lang=lv&catid=15",
        "https://www.delfi.lv/rss/sports",
    ],
    "Global News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://news.yahoo.com/rss/world",
    ],
}


def get_time_ago(entry):
  try:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
      pub_time = time.mktime(entry.published_parsed)
      diff = time.time() - pub_time
      if diff < 0:
        return None
      hours = int(diff // 3600)
      if hours < 1:
        minutes = int(diff // 60)
        return f"{max(1, minutes)}m ago"
      elif hours < 24:
        return f"{hours}h ago"
      else:
        return f"{int(hours // 24)}d ago"
  except Exception:
    pass
  return None


@st.cache_data(ttl=300)
def load_curated_headlines(feed_tuple, category_name):
  feed_urls = list(feed_tuple)
  raw_articles = []
  for url in feed_urls:
    parsed_feed = feedparser.parse(url)
    source_name = (
        "LSM"
        if "lsm.lv" in url
        else (
            "Delfi"
            if "delfi.lv" in url
            else "BBC" if "bbci.co.uk" in url else "Yahoo"
        )
    )

    for entry in parsed_feed.entries[:30]:
      title = entry.get("title", "No Title")
      summary = entry.get("summary", entry.get("description", ""))
      link = entry.get("link", "#")
      time_ago = get_time_ago(entry)

      if any(
          bad_word in title.lower()
          for bad_word in ["tests", "kura sēne", "horoskops", "zodiaka"]
      ):
        continue

      clean_snippet = (
          summary[:140] + "..."
          if len(summary) > 140
          else (summary if summary else title)
      )

      raw_articles.append({
          "title": title,
          "link": link,
          "summary_raw": summary,
          "snippet": clean_snippet,
          "source": source_name,
          "time": time_ago,
      })

  if client and raw_articles:
    titles_list = "\n".join(
        [f"{idx}: {a['title']}" for idx, a in enumerate(raw_articles)]
    )

    if category_name == "Latvian Major News":
      filter_prompt = f"""
            You are a strict national news editor for Latvia. Review these headlines:
            {titles_list}
            RULES:
            - ONLY keep major political news, government decisions, national economy updates, security warnings, or top civil developments in Latvia.
            - STRICTLY EXCLUDE AND DROP: any sports games, team scores, athlete interviews, tournaments, lifestyle pieces, horoscopes, and quizzes.
            Return ONLY a comma-separated list of allowed index numbers (e.g., 0, 3, 7). No extra text.
            """
    elif category_name == "Latvian Sports":
      filter_prompt = f"""
            You are a professional sports editor. Review these headlines:
            {titles_list}
            RULES:
            - ONLY keep professional sports results, game scores, tournament rankings, medal achievements, or official competitive updates involving Latvian sports teams or athletes (e.g., hockey, basketball, football, tennis, athletics).
            - STRICTLY EXCLUDE AND DROP: general political news, national government updates, lifestyle fitness tips, general equipment guides, or minor hobbies.
            Return ONLY a comma-separated list of allowed index numbers (e.g., 1, 4, 6). No extra text.
            """
    else:
      filter_prompt = f"""
            Select the major global news, international conflicts, and world economic shifts from this list:
            {titles_list}
            Return ONLY a comma-separated list of valid index numbers (e.g., 0, 1, 2). No extra text.
            """

    try:
      response = client.models.generate_content(
          model="gemini-3.8-flash", contents=filter_prompt
      )
      indices_str = response.text.strip().replace("\n", "")
      valid_indices = [
          int(i.strip()) for i in indices_str.split(",") if i.strip().isdigit()
      ]

      curated = [raw_articles[i] for i in valid_indices if i < len(raw_articles)]
      return curated if curated else raw_articles[:15]
    except Exception:
      return raw_articles[:15]

  return raw_articles[:15]


# Session State Initialization
if "selected_cat" not in st.session_state:
  st.session_state.selected_cat = "Latvian Major News"

if "visible_counts" not in st.session_state:
  st.session_state.visible_counts = {
      "Latvian Major News": 5,
      "Latvian Sports": 5,
      "Global News": 5,
  }

# 5. EXACT CATEGORY PILLS ROW MATCHING SCREENSHOT
col_spacer1, nav1, nav2, nav3, col_spacer2 = st.columns(
    [0.8, 1.2, 1.2, 1.2, 0.8]
)

categories = [
    ("🏛️ Latvian Major News", "Latvian Major News"),
    ("🏆 Latvian Sports", "Latvian Sports"),
    ("🌍 Global News", "Global News"),
]
nav_cols = [nav1, nav2, nav3]

for col, (display_label, cat_key) in zip(nav_cols, categories):
  with col:
    is_active = st.session_state.selected_cat == cat_key
    if is_active:
      st.markdown('<div class="active-cat-pill">', unsafe_allow_html=True)

    if st.button(display_label, key=f"cat_pill_{cat_key}"):
      st.session_state.selected_cat = cat_key
      st.rerun()

    if is_active:
      st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div style='margin-bottom: 1.8rem;'></div>", unsafe_allow_html=True
)

# 6. Centered Main Content Stream
active_cat = st.session_state.selected_cat
articles = load_curated_headlines(tuple(FEEDS[active_cat]), active_cat)
visible_count = st.session_state.visible_counts[active_cat]

left_space, center_feed, right_space = st.columns([1, 2.5, 1])

with center_feed:
  displayed_articles = articles[:visible_count]

  for i, article in enumerate(displayed_articles):
    time_str = f" • {article['time']}" if article["time"] else ""

    st.markdown(
        f"""
        <div class="news-card-box">
            <div class="card-meta">
                <span class="source-badge">{article['source']}</span>
                <span>{time_str}</span>
            </div>
            <div class="card-title">{article['title']}</div>
            <div class="card-snippet">{article['snippet']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2 = st.columns([1, 1])
    with b1:
      st.markdown(
          f"<div style='padding-top: 0.2rem;'><a class='article-link'"
          f" href='{article['link']}' target='_blank'>🔗 Read Full"
          " Article</a></div>",
          unsafe_allow_html=True,
      )
    with b2:
      st.markdown('<div class="ai-btn-wrap">', unsafe_allow_html=True)
      if st.button("✨ AI Summary", key=f"btn_{active_cat}_{i}"):
        if client:
          with st.spinner("Analyzing context..."):
            try:
              prompt = (
                  "Summarize the core facts of this news piece concisely in 3"
                  " bullet points. Focus strictly on major details: "
                  f"{article['title']} -- {article['summary_raw']}"
              )
              response = client.models.generate_content(
                  model="gemini-3.8-flash",
                  contents=prompt,
              )
              st.info(response.text)
            except Exception as e:
              if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.warning(
                    "⚠️ Free tier daily limit reached (20 requests/day)."
                    " Please try again tomorrow or check your plan details."
                )
              else:
                st.error(f"An error occurred: {e}")
        else:
          st.error("API client not initialized.")
      st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True
    )

  # Load More Button
  if visible_count < len(articles):
    st.write("")
    st.markdown('<div class="ai-btn-wrap" style="text-align: center;">', unsafe_allow_html=True)
    if st.button("🔽 Load More (+5 Articles)", key="load_more_btn"):
      st.session_state.visible_counts[active_cat] += 5
      st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)