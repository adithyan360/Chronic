import google.generativeai as genai

genai.configure(api_key="AIzaSyBh-ATGtmlgPxV1eR1Z6inSHUpXZZxI4MU")

try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
except Exception as e:
    print("Error listing models:", e)