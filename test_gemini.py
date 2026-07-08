import google.generativeai as genai

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyBh-ATGtmlgPxV1eR1Z6inSHUpXZZxI4MU"
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("What are chronic diseases? Answer in 2 sentences.")
    print("✅ Gemini API Working!")
    print("Response:", response.text)
except Exception as e:
    print("❌ Gemini API Error:", e)
    print("Error type:", type(e).__name__)