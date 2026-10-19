import streamlit as st
import feedparser
import requests
from google import genai
from google.genai.errors import APIError

# Set Streamlit Page Configuration
st.set_page_config(page_title="Daily Intelligence Briefing", page_icon="📰", layout="wide")

# ---------------------------------------------------------
# 1. MULTI-SOURCE RSS FEEDS
# ---------------------------------------------------------
LATVIAN_FEEDS = {
    "LSM": "https://www.lsm.lv/rss/",
    "Delfi": "https://www.delfi.lv/rss/",
    "TVNET": "https://www.tvnet.lv/rss"
}

GLOBAL_FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&hl=en-US&gl=US&ceid=US:en",
    "CNN": "http://rss.cnn.com/rss/edition.rss"
}

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS TO FETCH & MIX FEEDS
# ---------------------------------------------------------
def fetch_mixed_news(feed_dict, items_per_feed=5):
    """Fetches articles evenly from all feeds in the dictionary."""
    combined_articles = []
    
    for source_name, feed_url in feed_dict.items():
        try:
            parsed = feedparser.parse(feed_url)
            count = 0
            for entry in parsed.entries:
                if count >= items_per_feed:
                    break
                combined_articles.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "summary": entry.get("summary", entry.get("description", "")),
                    "source": source_name
                })
                count += 1
        except Exception as e:
            st.warning(f"Could not load news from {source_name}: {e}")
            
    return combined_articles

# Initialize Session State for persistent "Load More" counts
if "lv_count" not in st.session_state:
    st.session_state.lv_count = 5

if "global_count" not in st.session_state:
    st.session_state.global_count = 5

# ---------------------------------------------------------
# 3. AI SUMMARY WITH GEMINI FALLBACK HANDLING
# ---------------------------------------------------------
def generate_ai_summary(articles_text):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Gemini API key not found in Streamlit Secrets."
    
    client = genai.Client(api_key=api_key)
    prompt = f"Provide a brief, 3-bullet point executive summary of these news headlines:\n\n{articles_text}"
    
    # Try models in order of priority to bypass 503 traffic spikes
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    
    for model_id in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            return response.text
        except APIError as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                continue # Try next model if server is busy
            return f"An error occurred: {e}"
        except Exception as e:
            return f"An error occurred: {e}"
            
    return "⚠️ Google Gemini service is currently experiencing high demand across all model endpoints. Please try generating the summary again in a few moments."

# ---------------------------------------------------------
# 4. APP LAYOUT & INTERFACE
# ---------------------------------------------------------
st.title("📰 Daily Intelligence Briefing")

tab1, tab2 = st.tabs(["🇱🇻 Latvian News", "🌐 Global News"])

# --- LATVIAN NEWS TAB ---
with tab1:
    st.header("Latvian News Headlines")
    lv_news = fetch_mixed_news(LATVIAN_FEEDS, items_per_feed=10)
    
    # Render articles up to current session state count
    for item in lv_news[:st.session_state.lv_count]:
        st.markdown(f"**[{item['source']}]** [{item['title']}]({item['link']})")
        
    st.write("---")
    
    # Load More Button
    if st.session_state.lv_count < len(lv_news):
        if st.button("Load More Latvian Headlines", key="btn_lv"):
            st.session_state.lv_count += 5
            st.rerun()
            
    # AI Summary Button
    if st.button("✨ Generate AI Summary (Latvian News)", key="sum_lv"):
        headlines = "\n".join([f"- {item['title']}" for item in lv_news[:st.session_state.lv_count]])
        with st.spinner("Analyzing news with Gemini..."):
            summary = generate_ai_summary(headlines)
            st.info(summary)

# --- GLOBAL NEWS TAB ---
with tab2:
    st.header("Global News Headlines")
    global_news = fetch_mixed_news(GLOBAL_FEEDS, items_per_feed=10)
    
    for item in global_news[:st.session_state.global_count]:
        st.markdown(f"**[{item['source']}]** [{item['title']}]({item['link']})")
        
    st.write("---")
    
    if st.session_state.global_count < len(global_news):
        if st.button("Load More Global Headlines", key="btn_global"):
            st.session_state.global_count += 5
            st.rerun()
            
    if st.button("✨ Generate AI Summary (Global News)", key="sum_global"):
        headlines = "\n".join([f"- {item['title']}" for item in global_news[:st.session_state.global_count]])
        with st.spinner("Analyzing news with Gemini..."):
            summary = generate_ai_summary(headlines)
            st.info(summary)
