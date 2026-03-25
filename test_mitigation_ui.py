#!/usr/bin/env python3
"""Test the mitigation UI integration"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_mitigation_in_response():
    """Test that mitigation data appears in the dashboard response"""
    
    # Test with a mock email that should trigger breaches
    test_data = {
        "email": "amin.demo@gmail.com",  # HIGH risk breach in mock data
        "phone_number": "+60123456789",
        "bank_account": "1234567890",
        "api_mode": "mock",
        "submit_action": "analyze"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/", data=test_data, allow_redirects=True)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for mitigation sections
            checks = {
                "Dashboard loads": "BocorCheck Dashboard" in html_content,
                "Breach table exists": "Breach Incidents" in html_content,
                "Mitigation tips shown": "Recommended Mitigation Plan" in html_content,
                "Detailed mitigation section": "Detailed Mitigation Actions" in html_content,
                "Action cards exist": "action-card" in html_content,
                "Malaysian resources header": "Malaysian Resources" in html_content or "🇲🇾" in html_content,
                "Resource cards": "resource-card" in html_content,
                "Bank contact info": ("Maybank" in html_content or "PDRM" in html_content),
                "Step details": "details" in html_content and "View Steps" in html_content,
            }
            
            print("🧪 MITIGATION SYSTEM TEST RESULTS:\n")
            print("=" * 50)
            
            all_passed = True
            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
                if not result:
                    all_passed = False
            
            print("=" * 50)
            
            if all_passed:
                print("\n🎉 ALL TESTS PASSED! Mitigation system is working!\n")
                return True
            else:
                print("\n⚠️ Some features not found. Checking response content...")
                
                # Save full HTML to file for inspection
                with open('mitigation_response.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("Full response saved to mitigation_response.html")
                
                # Check if mitigation_data was passed to template
                if "mitigation_data" in html_content:
                    print("✅ mitigation_data variable found in HTML")
                else:
                    print("❌ mitigation_data NOT found - context variable may be empty")
                
                # Check if template variables are there
                if "Detailed Mitigation Actions" in html_content:
                    print("✅ Detailed Mitigation Actions text found")
                else:
                    print("❌ Detailed Mitigation Actions NOT found - template section not rendering")
                
                # Print a sample of the Malaysian resources section to verify it works
                if "Malaysian Resources" in html_content:
                    start = html_content.find("Malaysian Resources")
                    print(f"\n🔍 Sample of Malaysian Resources section:")
                    print(html_content[start:start+400])
                
                return False
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing mitigation system integration...\n")
    test_mitigation_in_response()
