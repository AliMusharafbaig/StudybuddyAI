import google.generativeai as genai
import os

api_key = "AIzaSyA0GasYWe9HRzmHBibou7qwTrVxYKb0BsM"
genai.configure(api_key=api_key)

print(f"DEBUG: Key: {api_key[:10]}...")

print("\n--- LISTING AVAILABLE MODELS ---\n")
available_models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            available_models.append(m.name)
except Exception as e:
    print(f"ListModels Failed: {e}")

print("\n--- TESTING FALLBACKS ---\n")
fallbacks = ["models/gemini-pro", "gemini-pro", "models/gemini-1.0-pro"]

# Add available models to test list if not present
for m in available_models:
    if m not in fallbacks:
        fallbacks.append(m)

working_model = None

for model_name in fallbacks:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi")
        if response.text:
            print(f"✅ SUCCESS!")
            if not working_model:
                working_model = model_name
                break # Stop at first success
        else:
            print("❌ Empty")
    except Exception as e:
        err = str(e)
        if "429" in err:
             print("❌ 429 Rate Limit")
        elif "404" in err:
             print("❌ 404 Not Found")
        else:
             print(f"❌ Error: {err[:50]}...")

print("\n--- COMPLETE ---")
if working_model:
    print(f"WINNER: {working_model}")
else:
    print("NO WORKING MODELS FOUND.")
