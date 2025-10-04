#!/usr/bin/env python3
"""
Specific test for the '[object Object]' error investigation
Based on the review request requirements
"""

import requests
import json
import sys

def test_object_object_error():
    """Test the specific scenario mentioned in the review request"""
    base_url = "https://questgen-agent-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    headers = {'Content-Type': 'application/json'}
    
    print("🔍 TESTING '[object Object]' ERROR - SPECIFIC SCENARIO")
    print("=" * 60)
    
    # Test 1: Exact scenario from review request
    print("\n1️⃣ Testing /start-auto-generation with exact sample data from review request")
    print("-" * 50)
    
    url = f"{api_url}/start-auto-generation"
    params = {
        "exam_id": "test",
        "course_id": "test", 
        "generation_mode": "new_questions"
    }
    body = {
        "correct_marks": 4.0,
        "incorrect_marks": -1.0, 
        "skipped_marks": 0.0,
        "time_minutes": 2.0,
        "total_questions": 10
    }
    
    print(f"URL: {url}")
    print(f"Query Params: {params}")
    print(f"Request Body: {json.dumps(body, indent=2)}")
    
    try:
        response = requests.post(url, json=body, params=params, headers=headers, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Raw Response Text: {response.text}")
        
        # Analyze the error response structure
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"\nParsed Error Response:")
                print(json.dumps(error_data, indent=2))
                
                # Check if it's an array or object
                if isinstance(error_data, list):
                    print(f"\n⚠️ ERROR RESPONSE IS AN ARRAY with {len(error_data)} items")
                    for i, item in enumerate(error_data):
                        print(f"  Item {i}: {item}")
                elif isinstance(error_data, dict):
                    print(f"\n⚠️ ERROR RESPONSE IS AN OBJECT with keys: {list(error_data.keys())}")
                    
                    # Check detail field specifically
                    if 'detail' in error_data:
                        detail = error_data['detail']
                        print(f"\nDetail field type: {type(detail)}")
                        print(f"Detail content: {detail}")
                        
                        if isinstance(detail, list):
                            print(f"⚠️ DETAIL IS AN ARRAY with {len(detail)} validation errors")
                            for i, validation_error in enumerate(detail):
                                print(f"  Validation Error {i}: {validation_error}")
                        elif isinstance(detail, str):
                            print(f"⚠️ DETAIL IS A STRING: {detail}")
                        else:
                            print(f"⚠️ DETAIL IS {type(detail)}: {detail}")
                            
            except json.JSONDecodeError as e:
                print(f"\n❌ Could not parse error response as JSON: {e}")
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"\n❌ Request failed with exception: {e}")
    
    # Test 2: Test with missing required fields
    print("\n\n2️⃣ Testing with missing required fields to trigger validation errors")
    print("-" * 50)
    
    empty_body = {}
    
    try:
        response = requests.post(url, json=empty_body, params=params, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")
        
        if response.status_code == 422:  # Validation error
            try:
                validation_errors = response.json()
                print(f"\nValidation Errors Structure:")
                print(json.dumps(validation_errors, indent=2))
                
                if isinstance(validation_errors, dict) and 'detail' in validation_errors:
                    detail = validation_errors['detail']
                    if isinstance(detail, list):
                        print(f"\n✅ FOUND THE ISSUE! Validation errors return as ARRAY in 'detail' field")
                        print(f"Number of validation errors: {len(detail)}")
                        print(f"First error: {detail[0] if detail else 'None'}")
                        
                        # This is likely what causes [object Object] in frontend
                        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
                        print(f"   - FastAPI/Pydantic returns validation errors as an array")
                        print(f"   - Frontend likely tries to display this array directly")
                        print(f"   - JavaScript converts array to '[object Object]' when displayed as string")
                        
            except json.JSONDecodeError:
                print("Could not parse validation error response")
                
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 3: Test with invalid data types
    print("\n\n3️⃣ Testing with invalid data types")
    print("-" * 50)
    
    invalid_body = {
        "correct_marks": "invalid_string",
        "incorrect_marks": "invalid_string",
        "skipped_marks": "invalid_string", 
        "time_minutes": "invalid_string",
        "total_questions": "invalid_string"
    }
    
    try:
        response = requests.post(url, json=invalid_body, params=params, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            validation_errors = response.json()
            if isinstance(validation_errors, dict) and 'detail' in validation_errors:
                detail = validation_errors['detail']
                if isinstance(detail, list):
                    print(f"✅ Confirmed: {len(detail)} validation errors returned as array")
                    print(f"Sample error: {detail[0] if detail else 'None'}")
                    
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test 4: Check what actual exam_id and course_id values exist
    print("\n\n4️⃣ Checking actual exam_id and course_id values in database")
    print("-" * 50)
    
    try:
        # Get exams
        exams_response = requests.get(f"{api_url}/exams", headers=headers, timeout=30)
        if exams_response.status_code == 200:
            exams = exams_response.json()
            print(f"✅ Found {len(exams)} exams in database:")
            for exam in exams:
                print(f"  - {exam.get('name', 'N/A')} (ID: {exam.get('id', 'N/A')})")
            
            # Test with first real exam
            if exams:
                real_exam_id = exams[0]['id']
                print(f"\n🔍 Testing with real exam_id: {real_exam_id}")
                
                # Get courses for this exam
                courses_response = requests.get(f"{api_url}/courses/{real_exam_id}", headers=headers, timeout=30)
                if courses_response.status_code == 200:
                    courses = courses_response.json()
                    print(f"✅ Found {len(courses)} courses for this exam:")
                    for course in courses:
                        print(f"  - {course.get('name', 'N/A')} (ID: {course.get('id', 'N/A')})")
                    
                    if courses:
                        real_course_id = courses[0]['id']
                        print(f"\n🔍 Testing start-auto-generation with REAL IDs:")
                        print(f"  exam_id: {real_exam_id}")
                        print(f"  course_id: {real_course_id}")
                        
                        real_params = {
                            "exam_id": real_exam_id,
                            "course_id": real_course_id,
                            "generation_mode": "new_questions"
                        }
                        
                        response = requests.post(url, json=body, params=real_params, headers=headers, timeout=30)
                        print(f"  Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("  ✅ SUCCESS with real IDs!")
                            success_data = response.json()
                            print(f"  Session ID: {success_data.get('session_id', 'N/A')}")
                            print(f"  Total Topics: {success_data.get('total_topics', 'N/A')}")
                            print(f"  Status: {success_data.get('status', 'N/A')}")
                        else:
                            print(f"  ❌ Still failed with real IDs: {response.text}")
                            
    except Exception as e:
        print(f"Failed to get exams: {e}")
    
    # Test 5: Test all-topics-with-weightage endpoint
    print("\n\n5️⃣ Testing /all-topics-with-weightage/{course_id} endpoint")
    print("-" * 50)
    
    # Test with invalid course_id first
    test_course_id = "test"
    try:
        response = requests.get(f"{api_url}/all-topics-with-weightage/{test_course_id}", headers=headers, timeout=30)
        print(f"Testing with course_id 'test':")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 500:
            error_data = response.json()
            print(f"  ✅ Confirmed: Invalid UUID causes 500 error")
            print(f"  Error detail: {error_data.get('detail', 'N/A')}")
            
    except Exception as e:
        print(f"Request failed: {e}")
    
    # Test with valid course_id if we found one
    if 'real_course_id' in locals():
        try:
            response = requests.get(f"{api_url}/all-topics-with-weightage/{real_course_id}", headers=headers, timeout=30)
            print(f"\nTesting with real course_id '{real_course_id}':")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                topics_data = response.json()
                print(f"  ✅ SUCCESS: Found {len(topics_data)} topics with weightage")
                if topics_data:
                    sample_topic = topics_data[0]
                    print(f"  Sample topic: {sample_topic.get('name', 'N/A')} (weightage: {sample_topic.get('weightage', 'N/A')})")
            else:
                print(f"  ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("\n\n🎯 FINAL ANALYSIS")
    print("=" * 60)
    print("ROOT CAUSE OF '[object Object]' ERROR:")
    print("1. FastAPI/Pydantic validation errors return as an ARRAY in the 'detail' field")
    print("2. When frontend tries to display this array directly, JavaScript converts it to '[object Object]'")
    print("3. The error occurs with:")
    print("   - Invalid UUID format for exam_id/course_id (causes 500 error)")
    print("   - Missing required fields (causes 422 error with array of validation errors)")
    print("   - Invalid data types (causes 422 error with array of validation errors)")
    print("\nSOLUTION:")
    print("- Frontend needs to properly handle validation error arrays")
    print("- Check if error.detail is an array and format it appropriately")
    print("- Use real UUID values for exam_id and course_id parameters")

if __name__ == "__main__":
    test_object_object_error()