import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from agents.explanation_builder import ExplanationBuilderAgent

async def main():
    print("--- STARTING MANUAL VERIFICATION ---")
    print(f"Using Model: {os.getenv('GEMINI_MODEL')}")
    key_prefix = os.getenv('GEMINI_API_KEY')[:5] if os.getenv('GEMINI_API_KEY') else "None"
    print(f"Using Key: {key_prefix}...")
    
    try:
        print("Initializing Agent...", end=" ")
        agent = ExplanationBuilderAgent()
        print("Done.")
        
        question = "Hello! Are you working correctly now?"
        print(f"\nSending Message: '{question}'\n")
        
        # Call the agent directly (simulating the chat route)
        response = await agent.answer_question(
            question=question,
            context=None,
            conversation_history=[]
        )
        
        print("--- AI RESPONSE ---")
        print(response)
        print("-------------------")
        
        if response and len(response) > 5 and "error" not in response.lower():
             print("\n✅ VERIFICATION SUCCESSFUL: The AI generated a valid text response.")
        else:
             print("\n❌ VERIFICATION FAILED: Response looked like an error or empty.")

    except Exception as e:
        print(f"\n❌ EXCEPTION DURING TEST: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
