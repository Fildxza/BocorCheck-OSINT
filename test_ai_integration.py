#!/usr/bin/env python3
"""
FILDZA_AI_ACTIVE - Test Script for AI Mitigation Integration
Tests connectivity to Ollama and validates AI response format
"""

import json
import requests
import sys
import time

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
OLLAMA_TIMEOUT = 40

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Ollama Server Connection")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        print("✓ Ollama server is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print(f"   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_phi3_model():
    """Test if phi3 model is available"""
    print("\n" + "="*60)
    print("🤖 TEST 2: phi3 Model Availability")
    print("="*60)
    
    try:
        # Simple test prompt
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": "Say 'hello' in one word",
            "stream": False
        }
        
        print(f"Connecting to: {OLLAMA_URL}")
        print(f"Model: {OLLAMA_MODEL}")
        print(f"Timeout: {OLLAMA_TIMEOUT}s")
        print("\nSending test prompt...")
        
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✓ phi3 model responded in {elapsed:.1f}s")
            data = response.json()
            response_text = data.get("response", "")
            print(f"Response: {response_text[:100]}...")
            return True
        else:
            print(f"❌ Model error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print(f"   Run: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Model timeout ({OLLAMA_TIMEOUT}s)")
        print("   Model might need to be loaded. Try again.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ai_mitigation():
    """Test full AI mitigation generation"""
    print("\n" + "="*60)
    print("🛡️  TEST 3: AI Mitigation Generation")
    print("="*60)
    
    test_data = {
        "email": "test@example.com",
        "breaches": [
            {
                "Name": "LinkedIn",
                "BreachDate": "2021-06-28",
                "DataClasses": ["Email", "Password"]
            },
            {
                "Name": "MyFitnessPal",
                "BreachDate": "2018-03-28",
                "DataClasses": ["Email", "Password", "Phone"]
            }
        ]
    }
    
    print(f"Test data: {json.dumps(test_data, indent=2)}\n")
    
    breaches = test_data["breaches"]
    data_types = sorted({d for b in breaches for d in b.get("DataClasses", [])})
    
    breach_summary = ""
    for i, breach in enumerate(breaches, 1):
        breach_summary += f"\n{i}. {breach.get('Name')}: {', '.join(breach.get('DataClasses', []))} ({breach.get('BreachDate')})"
    
    prompt = f"""You are a cybersecurity expert. Analyze this breach data and respond ONLY with JSON.

BREACH DATA:
Email: {test_data['email']}
Breaches: {len(breaches)}
Exposed: {', '.join(data_types)}{breach_summary}

For each action, make it SPECIFIC to the exposed data types.

PROVIDE ONLY THIS JSON (no other text):
{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "explanation": "Assessment based on specific breach data",
  "mitigation": {{
    "immediate": ["action 1", "action 2", "action 3"],
    "short_term": ["action 1", "action 2", "action 3"],
    "long_term": ["action 1", "action 2", "action 3"]
  }}
}}"""
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print("Sending mitigation analysis prompt to Ollama...")
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return False
        
        print(f"✓ Response received in {elapsed:.1f}s\n")
        
        data = response.json()
        response_text = data.get("response", "")
        
        # Extract JSON
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}")
        
        if start_idx == -1 or end_idx == -1:
            print("❌ No JSON found in response")
            print(f"Response: {response_text[:200]}...")
            return False
        
        json_str = response_text[start_idx:end_idx+1]
        
        try:
            result = json.loads(json_str)
            
            # Validate structure
            required_keys = {"risk_level", "explanation", "mitigation"}
            if not required_keys.issubset(result.keys()):
                print(f"❌ Missing keys: {required_keys - set(result.keys())}")
                return False
            
            print("✓ AI Response (formatted):")
            print(f"\n  Risk Level: {result.get('risk_level')}")
            print(f"  Explanation: {result.get('explanation')}")
            
            mitigation = result.get('mitigation', {})
            print(f"\n  Immediate Actions:")
            for action in mitigation.get('immediate', []):
                print(f"    • {action}")
            print(f"\n  Short-term Actions:")
            for action in mitigation.get('short_term', []):
                print(f"    • {action}")
            print(f"\n  Long-term Actions:")
            for action in mitigation.get('long_term', []):
                print(f"    • {action}")
            
            print("\n✓ Mitigation plan generated successfully!")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"JSON string: {json_str[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout ({OLLAMA_TIMEOUT}s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FILDZA_AI_ACTIVE - Integration Test Suite")
    print("="*60)
    
    results = {
        "Connection": test_ollama_connection(),
        "Model": test_phi3_model(),
        "Mitigation": test_ai_mitigation(),
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    
    if all_passed:
        print("✓ All tests passed! FILDZA_AI_ACTIVE is ready.")
        print("\nYou can now:")
        print("  1. Run: python bot.py")
        print("  2. Test: /check test@example.com")
        return 0
    else:
        print("❌ Some tests failed. Check errors above.")
        print("\nTroubleshooting:")
        print("  • Ollama: ollama serve")
        print("  • phi3 model: ollama pull phi3")
        print("  • Check connectivity: ping localhost:11434")
        return 1


if __name__ == "__main__":
    sys.exit(main())
