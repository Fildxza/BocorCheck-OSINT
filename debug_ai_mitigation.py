#!/usr/bin/env python3
"""
DEBUG SCRIPT - Test AI Mitigation Plan Generation
FILDZA_AI_ACTIVE - Verifies that mitigation plans are DIFFERENT for different breach scenarios

This script tests 4 different breach scenarios to ensure phi3 generates different (non-generic) responses:
1. Email only breach (LOW risk)
2. Email + Password breach (HIGH risk)
3. Email + Financial Data breach (HIGH risk)
4. Email + Password + Phone breach (CRITICAL risk)

Usage:
    python debug_ai_mitigation.py

Expected: Different mitigation plans for each scenario
"""

import json
import logging
import requests
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the analyzeWithAI function from bot.py
try:
    from bot import analyzeWithAI
except ImportError:
    logger.error("❌ Cannot import analyzeWithAI from bot.py")
    sys.exit(1)

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Scenario 1: Email Only (LOW RISK)",
        "email": "test_email_only@example.com",
        "breaches": [
            {
                "Name": "LinkedIn",
                "BreachDate": "2021-06-28",
                "DataClasses": ["Email"],
            }
        ]
    },
    {
        "name": "Scenario 2: Email + Password (HIGH RISK)",
        "email": "test_password_breach@example.com",
        "breaches": [
            {
                "Name": "LinkedIn",
                "BreachDate": "2021-06-28",
                "DataClasses": ["Email", "Password"],
            },
            {
                "Name": "Dropbox",
                "BreachDate": "2012-03-01",
                "DataClasses": ["Email", "Password"],
            }
        ]
    },
    {
        "name": "Scenario 3: Email + Financial Data (HIGH RISK)",
        "email": "test_financial_breach@example.com",
        "breaches": [
            {
                "Name": "Capital One",
                "BreachDate": "2019-07-29",
                "DataClasses": ["Email", "FinancialData"],
            }
        ]
    },
    {
        "name": "Scenario 4: Email + Password + Phone (CRITICAL)",
        "email": "test_critical_breach@example.com",
        "breaches": [
            {
                "Name": "LinkedIn",
                "BreachDate": "2021-06-28",
                "DataClasses": ["Email", "Password"],
            },
            {
                "Name": "Facebook",
                "BreachDate": "2019-04-03",
                "DataClasses": ["Email", "Phone"],
            },
            {
                "Name": "Yahoo",
                "BreachDate": "2013-02-27",
                "DataClasses": ["Email", "Password"],
            }
        ]
    }
]

def run_debug_tests():
    """Run all test scenarios and compare AI outputs"""
    
    logger.info("\n" + "="*70)
    logger.info("FILDZA_AI_ACTIVE - AI MITIGATION DEBUG TEST")
    logger.info("="*70)
    logger.info(f"Testing {len(TEST_SCENARIOS)} different breach scenarios...\n")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            logger.info(f"✓ Ollama is running with {len(models)} model(s)")
            if not any("phi3" in m.get("name", "") for m in models):
                logger.warning("⚠️ phi3 model not found. Run: ollama pull phi3")
    except:
        logger.error("❌ Cannot connect to Ollama at http://localhost:11434")
        logger.error("Please start Ollama: ollama run phi3")
        return
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"TEST #{i}: {scenario['name']}")
        logger.info(f"{'='*70}")
        logger.info(f"Email: {scenario['email']}")
        logger.info(f"Breaches: {len(scenario['breaches'])}")
        
        # Show breach details
        data_types = set()
        for breach in scenario['breaches']:
            logger.info(f"  • {breach['Name']}: {', '.join(breach['DataClasses'])}")
            data_types.update(breach['DataClasses'])
        logger.info(f"Exposed data types: {', '.join(sorted(data_types))}\n")
        
        # Call AI
        logger.info("Calling analyzeWithAI()...")
        osint_data = {
            "email": scenario['email'],
            "breaches": scenario['breaches']
        }
        
        ai_result = analyzeWithAI(osint_data)
        
        if not ai_result:
            logger.error("❌ AI returned None (fallback or error)")
            results.append({
                "scenario": scenario['name'],
                "email": scenario['email'],
                "success": False,
                "risk_level": "N/A",
                "explanation": "AI failed or returned None"
            })
            continue
        
        # Extract and display results
        risk_level = ai_result.get('risk_level', 'UNKNOWN')
        explanation = ai_result.get('explanation', 'No explanation')
        mitigation = ai_result.get('mitigation', {})
        
        logger.info(f"✓ AI Response received!")
        logger.info(f"  Risk Level: {risk_level}")
        logger.info(f"  Explanation: {explanation[:100]}...")
        logger.info(f"  Immediate Actions: {len(mitigation.get('immediate', []))} actions")
        logger.info(f"  Short-term Actions: {len(mitigation.get('short_term', []))} actions")
        logger.info(f"  Long-term Actions: {len(mitigation.get('long_term', []))} actions")
        
        # Store result for comparison
        results.append({
            "scenario": scenario['name'],
            "email": scenario['email'],
            "success": True,
            "risk_level": risk_level,
            "explanation": explanation,
            "immediate_actions": mitigation.get('immediate', []),
            "short_term_actions": mitigation.get('short_term', []),
            "long_term_actions": mitigation.get('long_term', [])
        })
    
    # Summary and comparison
    logger.info(f"\n{'='*70}")
    logger.info("SUMMARY & COMPARISON")
    logger.info(f"{'='*70}\n")
    
    successful = [r for r in results if r['success']]
    logger.info(f"Successful: {len(successful)}/{len(results)}\n")
    
    # Risk levels comparison
    logger.info("Risk Levels Across Scenarios:")
    for r in results:
        logger.info(f"  {r['scenario']:45} → {r['risk_level']}")
    
    # Check if outputs are different (non-generic)
    logger.info(f"\n{'='*70}")
    logger.info("DIFFERENTIATION CHECK (are responses different?)")
    logger.info(f"{'='*70}\n")
    
    if len(successful) > 1:
        first_immediate = results[0].get('immediate_actions', [])
        all_same = all(r.get('immediate_actions', []) == first_immediate for r in results[1:] if r['success'])
        
        if all_same and first_immediate:
            logger.warning("⚠️ All immediate actions are IDENTICAL across scenarios!")
            logger.warning("   This suggests mitigation plans are NOT dynamic/specific.")
            logger.warning("\n   Immediate actions in all scenarios:")
            for action in first_immediate:
                logger.warning(f"     • {action}")
        else:
            logger.info("✓ Immediate actions DIFFER across scenarios (good!)")
            for r in results:
                if r['success']:
                    logger.info(f"\n  {r['scenario']}:")
                    for action in r.get('immediate_actions', [])[:2]:  # Show first 2
                        logger.info(f"    • {action}")
    
    # Show detailed immediate actions for comparison
    logger.info(f"\n{'='*70}")
    logger.info("DETAILED IMMEDIATE ACTIONS (First 3 Per Scenario)")
    logger.info(f"{'='*70}\n")
    
    for r in results:
        if r['success']:
            logger.info(f"{r['scenario']}:")
            for action in r.get('immediate_actions', [])[:3]:
                logger.info(f"  • {action}")
            logger.info("")
    
    logger.info(f"{'='*70}")
    logger.info("TEST COMPLETE")
    logger.info(f"{'='*70}\n")
    
    # Recommendations
    if all(r.get('risk_level') == results[0].get('risk_level') for r in results if r['success']):
        logger.warning("\n⚠️ WARNING: All scenarios have the SAME risk level!")
        logger.warning("   The AI may not be properly analyzing breach data differences.")
        logger.warning("\n   SOLUTIONS:")
        logger.warning("   1. Check Ollama is running: ollama run phi3")
        logger.warning("   2. Try with a different model: ollama pull mistral")
        logger.warning("   3. Increase prompt specificity")
        logger.warning("   4. Check if phi3 model is corrupted - delete and re-pull")
    else:
        logger.info("✓ Different risk levels detected across scenarios - AI is responsive!")


if __name__ == "__main__":
    run_debug_tests()
