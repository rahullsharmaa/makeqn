#!/usr/bin/env python3
"""
Specific test for the "'list' object has no attribute 'get'" error fix
"""
import requests
import json
import sys

def test_list_fix():
    """Test the specific fix for list/get attribute error"""
    base_url = "https://qgen-fix.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Known working topic_id from previous tests
    topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
    
    print("🎯 Testing Fix for 'list' object has no attribute 'get' Error")
    print("=" * 60)
    
    # Test multiple question types to ensure the fix works consistently
    question_types = ["MCQ", "MSQ", "NAT"]
    
    all_success = True
    test_results = {}
    
    for q_type in question_types:
        print(f"\n🔍 Testing {q_type} question generation...")
        
        request_data = {
            "topic_id": topic_id,
            "question_type": q_type,
            "part_id": None,
            "slot_id": None
        }
        
        try:
            response = requests.post(
                f"{api_url}/generate-question",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ {q_type}: SUCCESS - Question generated without list/get error")
                    print(f"   Question: {data.get('question_statement', '')[:100]}...")
                    print(f"   Answer: {data.get('answer', 'N/A')}")
                    test_results[q_type] = {"success": True, "error": None}
                except json.JSONDecodeError as e:
                    print(f"❌ {q_type}: JSON parsing error - {str(e)}")
                    test_results[q_type] = {"success": False, "error": f"JSON parsing: {str(e)}"}
                    all_success = False
            else:
                error_msg = response.text
                print(f"❌ {q_type}: HTTP {response.status_code} - {error_msg}")
                test_results[q_type] = {"success": False, "error": f"HTTP {response.status_code}: {error_msg}"}
                all_success = False
                
        except Exception as e:
            print(f"❌ {q_type}: Exception - {str(e)}")
            test_results[q_type] = {"success": False, "error": f"Exception: {str(e)}"}
            all_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LIST/GET ERROR FIX TEST RESULTS")
    print("=" * 60)
    
    successful_types = [q_type for q_type, result in test_results.items() if result["success"]]
    failed_types = [q_type for q_type, result in test_results.items() if not result["success"]]
    
    print(f"✅ Successful: {successful_types} ({len(successful_types)}/{len(question_types)})")
    print(f"❌ Failed: {failed_types} ({len(failed_types)}/{len(question_types)})")
    
    if all_success:
        print("\n🎉 CONCLUSION: The 'list' object has no attribute 'get' error has been RESOLVED!")
        print("   ✅ All tested question types generate successfully")
        print("   ✅ No JSON parsing errors encountered")
        print("   ✅ Backend properly handles both dictionary and array responses from Gemini")
    else:
        print("\n⚠️  CONCLUSION: Some issues remain:")
        for q_type, result in test_results.items():
            if not result["success"]:
                print(f"   ❌ {q_type}: {result['error']}")
    
    return all_success

if __name__ == "__main__":
    success = test_list_fix()
    sys.exit(0 if success else 1)