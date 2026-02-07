# python -m scripts.test_groq_provider

import os
import time
from ai_slop_gate.providers.llm import GroqProvider

def test_groq():
    if not os.getenv("SLOPE_GATE_GROQ"):
        print("❌ Error: Please set SLOPE_GATE_GROQ environment variable.")
        return

    provider = GroqProvider()
    
    test_code = """
    def calculate_price(items):
        # TODO: I should probably fix this later, but AI suggested this
        # and it seems to work for now. 
        res = 0
        for i in items:
            res += i.price
        return res
    """
    
    print(f"🚀 Sending request to Groq ({provider.model})...")
    start_time = time.time()
    
    observations = provider.get_observations(test_code)
    
    end_time = time.time()
    
    print(f"⏱️ Response received in {end_time - start_time:.2f} seconds.")
    print("-" * 30)
    
    if observations:
        for i, obs in enumerate(observations, 1):
            print(f"{i}. [{obs.category.upper()}] - {obs.signal}")
    else:
        print("No observations found or error occurred.")

if __name__ == "__main__":
    test_groq()