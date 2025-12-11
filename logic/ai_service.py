# logic/ai_service.py
import google.generativeai as genai
from data.database import fetch_all

# ==========================================
# PASTE YOUR API KEY HERE
API_KEY = "Insert Your API Key Here"
# ==========================================

class AIService:
    def __init__(self):
        self.model = None
        self.active = False
        
        # Check if key is present
        if API_KEY and "Insert" not in API_KEY:
            try:
                # Configure the API
                genai.configure(api_key=API_KEY)
                
                # Initialize the model (using the latest flash model)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.active = True
                print("✅ DEBUG: AI Client initialized successfully.")
            except Exception as e:
                print(f"❌ DEBUG: AI Init Error: {e}")
        else:
            print("⚠️ DEBUG: API Key missing. Please add your Gemini API key.")

    def _get_context_from_db(self):
        """Fetches real data to make the AI smart"""
        try:
            # 1. Get Events
            events = fetch_all("SELECT title, datetime, location FROM events")
            events_text = "Upcoming Events:\n"
            if events:
                for e in events:
                    events_text += f"- {e[0]} on {e[1]} at {e[2]}\n"
            else:
                events_text += "No upcoming events scheduled.\n"
            
            # 2. Get Announcements
            news = fetch_all("SELECT title, content FROM announcements ORDER BY created_at DESC LIMIT 3")
            news_text = "Latest News:\n"
            if news:
                for n in news:
                    news_text += f"- {n[0]}: {n[1]}\n"
            else:
                news_text += "No recent announcements.\n"

            return events_text + "\n" + news_text
        except Exception as e:
            print(f"❌ DEBUG: Database Context Error: {e}")
            return "Context unavailable."

    def get_response(self, user_query):
        if not self.active:
            return "🔴 AI Service is offline. Please check your API key in logic/ai_service.py"

        # 1. Get Context
        db_context = self._get_context_from_db()
        
        # 2. Construct Full Prompt
        full_prompt = f"""You are 'Bazm AI', a helpful assistant for the Bazm-e-Paigham community.
You speak politely (start with Assalam-o-Alaikum when appropriate).
You understand Islamic community terms like Rukan (Admin), Rafeeq (Member), etc.

DATABASE CONTEXT:
{db_context}

USER QUERY:
{user_query}

Please answer based on the context above in a friendly and helpful manner."""

        try:
            # 3. Generate Content using the correct API
            response = self.model.generate_content(full_prompt)
            
            # Return the text response
            return response.text
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ DEBUG: Generation Error: {error_msg}")
            
            # Provide helpful error messages
            if "API_KEY_INVALID" in error_msg or "api_key" in error_msg.lower():
                return "🔑 Invalid API Key. Please check your Gemini API key."
            elif "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
                return "⚠️ API quota exceeded. Please check your Google AI Studio limits."
            elif "model" in error_msg.lower() or "NOT_FOUND" in error_msg:
                return "⚠️ Model error. Please ensure you're using the correct Gemini model."
            else:
                return f"❌ Error connecting to AI: {error_msg[:100]}..."