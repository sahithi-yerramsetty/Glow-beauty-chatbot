# ✨ GlowBot — AI Beauty Advisor Chatbot

A personalized beauty advisor chatbot built with LangChain + OpenAI + Streamlit.

## Features
- Collects skin type, hair type, concerns, budget
- Recommends products within your price range
- Builds AM/PM routines tailored to your profile
- Explains ingredients to use and avoid
- Remembers your profile throughout the conversation

## Setup (5 minutes)

### 1. Clone / download this folder

### 2. Create a virtual environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free OpenAI API key
- Go to https://platform.openai.com
- Sign up → API Keys → Create new key
- New accounts get $5 free credits (enough for hundreds of chats)

### 5. Run the app
```bash
streamlit run app.py
```

### 6. Open in browser
Streamlit will open automatically at `http://localhost:8501`
Enter your API key in the sidebar and start chatting!

## Project Structure
```
beauty_chatbot/
├── app.py          # Streamlit UI
├── chatbot.py      # LangChain logic + system prompt
├── requirements.txt
└── README.md
```

## Next Steps (Phase 2 & 3)
- Phase 2: Add ChromaDB vector database with real product data
- Phase 3: Deploy free on Streamlit Cloud with a public URL
