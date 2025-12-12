import google.generativeai as genai
import os

api_key = "AIzaSyBjhZ1JmH8VTbr4u52ZPi-ShjBYL0n62U8"
genai.configure(api_key=api_key)

print("Searching for 'flash' models...")
try:
    found = False
    for m in genai.list_models():
        if "1.5" in m.name or "flash" in m.name:
            print(f"FOUND: {m.name}")
            found = True
    
    if not found:
        print("No 1.5 or flash models found.")
        
except Exception as e:
    print(f"Error: {e}")
