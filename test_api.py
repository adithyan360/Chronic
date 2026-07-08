import google.generativeai as genai

genai.configure(api_key="AIzaSyBh-ATGtmlgPxV1eR1Z6inSHUpXZZxI4MU")

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("What is diabetes?")
    print("SUCCESS - Gemini API working!")
    print("Response:", response.text)
except Exception as e:
    print("FAILED - Gemini API error:")
    print("Error:", str(e))