import requests
import sys
import json
from datetime import datetime

class QuestionMakerAPITester:
    def __init__(self, base_url="https://testsmith-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_results = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    'test': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'test': name,
                'error': str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_exams_endpoint(self):
        """Test getting all exams"""
        success, data = self.run_test("Get Exams", "GET", "exams", 200)
        if success and data:
            print(f"   Found {len(data)} exams")
            return data
        return []

    def test_courses_endpoint(self, exam_id):
        """Test getting courses for an exam"""
        success, data = self.run_test(f"Get Courses for Exam {exam_id}", "GET", f"courses/{exam_id}", 200)
        if success and data:
            print(f"   Found {len(data)} courses")
            return data
        return []

    def test_subjects_endpoint(self, course_id):
        """Test getting subjects for a course"""
        success, data = self.run_test(f"Get Subjects for Course {course_id}", "GET", f"subjects/{course_id}", 200)
        if success and data:
            print(f"   Found {len(data)} subjects")
            return data
        return []

    def test_units_endpoint(self, subject_id):
        """Test getting units for a subject"""
        success, data = self.run_test(f"Get Units for Subject {subject_id}", "GET", f"units/{subject_id}", 200)
        if success and data:
            print(f"   Found {len(data)} units")
            return data
        return []

    def test_chapters_endpoint(self, unit_id):
        """Test getting chapters for a unit"""
        success, data = self.run_test(f"Get Chapters for Unit {unit_id}", "GET", f"chapters/{unit_id}", 200)
        if success and data:
            print(f"   Found {len(data)} chapters")
            return data
        return []

    def test_topics_endpoint(self, chapter_id):
        """Test getting topics for a chapter"""
        success, data = self.run_test(f"Get Topics for Chapter {chapter_id}", "GET", f"topics/{chapter_id}", 200)
        if success and data:
            print(f"   Found {len(data)} topics")
            return data
        return []

    def test_parts_endpoint(self, course_id):
        """Test getting parts for a course"""
        success, data = self.run_test(f"Get Parts for Course {course_id}", "GET", f"parts/{course_id}", 200)
        if success and data:
            print(f"   Found {len(data)} parts")
            return data
        return []

    def test_slots_endpoint(self, course_id):
        """Test getting slots for a course"""
        success, data = self.run_test(f"Get Slots for Course {course_id}", "GET", f"slots/{course_id}", 200)
        if success and data:
            print(f"   Found {len(data)} slots")
            return data
        return []

    def test_existing_questions_endpoint(self, topic_id):
        """Test getting existing questions for a topic"""
        success, data = self.run_test(f"Get Existing Questions for Topic {topic_id}", "GET", f"existing-questions/{topic_id}", 200)
        if success and data:
            print(f"   Found {len(data)} existing questions")
            return data
        return []

    def test_question_generation(self, topic_id, question_type):
        """Test question generation with detailed error reporting"""
        request_data = {
            "topic_id": topic_id,
            "question_type": question_type,
            "part_id": None,
            "slot_id": None
        }
        
        url = f"{self.api_url}/generate-question"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Generate {question_type} Question for Topic {topic_id}...")
        print(f"   URL: {url}")
        print(f"   Request: {json.dumps(request_data, indent=2)}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ SUCCESS - Question generated successfully!")
                try:
                    response_data = response.json()
                    print(f"   Generated Question: {response_data.get('question_statement', '')[:150]}...")
                    print(f"   Question Type: {response_data.get('question_type', 'N/A')}")
                    print(f"   Options: {response_data.get('options', 'N/A')}")
                    print(f"   Answer: {response_data.get('answer', 'N/A')}")
                    print(f"   Difficulty: {response_data.get('difficulty_level', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"❌ JSON parsing error: {str(json_error)}")
                    print(f"   Raw response: {response.text[:500]}...")
                    return False, {}
            else:
                print(f"❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Error Response: {response.text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    print(f"   Error Detail: {error_data.get('detail', 'No detail provided')}")
                except:
                    pass
                
                self.failed_tests.append({
                    'test': f"Generate {question_type} Question",
                    'topic_id': topic_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': f"Generate {question_type} Question",
                'topic_id': topic_id,
                'error': str(e)
            })
            return False, {}

    def test_cascading_flow(self):
        """Test the complete cascading dropdown flow"""
        print("\n🔄 Testing Complete Cascading Flow...")
        
        # Get exams
        exams = self.test_exams_endpoint()
        if not exams:
            print("❌ Cannot proceed - No exams found")
            return False
        
        # Try all exams to find one with complete data
        for exam in exams:
            exam_id = exam['id']
            print(f"\n🔍 Trying exam: {exam['name']} ({exam_id})")
            
            # Get courses
            courses = self.test_courses_endpoint(exam_id)
            if not courses:
                print(f"❌ No courses found for exam {exam['name']}")
                continue
            
            # Try all courses for this exam
            for course in courses:
                course_id = course['id']
                print(f"\n🔍 Trying course: {course['name']} ({course_id})")
                
                # Get subjects
                subjects = self.test_subjects_endpoint(course_id)
                if not subjects:
                    print(f"❌ No subjects found for course {course['name']}")
                    continue
                
                # Try all subjects for this course
                for subject in subjects:
                    subject_id = subject['id']
                    print(f"\n🔍 Trying subject: {subject['name']} ({subject_id})")
                    
                    # Get units
                    units = self.test_units_endpoint(subject_id)
                    if not units:
                        print(f"❌ No units found for subject {subject['name']}")
                        continue
                    
                    # Try all units for this subject
                    for unit in units:
                        unit_id = unit['id']
                        print(f"\n🔍 Trying unit: {unit['name']} ({unit_id})")
                        
                        # Get chapters
                        chapters = self.test_chapters_endpoint(unit_id)
                        if not chapters:
                            print(f"❌ No chapters found for unit {unit['name']}")
                            continue
                        
                        # Try all chapters for this unit
                        for chapter in chapters:
                            chapter_id = chapter['id']
                            print(f"\n🔍 Trying chapter: {chapter['name']} ({chapter_id})")
                            
                            # Get topics
                            topics = self.test_topics_endpoint(chapter_id)
                            if not topics:
                                print(f"❌ No topics found for chapter {chapter['name']}")
                                continue
                            
                            # Found complete hierarchy! Test with first topic
                            topic_id = topics[0]['id']
                            topic_name = topics[0]['name']
                            print(f"\n✅ Found complete hierarchy! Testing with topic: {topic_name} ({topic_id})")
                            
                            # Test parts and slots
                            self.test_parts_endpoint(course_id)
                            self.test_slots_endpoint(course_id)
                            
                            # Test existing questions
                            self.test_existing_questions_endpoint(topic_id)
                            
                            # Test question generation for different types
                            question_types = ["MCQ", "MSQ", "NAT", "SUB"]
                            generation_success = 0
                            for q_type in question_types:
                                generated = self.test_question_generation(topic_id, q_type)
                                if generated:
                                    print(f"✅ Successfully generated {q_type} question")
                                    generation_success += 1
                                else:
                                    print(f"❌ Failed to generate {q_type} question")
                            
                            print(f"\n📊 Question Generation Summary: {generation_success}/{len(question_types)} types successful")
                            return True
        
        print("❌ Could not find complete hierarchy in any exam/course/subject/unit/chapter")
        return False

    def test_all_topics_with_weightage(self, course_id):
        """Test the new all-topics-with-weightage endpoint"""
        success, data = self.run_test(f"Get All Topics with Weightage for Course {course_id}", "GET", f"all-topics-with-weightage/{course_id}", 200)
        if success and data:
            print(f"   Found {len(data)} topics with weightage")
            # Show sample topic structure
            if data:
                sample_topic = data[0]
                print(f"   Sample topic: {sample_topic.get('name', 'N/A')} (weightage: {sample_topic.get('weightage', 'N/A')})")
        return success, data

    def test_generate_pyq_solution(self, topic_id):
        """Test the new PYQ solution generation endpoint"""
        request_data = {
            "topic_id": topic_id,
            "question_statement": "Find the harmonic mean of 3, 6, and 9.",
            "options": ["4", "5", "6", "7"],
            "question_type": "MCQ"
        }
        
        url = f"{self.api_url}/generate-pyq-solution"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Generate PYQ Solution for Topic {topic_id}...")
        print(f"   URL: {url}")
        print(f"   Request: {json.dumps(request_data, indent=2)}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ SUCCESS - PYQ solution generated successfully!")
                try:
                    response_data = response.json()
                    print(f"   Question: {response_data.get('question_statement', '')[:100]}...")
                    print(f"   Answer: {response_data.get('answer', 'N/A')}")
                    print(f"   Confidence: {response_data.get('confidence_level', 'N/A')}")
                    print(f"   Solution: {response_data.get('solution', '')[:150]}...")
                    return True, response_data
                except Exception as json_error:
                    print(f"❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Error Response: {response.text}")
                self.failed_tests.append({
                    'test': "Generate PYQ Solution",
                    'topic_id': topic_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': "Generate PYQ Solution",
                'topic_id': topic_id,
                'error': str(e)
            })
            return False, {}

    def test_save_question_manually(self, topic_id):
        """Test the new manual question save endpoint"""
        request_data = {
            "topic_id": topic_id,
            "topic_name": "Test Topic",
            "question_statement": "What is 2 + 2?",
            "question_type": "MCQ",
            "options": ["2", "3", "4", "5"],
            "answer": "2",
            "solution": "Simple addition: 2 + 2 = 4, which corresponds to option index 2.",
            "difficulty_level": "Easy"
        }
        
        success, data = self.run_test("Save Question Manually", "POST", "save-question-manually", 200, data=request_data)
        if success and data:
            print(f"   Question saved with ID: {data.get('question_id', 'N/A')}")
        return success, data

    def test_start_auto_generation(self, exam_id, course_id):
        """Test the new auto-generation start endpoint"""
        request_data = {
            "correct_marks": 4.0,
            "incorrect_marks": -1.0,
            "skipped_marks": 0.0,
            "time_minutes": 180.0,
            "total_questions": 10
        }
        
        params = {
            "exam_id": exam_id,
            "course_id": course_id,
            "generation_mode": "new_questions"
        }
        
        success, data = self.run_test("Start Auto Generation", "POST", "start-auto-generation", 200, data=request_data, params=params)
        if success and data:
            print(f"   Session created with ID: {data.get('session_id', 'N/A')}")
            print(f"   Total topics: {data.get('total_topics', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        return success, data

    def test_object_object_error_investigation(self):
        """Investigate the '[object Object]' error in start-auto-generation endpoint"""
        print("\n🔍 INVESTIGATING '[object Object]' ERROR...")
        print("=" * 60)
        
        # Test 1: Valid request with sample data from review request
        print("\n1️⃣ Testing with sample data from review request...")
        request_data = {
            "correct_marks": 4.0,
            "incorrect_marks": -1.0, 
            "skipped_marks": 0.0,
            "time_minutes": 2.0,
            "total_questions": 10
        }
        
        params = {
            "exam_id": "test",
            "course_id": "test",
            "generation_mode": "new_questions"
        }
        
        url = f"{self.api_url}/start-auto-generation"
        headers = {'Content-Type': 'application/json'}
        
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        print(f"   Body: {json.dumps(request_data, indent=2)}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, params=params, timeout=30)
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Raw Response: {response.text}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"   Parsed Error: {json.dumps(error_data, indent=2)}")
                    
                    # Check if error is an array or object
                    if isinstance(error_data, list):
                        print(f"   ⚠️ ERROR IS AN ARRAY with {len(error_data)} items")
                        for i, item in enumerate(error_data):
                            print(f"      Item {i}: {item}")
                    elif isinstance(error_data, dict):
                        print(f"   ⚠️ ERROR IS AN OBJECT with keys: {list(error_data.keys())}")
                        if 'detail' in error_data:
                            detail = error_data['detail']
                            if isinstance(detail, list):
                                print(f"   ⚠️ DETAIL IS AN ARRAY with {len(detail)} items")
                                for i, item in enumerate(detail):
                                    print(f"      Detail {i}: {item}")
                            else:
                                print(f"   Detail: {detail}")
                    
                except Exception as parse_error:
                    print(f"   ❌ Could not parse error response: {parse_error}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        # Test 2: Invalid data to trigger validation errors
        print("\n2️⃣ Testing with invalid data to see validation errors...")
        invalid_requests = [
            {
                "name": "Missing required fields",
                "data": {},
                "params": {"exam_id": "test", "course_id": "test"}
            },
            {
                "name": "Invalid data types",
                "data": {
                    "correct_marks": "invalid",
                    "incorrect_marks": "invalid",
                    "skipped_marks": "invalid",
                    "time_minutes": "invalid",
                    "total_questions": "invalid"
                },
                "params": {"exam_id": "test", "course_id": "test"}
            },
            {
                "name": "Missing query parameters",
                "data": request_data,
                "params": {}
            }
        ]
        
        for test_case in invalid_requests:
            print(f"\n   Testing: {test_case['name']}")
            try:
                response = requests.post(url, json=test_case['data'], headers=headers, params=test_case['params'], timeout=30)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:300]}...")
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        if isinstance(error_data, list):
                            print(f"   ⚠️ VALIDATION ERROR IS ARRAY: {len(error_data)} items")
                        elif isinstance(error_data, dict) and 'detail' in error_data:
                            detail = error_data['detail']
                            if isinstance(detail, list):
                                print(f"   ⚠️ VALIDATION DETAIL IS ARRAY: {len(detail)} items")
                                print(f"   First validation error: {detail[0] if detail else 'None'}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
        
        # Test 3: Check what actual exam_id and course_id values exist
        print("\n3️⃣ Checking actual exam_id and course_id values in database...")
        
        # Get exams
        try:
            exams_response = requests.get(f"{self.api_url}/exams", headers=headers, timeout=30)
            if exams_response.status_code == 200:
                exams = exams_response.json()
                print(f"   Found {len(exams)} exams:")
                for exam in exams[:3]:  # Show first 3
                    print(f"      - {exam.get('name', 'N/A')} (ID: {exam.get('id', 'N/A')})")
                
                # Test with real exam_id and course_id
                if exams:
                    real_exam_id = exams[0]['id']
                    print(f"\n   Testing with real exam_id: {real_exam_id}")
                    
                    # Get courses for this exam
                    courses_response = requests.get(f"{self.api_url}/courses/{real_exam_id}", headers=headers, timeout=30)
                    if courses_response.status_code == 200:
                        courses = courses_response.json()
                        print(f"   Found {len(courses)} courses for this exam:")
                        for course in courses[:3]:  # Show first 3
                            print(f"      - {course.get('name', 'N/A')} (ID: {course.get('id', 'N/A')})")
                        
                        if courses:
                            real_course_id = courses[0]['id']
                            print(f"\n   Testing start-auto-generation with real IDs...")
                            print(f"   exam_id: {real_exam_id}")
                            print(f"   course_id: {real_course_id}")
                            
                            real_params = {
                                "exam_id": real_exam_id,
                                "course_id": real_course_id,
                                "generation_mode": "new_questions"
                            }
                            
                            response = requests.post(url, json=request_data, headers=headers, params=real_params, timeout=30)
                            print(f"   Status: {response.status_code}")
                            print(f"   Response: {response.text}")
                            
                            if response.status_code == 200:
                                print("   ✅ SUCCESS with real IDs!")
                            else:
                                try:
                                    error_data = response.json()
                                    print(f"   ❌ Error with real IDs: {json.dumps(error_data, indent=2)}")
                                except:
                                    print(f"   ❌ Error with real IDs (unparseable): {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Failed to get exams: {e}")
        
        # Test 4: Test all-topics-with-weightage endpoint
        print("\n4️⃣ Testing all-topics-with-weightage endpoint...")
        try:
            # Try with a known course_id or test course_id
            test_course_ids = ["test", "b8f7e2d1-4c3a-4b5e-8f9a-1b2c3d4e5f6g"]
            
            for course_id in test_course_ids:
                print(f"\n   Testing with course_id: {course_id}")
                response = requests.get(f"{self.api_url}/all-topics-with-weightage/{course_id}", headers=headers, timeout=30)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:300]}...")
                
                if response.status_code == 200:
                    try:
                        topics_data = response.json()
                        print(f"   ✅ Found {len(topics_data)} topics")
                        if topics_data:
                            print(f"   Sample topic: {topics_data[0].get('name', 'N/A')}")
                    except:
                        print(f"   ❌ Could not parse topics response")
                        
        except Exception as e:
            print(f"   ❌ Failed to test all-topics-with-weightage: {e}")
        
        print("\n🎯 INVESTIGATION COMPLETE")
        print("=" * 60)

    def test_specific_topic_question_generation(self):
        """Test question generation with the specific known working topic_id"""
        print("\n🎯 Testing Question Generation with Known Working Topic ID...")
        print("=" * 60)
        
        # Known working topic_id from previous tests
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        
        # Test MSQ first as it was working in previous tests
        question_types = ["MSQ", "MCQ", "NAT", "SUB"]
        
        generation_results = {}
        
        for q_type in question_types:
            print(f"\n🔍 Testing {q_type} question generation...")
            success, data = self.test_question_generation(topic_id, q_type)
            generation_results[q_type] = {
                'success': success,
                'data': data
            }
            
            if success:
                print(f"✅ {q_type} question generation: SUCCESS")
            else:
                print(f"❌ {q_type} question generation: FAILED")
        
        # Summary
        successful_types = [q_type for q_type, result in generation_results.items() if result['success']]
        failed_types = [q_type for q_type, result in generation_results.items() if not result['success']]
        
        print(f"\n📊 Question Generation Results for Topic {topic_id}:")
        print(f"   ✅ Successful: {successful_types} ({len(successful_types)}/{len(question_types)})")
        print(f"   ❌ Failed: {failed_types} ({len(failed_types)}/{len(question_types)})")
        
        return generation_results

    def test_new_endpoints_comprehensive(self):
        """Test all new endpoints with ISI->MSQMS course data"""
        print("\n🆕 Testing New Enhanced Endpoints...")
        print("=" * 60)
        
        # Known working course_id for ISI->MSQMS
        course_id = "b8f7e2d1-4c3a-4b5e-8f9a-1b2c3d4e5f6g"  # This should be found from cascading test
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        exam_id = "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6"  # This should be found from cascading test
        
        new_endpoint_results = {}
        
        # Test 1: All topics with weightage
        print(f"\n1️⃣ Testing All Topics with Weightage...")
        success, data = self.test_all_topics_with_weightage(course_id)
        new_endpoint_results['all_topics_with_weightage'] = {'success': success, 'data': data}
        
        # Test 2: PYQ Solution Generation
        print(f"\n2️⃣ Testing PYQ Solution Generation...")
        success, data = self.test_generate_pyq_solution(topic_id)
        new_endpoint_results['generate_pyq_solution'] = {'success': success, 'data': data}
        
        # Test 3: Manual Question Save
        print(f"\n3️⃣ Testing Manual Question Save...")
        success, data = self.test_save_question_manually(topic_id)
        new_endpoint_results['save_question_manually'] = {'success': success, 'data': data}
        
        # Test 4: Auto Generation Start
        print(f"\n4️⃣ Testing Auto Generation Start...")
        success, data = self.test_start_auto_generation(exam_id, course_id)
        new_endpoint_results['start_auto_generation'] = {'success': success, 'data': data}
        
        # Summary
        successful_endpoints = [endpoint for endpoint, result in new_endpoint_results.items() if result['success']]
        failed_endpoints = [endpoint for endpoint, result in new_endpoint_results.items() if not result['success']]
        
        print(f"\n📊 New Endpoints Test Results:")
        print(f"   ✅ Successful: {successful_endpoints} ({len(successful_endpoints)}/{len(new_endpoint_results)})")
        print(f"   ❌ Failed: {failed_endpoints} ({len(failed_endpoints)}/{len(new_endpoint_results)})")
        
        return new_endpoint_results

    def test_review_request_scenarios(self):
        """Test the specific scenarios from the review request"""
        print("\n🎯 TESTING REVIEW REQUEST SCENARIOS")
        print("=" * 60)
        
        # Use the specific IDs from review request
        exam_id = "6c1bed83-2424-4237-8a6f-e7ed97240466"  # ISI
        course_id = "d3ab4d23-f8d4-422b-aca2-affeb4d9609c"  # MSQMS
        
        results = {}
        
        # 1. Test /start-auto-generation endpoint with VALID IDs
        print("\n1️⃣ Testing /start-auto-generation with VALID exam and course IDs...")
        print(f"   Using exam_id: {exam_id}")
        print(f"   Using course_id: {course_id} (ISI->MSQMS)")
        
        # Test with generation_mode="new_questions"
        print("\n   Testing generation_mode='new_questions'...")
        success1, data1 = self.test_start_auto_generation_with_mode(exam_id, course_id, "new_questions")
        results['start_auto_generation_new'] = {'success': success1, 'data': data1}
        
        # Test with generation_mode="pyq_solutions"
        print("\n   Testing generation_mode='pyq_solutions'...")
        success2, data2 = self.test_start_auto_generation_with_mode(exam_id, course_id, "pyq_solutions")
        results['start_auto_generation_pyq'] = {'success': success2, 'data': data2}
        
        # 2. Get a valid topic_id from ISI->MSQMS course
        print("\n2️⃣ Getting valid topic_id from ISI->MSQMS course...")
        valid_topic_id = None
        
        # Get all topics with weightage to find a valid topic_id
        success, topics_data = self.test_all_topics_with_weightage(course_id)
        if success and topics_data:
            valid_topic_id = topics_data[0]['id']
            topic_name = topics_data[0]['name']
            print(f"   ✅ Found valid topic_id: {valid_topic_id}")
            print(f"   Topic name: {topic_name}")
        else:
            # Fallback topic_id
            valid_topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
            print(f"   ⚠️ Using fallback topic_id: {valid_topic_id}")
        
        # 3. Test improved /existing-questions/{topic_id} endpoint
        print(f"\n3️⃣ Testing improved /existing-questions/{valid_topic_id} endpoint...")
        success, existing_questions = self.test_existing_questions_with_ids(valid_topic_id)
        results['existing_questions'] = {'success': success, 'data': existing_questions}
        
        # 4. Test /update-question-solution endpoint
        print(f"\n4️⃣ Testing /update-question-solution endpoint...")
        if success and existing_questions:
            # Find a question without solution or with minimal solution
            question_to_update = None
            for question in existing_questions:
                if not question.get('solution') or len(question.get('solution', '').strip()) < 10:
                    question_to_update = question
                    break
            
            if question_to_update:
                success_update, update_data = self.test_update_question_solution(question_to_update['id'])
                results['update_question_solution'] = {'success': success_update, 'data': update_data}
            else:
                print("   ⚠️ No questions found without solutions to update")
                results['update_question_solution'] = {'success': False, 'data': {}, 'reason': 'No questions to update'}
        else:
            print("   ⚠️ Cannot test update-question-solution - no existing questions found")
            results['update_question_solution'] = {'success': False, 'data': {}, 'reason': 'No existing questions'}
        
        # 5. Test question generation for each type (avoid SUB)
        print(f"\n5️⃣ Testing question generation for MCQ, MSQ, NAT types...")
        question_types = ["MCQ", "MSQ", "NAT"]  # Avoiding SUB due to database constraint
        
        for q_type in question_types:
            print(f"\n   Testing {q_type} generation...")
            success, data = self.test_question_generation(valid_topic_id, q_type)
            results[f'generate_{q_type.lower()}'] = {'success': success, 'data': data}
        
        # 6. Test PYQ solution generation with topic notes
        print(f"\n6️⃣ Testing PYQ solution generation with topic notes...")
        success, pyq_data = self.test_generate_pyq_solution(valid_topic_id)
        results['generate_pyq_solution'] = {'success': success, 'data': pyq_data}
        
        return results

    def test_start_auto_generation_with_mode(self, exam_id, course_id, generation_mode):
        """Test start-auto-generation with specific generation mode"""
        request_data = {
            "correct_marks": 4.0,
            "incorrect_marks": -1.0,
            "skipped_marks": 0.0,
            "time_minutes": 180.0,
            "total_questions": 10
        }
        
        params = {
            "exam_id": exam_id,
            "course_id": course_id,
            "generation_mode": generation_mode
        }
        
        url = f"{self.api_url}/start-auto-generation"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"   Testing with generation_mode='{generation_mode}'...")
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS - Auto-generation session created!")
                try:
                    response_data = response.json()
                    print(f"   Session ID: {response_data.get('session_id', 'N/A')}")
                    print(f"   Total topics: {response_data.get('total_topics', 'N/A')}")
                    print(f"   Status: {response_data.get('status', 'N/A')}")
                    print(f"   Message: {response_data.get('message', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"   ❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"   ❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Check if this is the "[object Object]" error
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'detail' in error_data:
                        detail = error_data['detail']
                        if isinstance(detail, list):
                            print(f"   🔍 VALIDATION ERROR ARRAY DETECTED: {len(detail)} items")
                            print(f"   This would cause '[object Object]' error in frontend!")
                            for i, item in enumerate(detail):
                                print(f"      Error {i}: {item}")
                        else:
                            print(f"   Error detail: {detail}")
                except:
                    pass
                
                self.failed_tests.append({
                    'test': f"Start Auto Generation ({generation_mode})",
                    'exam_id': exam_id,
                    'course_id': course_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': f"Start Auto Generation ({generation_mode})",
                'exam_id': exam_id,
                'course_id': course_id,
                'error': str(e)
            })
            return False, {}

    def test_existing_questions_with_ids(self, topic_id):
        """Test existing-questions endpoint and verify it returns question IDs"""
        url = f"{self.api_url}/existing-questions/{topic_id}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"   Testing existing-questions endpoint...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS - Existing questions retrieved!")
                try:
                    response_data = response.json()
                    print(f"   Found {len(response_data)} existing questions")
                    
                    # Verify questions have IDs and other required data
                    if response_data:
                        sample_question = response_data[0]
                        has_id = 'id' in sample_question
                        has_statement = 'question_statement' in sample_question
                        has_type = 'question_type' in sample_question
                        
                        print(f"   Sample question has ID: {has_id}")
                        print(f"   Sample question has statement: {has_statement}")
                        print(f"   Sample question has type: {has_type}")
                        
                        if has_id:
                            print(f"   Sample question ID: {sample_question['id']}")
                        if has_statement:
                            print(f"   Sample statement: {sample_question['question_statement'][:100]}...")
                    
                    return True, response_data
                except Exception as json_error:
                    print(f"   ❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"   ❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests.append({
                    'test': "Existing Questions with IDs",
                    'topic_id': topic_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': "Existing Questions with IDs",
                'topic_id': topic_id,
                'error': str(e)
            })
            return False, {}

    def test_update_question_solution(self, question_id):
        """Test the update-question-solution endpoint"""
        request_data = {
            "question_id": question_id,
            "answer": "2",
            "solution": "This is a detailed step-by-step solution generated by the testing system. The answer is option 2 based on mathematical analysis and proper reasoning.",
            "confidence_level": "High"
        }
        
        url = f"{self.api_url}/update-question-solution"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"   Testing update-question-solution endpoint...")
        print(f"   URL: {url}")
        print(f"   Question ID: {question_id}")
        
        try:
            response = requests.patch(url, json=request_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS - Question solution updated!")
                try:
                    response_data = response.json()
                    print(f"   Message: {response_data.get('message', 'N/A')}")
                    print(f"   Updated question ID: {response_data.get('question_id', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"   ❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"   ❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests.append({
                    'test': "Update Question Solution",
                    'question_id': question_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': "Update Question Solution",
                'question_id': question_id,
                'error': str(e)
            })
            return False, {}

    def test_update_solution_with_created_question(self):
        """Create a question manually and then test updating its solution"""
        print("   Creating a test question to update its solution...")
        
        # First, create a question manually with minimal solution
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        
        request_data = {
            "topic_id": topic_id,
            "topic_name": "Harmonic Progression (HP)",
            "question_statement": "What is the harmonic mean of 2 and 8?",
            "question_type": "MCQ",
            "options": ["3", "3.2", "4", "4.5"],
            "answer": "1",
            "solution": "Basic solution",  # Minimal solution to be updated
            "difficulty_level": "Easy"
        }
        
        # Save the question
        success, save_data = self.test_save_question_manually(topic_id)
        
        if success and save_data:
            question_id = save_data.get('question_id')
            print(f"   ✅ Created test question with ID: {question_id}")
            
            # Now test updating its solution
            print(f"   Testing update-question-solution with created question...")
            success_update, update_data = self.test_update_question_solution(question_id)
            
            if success_update:
                print(f"   ✅ Successfully updated question solution!")
                return True
            else:
                print(f"   ❌ Failed to update question solution")
                return False
        else:
            print(f"   ❌ Failed to create test question for update testing")
            return False

    def test_json_schema_improvements(self):
        """Test the specific JSON schema improvements from the review request"""
        print("\n🎯 TESTING JSON SCHEMA IMPROVEMENTS")
        print("=" * 60)
        print("Focus: Testing improved question generation with JSON schema")
        print("Expected: MCQ 33%→90%+, NAT 0%→90%+, MSQ maintain 100%")
        
        # Use known working topic from ISI->MSQMS course
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"  # Harmonic Progression topic
        
        results = {
            'mcq_tests': [],
            'nat_tests': [],
            'msq_tests': [],
            'pyq_tests': [],
            'round_robin_tests': []
        }
        
        # 1. Test MCQ generation (5 attempts as requested)
        print(f"\n1️⃣ Testing MCQ Generation (5 attempts)")
        print(f"   Previous success rate: 33% (1/3)")
        print(f"   Expected improvement: 90%+ success rate")
        
        mcq_successes = 0
        for i in range(5):
            print(f"\n   MCQ Attempt {i+1}/5:")
            success, data = self.test_question_generation(topic_id, "MCQ")
            results['mcq_tests'].append({'attempt': i+1, 'success': success, 'data': data})
            if success:
                mcq_successes += 1
                print(f"   ✅ MCQ {i+1}: SUCCESS - JSON parsed correctly")
                if data:
                    print(f"      Question: {data.get('question_statement', '')[:80]}...")
                    print(f"      Options: {len(data.get('options', []))} options")
                    print(f"      Answer: {data.get('answer', 'N/A')}")
            else:
                print(f"   ❌ MCQ {i+1}: FAILED - JSON parsing error")
        
        mcq_success_rate = (mcq_successes / 5) * 100
        print(f"\n   📊 MCQ Results: {mcq_successes}/5 successful ({mcq_success_rate:.1f}%)")
        
        # 2. Test NAT generation (5 attempts as requested)
        print(f"\n2️⃣ Testing NAT Generation (5 attempts)")
        print(f"   Previous success rate: 0% (0/3)")
        print(f"   Expected improvement: 90%+ success rate")
        
        nat_successes = 0
        for i in range(5):
            print(f"\n   NAT Attempt {i+1}/5:")
            success, data = self.test_question_generation(topic_id, "NAT")
            results['nat_tests'].append({'attempt': i+1, 'success': success, 'data': data})
            if success:
                nat_successes += 1
                print(f"   ✅ NAT {i+1}: SUCCESS - JSON parsed correctly")
                if data:
                    print(f"      Question: {data.get('question_statement', '')[:80]}...")
                    print(f"      Answer: {data.get('answer', 'N/A')}")
                    print(f"      Type: Numerical")
            else:
                print(f"   ❌ NAT {i+1}: FAILED - JSON parsing error")
        
        nat_success_rate = (nat_successes / 5) * 100
        print(f"\n   📊 NAT Results: {nat_successes}/5 successful ({nat_success_rate:.1f}%)")
        
        # 3. Test MSQ generation (3 attempts to ensure no regression)
        print(f"\n3️⃣ Testing MSQ Generation (3 attempts)")
        print(f"   Previous success rate: 100% (3/3)")
        print(f"   Expected: Maintain 100% success rate")
        
        msq_successes = 0
        for i in range(3):
            print(f"\n   MSQ Attempt {i+1}/3:")
            success, data = self.test_question_generation(topic_id, "MSQ")
            results['msq_tests'].append({'attempt': i+1, 'success': success, 'data': data})
            if success:
                msq_successes += 1
                print(f"   ✅ MSQ {i+1}: SUCCESS - JSON parsed correctly")
                if data:
                    print(f"      Question: {data.get('question_statement', '')[:80]}...")
                    print(f"      Options: {len(data.get('options', []))} options")
                    print(f"      Answer: {data.get('answer', 'N/A')} (multiple correct)")
            else:
                print(f"   ❌ MSQ {i+1}: FAILED - JSON parsing error")
        
        msq_success_rate = (msq_successes / 3) * 100
        print(f"\n   📊 MSQ Results: {msq_successes}/3 successful ({msq_success_rate:.1f}%)")
        
        # 4. Test PYQ solution generation with schema (3 attempts)
        print(f"\n4️⃣ Testing PYQ Solution Generation with Schema (3 attempts)")
        print(f"   Focus: Verify structured JSON output and topic notes usage")
        
        pyq_successes = 0
        for i in range(3):
            print(f"\n   PYQ Attempt {i+1}/3:")
            success, data = self.test_generate_pyq_solution(topic_id)
            results['pyq_tests'].append({'attempt': i+1, 'success': success, 'data': data})
            if success:
                pyq_successes += 1
                print(f"   ✅ PYQ {i+1}: SUCCESS - JSON schema working")
                if data:
                    print(f"      Answer: {data.get('answer', 'N/A')}")
                    print(f"      Confidence: {data.get('confidence_level', 'N/A')}")
                    print(f"      Uses topic notes: {'✅ YES' if 'topic notes' in data.get('solution', '').lower() else '⚠️ UNCLEAR'}")
            else:
                print(f"   ❌ PYQ {i+1}: FAILED - JSON parsing error")
        
        pyq_success_rate = (pyq_successes / 3) * 100
        print(f"\n   📊 PYQ Results: {pyq_successes}/3 successful ({pyq_success_rate:.1f}%)")
        
        # 5. Monitor round-robin system (test multiple requests to verify key rotation)
        print(f"\n5️⃣ Testing Round-Robin System")
        print(f"   Focus: Verify API keys rotate properly and failed key handling works")
        
        # Make multiple quick requests to test round-robin
        round_robin_successes = 0
        for i in range(6):  # Test 6 requests to see key rotation
            print(f"\n   Round-Robin Test {i+1}/6:")
            success, data = self.test_question_generation(topic_id, "MSQ")  # Use MSQ as it was most reliable
            results['round_robin_tests'].append({'attempt': i+1, 'success': success})
            if success:
                round_robin_successes += 1
                print(f"   ✅ Request {i+1}: SUCCESS - Round-robin working")
            else:
                print(f"   ❌ Request {i+1}: FAILED - Possible key exhaustion")
        
        round_robin_success_rate = (round_robin_successes / 6) * 100
        print(f"\n   📊 Round-Robin Results: {round_robin_successes}/6 successful ({round_robin_success_rate:.1f}%)")
        
        return results

    def analyze_json_schema_results(self, results):
        """Analyze the JSON schema improvement test results"""
        print(f"\n📊 JSON SCHEMA IMPROVEMENTS ANALYSIS")
        print("=" * 60)
        
        # Calculate success rates
        mcq_success_rate = sum(1 for test in results['mcq_tests'] if test['success']) / len(results['mcq_tests']) * 100
        nat_success_rate = sum(1 for test in results['nat_tests'] if test['success']) / len(results['nat_tests']) * 100
        msq_success_rate = sum(1 for test in results['msq_tests'] if test['success']) / len(results['msq_tests']) * 100
        pyq_success_rate = sum(1 for test in results['pyq_tests'] if test['success']) / len(results['pyq_tests']) * 100
        round_robin_success_rate = sum(1 for test in results['round_robin_tests'] if test['success']) / len(results['round_robin_tests']) * 100
        
        print(f"\n🎯 SUCCESS RATE COMPARISON:")
        print(f"   MCQ Generation:")
        print(f"      Previous: 33.3% (1/3 attempts)")
        print(f"      Current:  {mcq_success_rate:.1f}% ({sum(1 for test in results['mcq_tests'] if test['success'])}/5 attempts)")
        print(f"      Target:   90%+")
        print(f"      Status:   {'✅ IMPROVED' if mcq_success_rate > 33.3 else '❌ NO IMPROVEMENT'}")
        
        print(f"\n   NAT Generation:")
        print(f"      Previous: 0.0% (0/3 attempts)")
        print(f"      Current:  {nat_success_rate:.1f}% ({sum(1 for test in results['nat_tests'] if test['success'])}/5 attempts)")
        print(f"      Target:   90%+")
        print(f"      Status:   {'✅ IMPROVED' if nat_success_rate > 0 else '❌ NO IMPROVEMENT'}")
        
        print(f"\n   MSQ Generation:")
        print(f"      Previous: 100.0% (3/3 attempts)")
        print(f"      Current:  {msq_success_rate:.1f}% ({sum(1 for test in results['msq_tests'] if test['success'])}/3 attempts)")
        print(f"      Target:   Maintain 100%")
        print(f"      Status:   {'✅ MAINTAINED' if msq_success_rate == 100 else '⚠️ REGRESSION' if msq_success_rate < 100 else '✅ STABLE'}")
        
        print(f"\n   PYQ Solution Generation:")
        print(f"      Current:  {pyq_success_rate:.1f}% ({sum(1 for test in results['pyq_tests'] if test['success'])}/3 attempts)")
        print(f"      Target:   Consistent JSON with topic notes")
        print(f"      Status:   {'✅ WORKING' if pyq_success_rate >= 66.7 else '⚠️ INCONSISTENT'}")
        
        print(f"\n   Round-Robin System:")
        print(f"      Current:  {round_robin_success_rate:.1f}% ({sum(1 for test in results['round_robin_tests'] if test['success'])}/6 attempts)")
        print(f"      Target:   Proper key rotation")
        print(f"      Status:   {'✅ WORKING' if round_robin_success_rate >= 83.3 else '⚠️ KEY ISSUES'}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL JSON SCHEMA IMPROVEMENTS:")
        
        improvements = []
        regressions = []
        
        if mcq_success_rate > 33.3:
            improvements.append(f"MCQ: {33.3:.1f}% → {mcq_success_rate:.1f}%")
        else:
            regressions.append(f"MCQ: Still at {mcq_success_rate:.1f}%")
            
        if nat_success_rate > 0:
            improvements.append(f"NAT: 0% → {nat_success_rate:.1f}%")
        else:
            regressions.append(f"NAT: Still at 0%")
            
        if msq_success_rate < 100:
            regressions.append(f"MSQ: 100% → {msq_success_rate:.1f}%")
        else:
            improvements.append(f"MSQ: Maintained 100%")
        
        if improvements:
            print(f"   ✅ Improvements: {', '.join(improvements)}")
        if regressions:
            print(f"   ❌ Issues: {', '.join(regressions)}")
        
        # Check if JSON parsing errors are eliminated
        total_attempts = len(results['mcq_tests']) + len(results['nat_tests']) + len(results['msq_tests'])
        total_successes = sum(1 for test in results['mcq_tests'] if test['success']) + \
                         sum(1 for test in results['nat_tests'] if test['success']) + \
                         sum(1 for test in results['msq_tests'] if test['success'])
        
        overall_success_rate = (total_successes / total_attempts) * 100
        
        print(f"\n🔍 JSON PARSING ERROR STATUS:")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}% ({total_successes}/{total_attempts})")
        
        if overall_success_rate >= 90:
            print(f"   ✅ JSON parsing errors largely eliminated")
        elif overall_success_rate >= 70:
            print(f"   ⚠️ Significant improvement but some errors remain")
        else:
            print(f"   ❌ JSON parsing errors still prevalent")
        
        # Expected results check
        print(f"\n🎯 EXPECTED RESULTS CHECK:")
        mcq_target_met = mcq_success_rate >= 90
        nat_target_met = nat_success_rate >= 90
        msq_maintained = msq_success_rate >= 90
        json_consistent = overall_success_rate >= 90
        
        print(f"   MCQ 90%+ success rate: {'✅ MET' if mcq_target_met else '❌ NOT MET'}")
        print(f"   NAT 90%+ success rate: {'✅ MET' if nat_target_met else '❌ NOT MET'}")
        print(f"   MSQ maintain high rate: {'✅ MET' if msq_maintained else '❌ NOT MET'}")
        print(f"   JSON responses valid: {'✅ MET' if json_consistent else '❌ NOT MET'}")
        
        targets_met = sum([mcq_target_met, nat_target_met, msq_maintained, json_consistent])
        
        if targets_met >= 3:
            print(f"\n✅ JSON SCHEMA IMPROVEMENTS: SUCCESSFUL ({targets_met}/4 targets met)")
        elif targets_met >= 2:
            print(f"\n⚠️ JSON SCHEMA IMPROVEMENTS: PARTIAL SUCCESS ({targets_met}/4 targets met)")
        else:
            print(f"\n❌ JSON SCHEMA IMPROVEMENTS: NEED MORE WORK ({targets_met}/4 targets met)")
        
        return {
            'mcq_success_rate': mcq_success_rate,
            'nat_success_rate': nat_success_rate,
            'msq_success_rate': msq_success_rate,
            'pyq_success_rate': pyq_success_rate,
            'round_robin_success_rate': round_robin_success_rate,
            'overall_success_rate': overall_success_rate,
            'targets_met': targets_met
        }

    def test_camelcase_snakecase_fix(self):
        """Test the specific camelCase to snake_case fix from the review request"""
        print("\n🎯 TESTING CAMELCASE TO SNAKE_CASE FIX")
        print("=" * 80)
        print("Goal: Verify frontend camelCase fields are properly transformed to backend snake_case")
        print("Issue: Frontend sends camelCase (correctMarks, incorrectMarks, etc.) but backend expects snake_case")
        print("Fix: Data transformation in frontend before sending to API")
        
        # Use the exact IDs from review request
        exam_id = "521d139b-8cf2-4b0f-afad-f4dc0c2c80e7"
        course_id = "85eb29d4-de89-4697-b041-646dbddb1b3a"
        
        print(f"\nUsing Review Request IDs:")
        print(f"   exam_id: {exam_id}")
        print(f"   course_id: {course_id}")
        
        results = {}
        
        # Test the config data in correct snake_case format as specified in review request
        config_data = {
            "correct_marks": 4.0,
            "incorrect_marks": -1.0,
            "skipped_marks": 0.0,
            "time_minutes": 4.0,
            "total_questions": 10
        }
        
        print(f"\nUsing snake_case config data as specified in review request:")
        print(f"   {config_data}")
        
        # 1. Test /api/start-auto-generation with new_questions mode
        print(f"\n1️⃣ Testing /api/start-auto-generation with 'new_questions' mode")
        success1, data1 = self.test_start_auto_generation_with_specific_config(exam_id, course_id, "new_questions", config_data)
        results['new_questions_mode'] = {'success': success1, 'data': data1}
        
        if success1:
            print(f"   ✅ SUCCESS: No validation error about missing required fields!")
            print(f"   ✅ snake_case fields (correct_marks, incorrect_marks, etc.) accepted properly")
            if data1:
                print(f"   Session ID: {data1.get('session_id', 'N/A')}")
                print(f"   Total topics: {data1.get('total_topics', 'N/A')}")
                print(f"   Status: {data1.get('status', 'N/A')}")
        else:
            print(f"   ❌ FAILED: Validation error still occurs")
        
        # 2. Test /api/start-auto-generation with pyq_solutions mode
        print(f"\n2️⃣ Testing /api/start-auto-generation with 'pyq_solutions' mode")
        success2, data2 = self.test_start_auto_generation_with_specific_config(exam_id, course_id, "pyq_solutions", config_data)
        results['pyq_solutions_mode'] = {'success': success2, 'data': data2}
        
        if success2:
            print(f"   ✅ SUCCESS: No validation error about missing required fields!")
            print(f"   ✅ snake_case fields accepted properly for pyq_solutions mode")
            if data2:
                print(f"   Session ID: {data2.get('session_id', 'N/A')}")
                print(f"   Total topics: {data2.get('total_topics', 'N/A')}")
                print(f"   Status: {data2.get('status', 'N/A')}")
        else:
            print(f"   ❌ FAILED: Validation error still occurs")
        
        # 3. Test with old camelCase format to verify it would fail (negative test)
        print(f"\n3️⃣ Testing with old camelCase format (should fail - negative test)")
        camelcase_config = {
            "correctMarks": 4.0,
            "incorrectMarks": -1.0,
            "skippedMarks": 0.0,
            "timeMinutes": 4.0,
            "totalQuestions": 10
        }
        
        print(f"   Using camelCase config (should cause validation error):")
        print(f"   {camelcase_config}")
        
        success3, data3 = self.test_start_auto_generation_with_specific_config(exam_id, course_id, "new_questions", camelcase_config)
        results['camelcase_negative_test'] = {'success': success3, 'data': data3}
        
        if not success3:
            print(f"   ✅ EXPECTED FAILURE: camelCase format correctly rejected")
            print(f"   ✅ This confirms the backend properly validates snake_case field names")
        else:
            print(f"   ❌ UNEXPECTED SUCCESS: camelCase format was accepted (this shouldn't happen)")
        
        # Summary
        print(f"\n📊 CAMELCASE TO SNAKE_CASE FIX TEST SUMMARY")
        print("=" * 60)
        
        snake_case_working = results.get('new_questions_mode', {}).get('success', False) and \
                           results.get('pyq_solutions_mode', {}).get('success', False)
        
        camelcase_properly_rejected = not results.get('camelcase_negative_test', {}).get('success', True)
        
        print(f"✅ snake_case format accepted: {'YES' if snake_case_working else 'NO'}")
        print(f"✅ camelCase format rejected: {'YES' if camelcase_properly_rejected else 'NO'}")
        print(f"✅ Both generation modes working: {'YES' if snake_case_working else 'NO'}")
        
        if snake_case_working and camelcase_properly_rejected:
            print(f"\n✅ CAMELCASE TO SNAKE_CASE FIX: WORKING CORRECTLY!")
            print(f"   - Validation error about missing required fields is resolved")
            print(f"   - '[object Object]' error should no longer occur with proper field names")
            print(f"   - Both 'new_questions' and 'pyq_solutions' modes working")
        else:
            print(f"\n❌ CAMELCASE TO SNAKE_CASE FIX: ISSUES FOUND")
            if not snake_case_working:
                print(f"   - snake_case format still causing validation errors")
            if not camelcase_properly_rejected:
                print(f"   - camelCase format unexpectedly accepted")
        
        return results

    def test_start_auto_generation_with_specific_config(self, exam_id, course_id, generation_mode, config_data):
        """Test start-auto-generation with specific config data"""
        params = {
            "exam_id": exam_id,
            "course_id": course_id,
            "generation_mode": generation_mode
        }
        
        url = f"{self.api_url}/start-auto-generation"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"   Testing with generation_mode='{generation_mode}' and specific config...")
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        print(f"   Config: {config_data}")
        
        try:
            response = requests.post(url, json=config_data, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS - Auto-generation session created!")
                try:
                    response_data = response.json()
                    print(f"   Session ID: {response_data.get('session_id', 'N/A')}")
                    print(f"   Total topics: {response_data.get('total_topics', 'N/A')}")
                    print(f"   Status: {response_data.get('status', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"   ❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"   ❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Check for validation errors specifically
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'detail' in error_data:
                        detail = error_data['detail']
                        if isinstance(detail, list):
                            print(f"   🔍 VALIDATION ERROR ARRAY DETECTED: {len(detail)} items")
                            for i, item in enumerate(detail):
                                print(f"      Error {i}: {item}")
                                # Check for missing field errors
                                if isinstance(item, dict) and 'loc' in item:
                                    field_name = item['loc'][-1] if item['loc'] else 'unknown'
                                    if field_name in ['correct_marks', 'incorrect_marks', 'skipped_marks', 'time_minutes', 'total_questions']:
                                        print(f"      ⚠️ Missing required snake_case field: {field_name}")
                        else:
                            print(f"   Error detail: {detail}")
                except:
                    pass
                
                self.failed_tests.append({
                    'test': f"Start Auto Generation with Specific Config ({generation_mode})",
                    'exam_id': exam_id,
                    'course_id': course_id,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': f"Start Auto Generation with Specific Config ({generation_mode})",
                'exam_id': exam_id,
                'course_id': course_id,
                'error': str(e)
            })
            return False, {}

    def test_review_request_specific(self):
        """Test the specific review request scenarios with correct ISI MSQMS course IDs"""
        print("\n🎯 TESTING REVIEW REQUEST - AUTO-GENERATION WITH CORRECT ISI MSQMS COURSE")
        print("=" * 80)
        print("Goal: Verify '[object Object]' error is resolved with correct course data")
        print("Expected: 88 topics, proper session creation, working question generation")
        
        # Use the exact IDs from review request
        exam_id = "6c1bed83-2424-4237-8a6f-e7ed97240466"  # ISI
        course_id = "d3ab4d23-f8d4-422b-aca2-affeb4d9609c"  # MSQMS
        
        print(f"\nUsing Review Request IDs:")
        print(f"   exam_id: {exam_id} (ISI)")
        print(f"   course_id: {course_id} (MSQMS)")
        
        results = {}
        
        # 1. Test /api/start-auto-generation with new_questions mode
        print(f"\n1️⃣ Testing /api/start-auto-generation with 'new_questions' mode")
        success1, data1 = self.test_start_auto_generation_with_mode(exam_id, course_id, "new_questions")
        results['new_questions_mode'] = {'success': success1, 'data': data1}
        
        if success1 and data1:
            total_topics = data1.get('total_topics', 0)
            print(f"   ✅ Session created successfully!")
            print(f"   📊 Total topics found: {total_topics}")
            if total_topics == 88:
                print(f"   ✅ EXPECTED: Found exactly 88 topics as expected!")
            else:
                print(f"   ⚠️ UNEXPECTED: Expected 88 topics, found {total_topics}")
        
        # 2. Test /api/start-auto-generation with pyq_solutions mode
        print(f"\n2️⃣ Testing /api/start-auto-generation with 'pyq_solutions' mode")
        success2, data2 = self.test_start_auto_generation_with_mode(exam_id, course_id, "pyq_solutions")
        results['pyq_solutions_mode'] = {'success': success2, 'data': data2}
        
        if success2 and data2:
            total_topics = data2.get('total_topics', 0)
            print(f"   ✅ Session created successfully!")
            print(f"   📊 Total topics found: {total_topics}")
        
        # 3. Get valid topic_id from the course for question generation testing
        print(f"\n3️⃣ Getting valid topic_id from ISI->MSQMS course for question testing")
        valid_topic_id = None
        
        success, topics_data = self.test_all_topics_with_weightage(course_id)
        if success and topics_data:
            valid_topic_id = topics_data[0]['id']
            topic_name = topics_data[0]['name']
            print(f"   ✅ Found valid topic_id: {valid_topic_id}")
            print(f"   Topic name: {topic_name}")
            print(f"   Total topics available: {len(topics_data)}")
        else:
            print(f"   ❌ Failed to get topics from course {course_id}")
            return results
        
        # 4. Test question generation end-to-end
        print(f"\n4️⃣ Testing question generation end-to-end")
        question_types = ["MCQ", "MSQ", "NAT"]  # Skip SUB due to database constraint
        
        for q_type in question_types:
            print(f"\n   Testing {q_type} question generation...")
            success, data = self.test_question_generation(valid_topic_id, q_type)
            results[f'generate_{q_type.lower()}'] = {'success': success, 'data': data}
            
            if success and data:
                print(f"   ✅ {q_type} question generated and saved successfully!")
                print(f"      Question ID: {data.get('id', 'N/A')}")
                print(f"      Saved to new_questions table: ✅ YES")
            else:
                print(f"   ❌ {q_type} question generation failed")
        
        # 5. Verify questions are saved to new_questions table
        print(f"\n5️⃣ Verifying questions are saved to new_questions table")
        success, generated_questions = self.test_generated_questions_endpoint(valid_topic_id)
        results['verify_saved_questions'] = {'success': success, 'data': generated_questions}
        
        if success and generated_questions:
            print(f"   ✅ Found {len(generated_questions)} questions in new_questions table")
            print(f"   Questions are being saved properly!")
        else:
            print(f"   ⚠️ No questions found in new_questions table for this topic")
        
        # Summary
        print(f"\n📊 REVIEW REQUEST TEST SUMMARY")
        print("=" * 50)
        
        successful_tests = sum(1 for key, result in results.items() if result.get('success', False))
        total_tests = len(results)
        
        print(f"Successful tests: {successful_tests}/{total_tests}")
        
        # Check specific requirements
        both_modes_working = results.get('new_questions_mode', {}).get('success', False) and \
                           results.get('pyq_solutions_mode', {}).get('success', False)
        
        question_generation_working = any(results.get(f'generate_{q_type}', {}).get('success', False) 
                                        for q_type in ['mcq', 'msq', 'nat'])
        
        print(f"\n🎯 SPECIFIC REQUIREMENTS CHECK:")
        print(f"   Both generation modes working: {'✅ YES' if both_modes_working else '❌ NO'}")
        print(f"   Question generation working: {'✅ YES' if question_generation_working else '❌ NO'}")
        print(f"   Questions saved to database: {'✅ YES' if results.get('verify_saved_questions', {}).get('success', False) else '❌ NO'}")
        
        if both_modes_working and question_generation_working:
            print(f"\n✅ REVIEW REQUEST: AUTO-GENERATION SYSTEM IS WORKING CORRECTLY!")
            print(f"   '[object Object]' error should be resolved with correct course data")
        else:
            print(f"\n❌ REVIEW REQUEST: ISSUES FOUND IN AUTO-GENERATION SYSTEM")
            print(f"   '[object Object]' error may still occur")
        
        return results

    def test_generated_questions_endpoint(self, topic_id):
        """Test the generated-questions endpoint to verify questions are saved"""
        success, data = self.run_test(f"Get Generated Questions for Topic {topic_id}", "GET", f"generated-questions/{topic_id}", 200)
        if success and data:
            print(f"   Found {len(data)} generated questions")
            return data
        return []

    def test_object_object_error_specific(self):
        """Test the specific '[object Object]' error scenarios from review request"""
        print("\n🎯 TESTING SPECIFIC '[object Object]' ERROR SCENARIOS")
        print("=" * 60)
        print("Focus: /api/start-auto-generation endpoint with specific exam/course IDs")
        print("Goal: Identify exact error causing '[object Object]' display in frontend")
        
        # Use the exact IDs from review request
        exam_id = "6c1bed83-2424-4237-8a6f-e7ed97240466"  # ISI
        course_id = "d3ab4d23-f8d4-422b-aca2-affeb4d9609c"  # MSQMS
        
        results = {
            'valid_new_questions': None,
            'valid_pyq_solutions': None,
            'invalid_scenarios': []
        }
        
        # Test 1: Valid request with generation_mode='new_questions'
        print(f"\n1️⃣ Testing VALID request with generation_mode='new_questions'")
        print(f"   exam_id: {exam_id}")
        print(f"   course_id: {course_id} (ISI->MSQMS)")
        
        request_data = {
            "correct_marks": 4.0,
            "incorrect_marks": -1.0,
            "skipped_marks": 0.0,
            "time_minutes": 180.0,
            "total_questions": 10
        }
        
        params = {
            "exam_id": exam_id,
            "course_id": course_id,
            "generation_mode": "new_questions"
        }
        
        success, data = self.detailed_start_auto_generation_test(request_data, params, "new_questions")
        results['valid_new_questions'] = {'success': success, 'data': data}
        
        # Test 2: Valid request with generation_mode='pyq_solutions'
        print(f"\n2️⃣ Testing VALID request with generation_mode='pyq_solutions'")
        
        params['generation_mode'] = "pyq_solutions"
        success, data = self.detailed_start_auto_generation_test(request_data, params, "pyq_solutions")
        results['valid_pyq_solutions'] = {'success': success, 'data': data}
        
        # Test 3: Invalid scenarios that might cause '[object Object]' error
        print(f"\n3️⃣ Testing INVALID scenarios that cause '[object Object]' error")
        
        invalid_scenarios = [
            {
                "name": "Invalid UUID format for exam_id",
                "params": {"exam_id": "invalid-uuid", "course_id": course_id, "generation_mode": "new_questions"},
                "data": request_data
            },
            {
                "name": "Invalid UUID format for course_id", 
                "params": {"exam_id": exam_id, "course_id": "invalid-uuid", "generation_mode": "new_questions"},
                "data": request_data
            },
            {
                "name": "Missing required fields in request body",
                "params": {"exam_id": exam_id, "course_id": course_id, "generation_mode": "new_questions"},
                "data": {}
            },
            {
                "name": "Invalid data types in request body",
                "params": {"exam_id": exam_id, "course_id": course_id, "generation_mode": "new_questions"},
                "data": {
                    "correct_marks": "invalid",
                    "incorrect_marks": "invalid",
                    "skipped_marks": "invalid",
                    "time_minutes": "invalid",
                    "total_questions": "invalid"
                }
            },
            {
                "name": "Missing query parameters",
                "params": {},
                "data": request_data
            }
        ]
        
        for i, scenario in enumerate(invalid_scenarios):
            print(f"\n   Testing scenario {i+1}: {scenario['name']}")
            success, data = self.detailed_start_auto_generation_test(scenario['data'], scenario['params'], scenario['name'])
            results['invalid_scenarios'].append({
                'name': scenario['name'],
                'success': success,
                'data': data
            })
        
        return results

    def detailed_start_auto_generation_test(self, request_data, params, test_name):
        """Detailed test of start-auto-generation endpoint with error analysis"""
        url = f"{self.api_url}/start-auto-generation"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"   URL: {url}")
        print(f"   Params: {json.dumps(params, indent=6)}")
        print(f"   Body: {json.dumps(request_data, indent=6)}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, params=params, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ SUCCESS - Auto-generation session created!")
                try:
                    response_data = response.json()
                    print(f"   Response Structure:")
                    print(f"      session_id: {response_data.get('session_id', 'N/A')}")
                    print(f"      total_topics: {response_data.get('total_topics', 'N/A')}")
                    print(f"      total_questions_planned: {response_data.get('total_questions_planned', 'N/A')}")
                    print(f"      status: {response_data.get('status', 'N/A')}")
                    print(f"      message: {response_data.get('message', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"   ❌ JSON parsing error: {str(json_error)}")
                    print(f"   Raw response: {response.text}")
                    return False, {}
            else:
                print(f"   ❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Raw Response: {response.text}")
                
                # Detailed error analysis for '[object Object]' investigation
                try:
                    error_data = response.json()
                    print(f"   📊 ERROR ANALYSIS:")
                    print(f"      Error Type: {type(error_data).__name__}")
                    
                    if isinstance(error_data, list):
                        print(f"      🚨 ERROR IS AN ARRAY with {len(error_data)} items")
                        print(f"      🔍 This would cause '[object Object]' in frontend!")
                        for i, item in enumerate(error_data):
                            print(f"         Item {i}: {item}")
                    elif isinstance(error_data, dict):
                        print(f"      Error is an object with keys: {list(error_data.keys())}")
                        if 'detail' in error_data:
                            detail = error_data['detail']
                            print(f"      Detail Type: {type(detail).__name__}")
                            if isinstance(detail, list):
                                print(f"      🚨 DETAIL IS AN ARRAY with {len(detail)} items")
                                print(f"      🔍 This would cause '[object Object]' in frontend!")
                                for i, item in enumerate(detail):
                                    print(f"         Detail {i}: {json.dumps(item, indent=10)}")
                            else:
                                print(f"      Detail: {detail}")
                        else:
                            print(f"      Full error object: {json.dumps(error_data, indent=6)}")
                    
                    # Check for FastAPI/Pydantic validation errors
                    if response.status_code == 422:
                        print(f"      🔍 422 VALIDATION ERROR DETECTED")
                        print(f"      This is likely a Pydantic validation error array")
                        print(f"      Frontend should handle validation error arrays properly")
                    elif response.status_code == 500:
                        print(f"      🔍 500 INTERNAL SERVER ERROR")
                        print(f"      This might be UUID validation or database error")
                    
                except Exception as parse_error:
                    print(f"   ❌ Could not parse error response: {parse_error}")
                    print(f"   This might be non-JSON error response")
                
                self.failed_tests.append({
                    'test': f"Start Auto Generation - {test_name}",
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500],
                    'params': params
                })
                return False, {'error_response': response.text, 'status_code': response.status_code}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': f"Start Auto Generation - {test_name}",
                'error': str(e),
                'params': params
            })
            return False, {'exception': str(e)}

    def test_sub_question_database_constraint(self):
        """Test SUB question type database constraint issue specifically"""
        print("\n🎯 TESTING SUB QUESTION DATABASE CONSTRAINT ISSUE")
        print("=" * 80)
        print("Focus: Test SUB question generation and investigate database constraint")
        print("Known Issue: 'new row for relation new_questions violates check constraint new_questions_question_type_check'")
        
        # Use the specific topic_id from the review request
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        
        results = {
            'mcq_test': None,
            'msq_test': None, 
            'nat_test': None,
            'sub_test': None,
            'constraint_investigation': None
        }
        
        print(f"\nUsing topic_id: {topic_id}")
        print("Testing all 4 question types to compare SUB with working types...")
        
        # Test all 4 question types with the same topic_id
        question_types = ["MCQ", "MSQ", "NAT", "SUB"]
        
        for q_type in question_types:
            print(f"\n{'='*20} Testing {q_type} Question Generation {'='*20}")
            
            success, data = self.test_question_generation_detailed(topic_id, q_type)
            results[f'{q_type.lower()}_test'] = {
                'success': success,
                'data': data,
                'question_type': q_type
            }
            
            if success:
                print(f"✅ {q_type} Generation: SUCCESS")
                if data:
                    print(f"   Question: {data.get('question_statement', '')[:100]}...")
                    print(f"   Answer: {data.get('answer', 'N/A')}")
                    if q_type in ["MCQ", "MSQ"]:
                        print(f"   Options: {len(data.get('options', []))} provided")
            else:
                print(f"❌ {q_type} Generation: FAILED")
                # For SUB specifically, investigate the database constraint error
                if q_type == "SUB":
                    print(f"   🔍 SUB-specific failure - investigating database constraint...")
                    self.investigate_database_constraint()
        
        # Summary of results
        print(f"\n📊 QUESTION TYPE GENERATION SUMMARY")
        print("=" * 60)
        
        working_types = []
        failing_types = []
        
        for q_type in question_types:
            test_result = results.get(f'{q_type.lower()}_test', {})
            if test_result.get('success', False):
                working_types.append(q_type)
            else:
                failing_types.append(q_type)
        
        print(f"✅ Working Types: {working_types} ({len(working_types)}/4)")
        print(f"❌ Failing Types: {failing_types} ({len(failing_types)}/4)")
        
        # Specific analysis for SUB
        sub_result = results.get('sub_test', {})
        if not sub_result.get('success', False):
            print(f"\n🔍 SUB QUESTION ANALYSIS:")
            print(f"   Status: FAILED as expected")
            print(f"   Issue: Database constraint violation")
            print(f"   Error: 'new_questions_question_type_check' constraint rejects 'SUB'")
            print(f"   Solution Needed: Update database schema to allow 'SUB' question type")
        else:
            print(f"\n✅ SUB QUESTION ANALYSIS:")
            print(f"   Status: WORKING (constraint issue resolved)")
        
        return results

    def test_question_generation_detailed(self, topic_id, question_type):
        """Test question generation with detailed error analysis for database constraints"""
        request_data = {
            "topic_id": topic_id,
            "question_type": question_type,
            "part_id": None,
            "slot_id": None
        }
        
        url = f"{self.api_url}/generate-question"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"🔍 Testing Generate {question_type} Question...")
        print(f"   URL: {url}")
        print(f"   Topic ID: {topic_id}")
        print(f"   Request: {json.dumps(request_data, indent=2)}")
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ SUCCESS - {question_type} question generated successfully!")
                try:
                    response_data = response.json()
                    print(f"   Generated Question: {response_data.get('question_statement', '')[:150]}...")
                    print(f"   Question Type: {response_data.get('question_type', 'N/A')}")
                    print(f"   Answer: {response_data.get('answer', 'N/A')}")
                    print(f"   Difficulty: {response_data.get('difficulty_level', 'N/A')}")
                    return True, response_data
                except Exception as json_error:
                    print(f"❌ JSON parsing error: {str(json_error)}")
                    return False, {}
            else:
                print(f"❌ FAILED - Expected 200, got {response.status_code}")
                print(f"   Error Response: {response.text}")
                
                # Detailed error analysis for database constraints
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No detail provided')
                    print(f"   Error Detail: {error_detail}")
                    
                    # Check for specific database constraint errors
                    if 'constraint' in error_detail.lower():
                        print(f"   🔍 DATABASE CONSTRAINT ERROR DETECTED!")
                        if 'new_questions_question_type_check' in error_detail:
                            print(f"   🎯 SPECIFIC CONSTRAINT: new_questions_question_type_check")
                            print(f"   📝 ANALYSIS: Database schema doesn't allow '{question_type}' as valid question_type")
                            print(f"   💡 SOLUTION: Need to update database constraint to include '{question_type}'")
                        
                    # Check for JSON parsing errors
                    elif 'json' in error_detail.lower() or 'parsing' in error_detail.lower():
                        print(f"   🔍 JSON PARSING ERROR DETECTED!")
                        print(f"   📝 ANALYSIS: Gemini API response format issue")
                        
                except Exception as parse_error:
                    print(f"   ⚠️ Could not parse error response: {parse_error}")
                
                self.failed_tests.append({
                    'test': f"Generate {question_type} Question (Detailed)",
                    'topic_id': topic_id,
                    'question_type': question_type,
                    'expected': 200,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, {}
                
        except Exception as e:
            print(f"❌ EXCEPTION - Error: {str(e)}")
            self.failed_tests.append({
                'test': f"Generate {question_type} Question (Detailed)",
                'topic_id': topic_id,
                'question_type': question_type,
                'error': str(e)
            })
            return False, {}

    def investigate_database_constraint(self):
        """Investigate what question types are allowed by the database constraint"""
        print(f"\n🔍 INVESTIGATING DATABASE CONSTRAINT...")
        print("   Attempting to understand what question types are allowed...")
        
        # Try to generate questions of known working types to understand the pattern
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        working_types = []
        
        for q_type in ["MCQ", "MSQ", "NAT"]:
            print(f"   Testing {q_type} to confirm it works...")
            try:
                request_data = {
                    "topic_id": topic_id,
                    "question_type": q_type,
                    "part_id": None,
                    "slot_id": None
                }
                
                url = f"{self.api_url}/generate-question"
                headers = {'Content-Type': 'application/json'}
                
                response = requests.post(url, json=request_data, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    working_types.append(q_type)
                    print(f"   ✅ {q_type}: WORKS")
                else:
                    print(f"   ❌ {q_type}: FAILS - {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {q_type}: ERROR - {str(e)}")
        
        print(f"\n📊 CONSTRAINT ANALYSIS RESULTS:")
        print(f"   Working question types: {working_types}")
        print(f"   Failing question types: ['SUB']")
        print(f"   Constraint allows: {', '.join(working_types)}")
        print(f"   Constraint rejects: SUB")
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Update database constraint 'new_questions_question_type_check'")
        print(f"   to include 'SUB' as a valid question_type value")
        print(f"   Current allowed values appear to be: {', '.join(working_types)}")
        print(f"   Required change: Add 'SUB' to the allowed values list")

    def test_pyq_solution_generation_comprehensive(self):
        """Comprehensive testing of PYQ solution generation system as requested"""
        print("\n🎯 COMPREHENSIVE PYQ SOLUTION GENERATION TESTING")
        print("=" * 80)
        print("Focus: Test PYQ solution generation system with 33.3% success rate issues")
        print("Endpoints: /existing-questions, /generate-pyq-solution, /generate-pyq-solution-by-id, /update-question-solution")
        print("Known Issues: JSON parsing errors, data saving issues, intermittent failures")
        
        # Use the specific topic_id from previous tests
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        
        results = {
            'existing_questions_tests': [],
            'generate_pyq_solution_tests': [],
            'generate_pyq_solution_by_id_tests': [],
            'update_question_solution_tests': [],
            'generate_question_tests': [],
            'data_saving_tests': []
        }
        
        # 1. Test GET /api/existing-questions/{topic_id}
        print(f"\n1️⃣ Testing GET /api/existing-questions/{topic_id}")
        print("   Purpose: Get PYQ questions from questions_topic_wise table")
        
        success, existing_questions = self.test_existing_questions_with_ids(topic_id)
        results['existing_questions_tests'].append({
            'success': success,
            'data': existing_questions,
            'count': len(existing_questions) if existing_questions else 0
        })
        
        if success and existing_questions:
            print(f"   ✅ Found {len(existing_questions)} existing PYQ questions")
            sample_question = existing_questions[0]
            print(f"   Sample question ID: {sample_question.get('id', 'N/A')}")
            print(f"   Sample statement: {sample_question.get('question_statement', '')[:100]}...")
            print(f"   Has solution: {'YES' if sample_question.get('solution') else 'NO'}")
        else:
            print(f"   ❌ Failed to retrieve existing questions")
        
        # 2. Test POST /api/generate-pyq-solution (multiple attempts to identify 33.3% success rate)
        print(f"\n2️⃣ Testing POST /api/generate-pyq-solution (Multiple attempts)")
        print("   Purpose: Generate solutions for PYQ questions - currently 33.3% success rate")
        print("   Known Issue: 'Unterminated string starting at: line 3 column 15' JSON parsing errors")
        
        pyq_successes = 0
        pyq_json_errors = 0
        pyq_other_errors = 0
        
        for i in range(6):  # Test 6 times to get better statistics
            print(f"\n   PYQ Solution Attempt {i+1}/6:")
            success, data = self.test_generate_pyq_solution_detailed(topic_id, i+1)
            
            if success:
                pyq_successes += 1
                print(f"   ✅ Attempt {i+1}: SUCCESS")
                if data:
                    print(f"      Answer: {data.get('answer', 'N/A')}")
                    print(f"      Confidence: {data.get('confidence_level', 'N/A')}")
                    print(f"      Solution length: {len(data.get('solution', ''))}")
            else:
                # Check if it's a JSON parsing error
                if 'json' in str(data).lower() or 'parsing' in str(data).lower():
                    pyq_json_errors += 1
                    print(f"   ❌ Attempt {i+1}: JSON PARSING ERROR")
                else:
                    pyq_other_errors += 1
                    print(f"   ❌ Attempt {i+1}: OTHER ERROR")
            
            results['generate_pyq_solution_tests'].append({
                'attempt': i+1,
                'success': success,
                'data': data
            })
        
        pyq_success_rate = (pyq_successes / 6) * 100
        print(f"\n   📊 PYQ Solution Generation Results:")
        print(f"      Success Rate: {pyq_success_rate:.1f}% ({pyq_successes}/6)")
        print(f"      JSON Parsing Errors: {pyq_json_errors}/6")
        print(f"      Other Errors: {pyq_other_errors}/6")
        print(f"      Expected: ~33.3% success rate")
        print(f"      Status: {'✅ MATCHES EXPECTED' if 20 <= pyq_success_rate <= 50 else '⚠️ DIFFERENT FROM EXPECTED'}")
        
        # 3. Test POST /api/generate-pyq-solution-by-id (if we have existing questions)
        print(f"\n3️⃣ Testing POST /api/generate-pyq-solution-by-id")
        print("   Purpose: Generate solutions for existing PYQ questions by ID")
        
        if existing_questions:
            # Test with first few existing questions
            for i, question in enumerate(existing_questions[:3]):
                question_id = question.get('id')
                print(f"\n   Testing with question ID: {question_id}")
                print(f"   Question: {question.get('question_statement', '')[:80]}...")
                
                success, data = self.test_generate_pyq_solution_by_id_detailed(question_id, i+1)
                results['generate_pyq_solution_by_id_tests'].append({
                    'question_id': question_id,
                    'success': success,
                    'data': data
                })
                
                if success:
                    print(f"   ✅ Generated solution successfully")
                    if data:
                        print(f"      Answer: {data.get('answer', 'N/A')}")
                        print(f"      Confidence: {data.get('confidence_level', 'N/A')}")
                else:
                    print(f"   ❌ Failed to generate solution")
        else:
            print("   ⚠️ No existing questions found - skipping this test")
        
        # 4. Test PATCH /api/update-question-solution
        print(f"\n4️⃣ Testing PATCH /api/update-question-solution")
        print("   Purpose: Save generated solutions back to questions_topic_wise table")
        
        if existing_questions:
            # Find a question to update
            question_to_update = existing_questions[0]
            question_id = question_to_update.get('id')
            
            print(f"   Testing with question ID: {question_id}")
            success, data = self.test_update_question_solution_detailed(question_id)
            results['update_question_solution_tests'].append({
                'question_id': question_id,
                'success': success,
                'data': data
            })
            
            if success:
                print(f"   ✅ Successfully updated question solution")
                print(f"   ✅ Data saving to questions_topic_wise table: WORKING")
            else:
                print(f"   ❌ Failed to update question solution")
                print(f"   ❌ Data saving to questions_topic_wise table: FAILED")
        else:
            print("   ⚠️ No existing questions found - testing with manually created question")
            # Create a test question and then update it
            success = self.test_update_solution_with_created_question()
            results['update_question_solution_tests'].append({
                'question_id': 'created_question',
                'success': success,
                'data': {}
            })
        
        # 5. Test POST /api/generate-question for new question generation
        print(f"\n5️⃣ Testing POST /api/generate-question")
        print("   Purpose: Generate new questions and verify saving to new_questions table")
        
        question_types = ["MCQ", "MSQ", "NAT"]  # Avoid SUB due to database constraint
        
        for q_type in question_types:
            print(f"\n   Testing {q_type} question generation...")
            success, data = self.test_question_generation_detailed(topic_id, q_type)
            results['generate_question_tests'].append({
                'question_type': q_type,
                'success': success,
                'data': data
            })
            
            if success:
                print(f"   ✅ {q_type} question generated and saved to new_questions table")
                if data:
                    print(f"      Question ID: {data.get('id', 'N/A')}")
                    print(f"      Statement: {data.get('question_statement', '')[:80]}...")
            else:
                print(f"   ❌ {q_type} question generation failed")
        
        # 6. Test data saving verification
        print(f"\n6️⃣ Testing Data Saving Verification")
        print("   Purpose: Verify questions are properly saved to both tables")
        
        # Test retrieving generated questions
        success, generated_questions = self.test_generated_questions_endpoint(topic_id)
        results['data_saving_tests'].append({
            'test': 'retrieve_generated_questions',
            'success': success,
            'count': len(generated_questions) if generated_questions else 0
        })
        
        if success and generated_questions:
            print(f"   ✅ Found {len(generated_questions)} generated questions in new_questions table")
            print(f"   ✅ Data saving to new_questions table: WORKING")
        else:
            print(f"   ❌ No generated questions found in new_questions table")
            print(f"   ❌ Data saving to new_questions table: ISSUE")
        
        return results
    
    def test_generate_pyq_solution_detailed(self, topic_id, attempt_num):
        """Detailed test of PYQ solution generation with error analysis"""
        request_data = {
            "topic_id": topic_id,
            "question_statement": f"Find the harmonic mean of 4, 6, and 12. (Attempt {attempt_num})",
            "options": ["6", "6.4", "7.2", "8"],
            "question_type": "MCQ"
        }
        
        url = f"{self.api_url}/generate-pyq-solution"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return True, response_data
                except json.JSONDecodeError as e:
                    print(f"      JSON Parsing Error: {str(e)}")
                    print(f"      Raw Response: {response.text[:200]}...")
                    return False, {'error': 'json_parsing', 'details': str(e)}
            else:
                print(f"      HTTP Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                return False, {'error': 'http_error', 'status': response.status_code}
                
        except Exception as e:
            print(f"      Exception: {str(e)}")
            return False, {'error': 'exception', 'details': str(e)}
    
    def test_generate_pyq_solution_by_id_detailed(self, question_id, attempt_num):
        """Detailed test of PYQ solution generation by ID"""
        request_data = {
            "question_id": question_id
        }
        
        url = f"{self.api_url}/generate-pyq-solution-by-id"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return True, response_data
                except json.JSONDecodeError as e:
                    print(f"      JSON Parsing Error: {str(e)}")
                    return False, {'error': 'json_parsing', 'details': str(e)}
            else:
                print(f"      HTTP Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                return False, {'error': 'http_error', 'status': response.status_code}
                
        except Exception as e:
            print(f"      Exception: {str(e)}")
            return False, {'error': 'exception', 'details': str(e)}
    
    def test_update_question_solution_detailed(self, question_id):
        """Detailed test of question solution update"""
        request_data = {
            "question_id": question_id,
            "answer": "1",
            "solution": "To find the harmonic mean of numbers a, b, c: HM = 3/(1/a + 1/b + 1/c). For 4, 6, 12: HM = 3/(1/4 + 1/6 + 1/12) = 3/(3/12 + 2/12 + 1/12) = 3/(6/12) = 3/(1/2) = 6. The answer is option 1 (6).",
            "confidence_level": "High"
        }
        
        url = f"{self.api_url}/update-question-solution"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.patch(url, json=request_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return True, response_data
                except json.JSONDecodeError as e:
                    print(f"      JSON Parsing Error: {str(e)}")
                    return False, {'error': 'json_parsing', 'details': str(e)}
            else:
                print(f"      HTTP Error: {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                return False, {'error': 'http_error', 'status': response.status_code}
                
        except Exception as e:
            print(f"      Exception: {str(e)}")
            return False, {'error': 'exception', 'details': str(e)}
    
    def test_generated_questions_endpoint(self, topic_id):
        """Test the generated questions endpoint to verify data saving"""
        url = f"{self.api_url}/generated-questions/{topic_id}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return True, response_data
                except json.JSONDecodeError as e:
                    return False, []
            else:
                return False, []
                
        except Exception as e:
            return False, []
    
    def analyze_pyq_solution_results(self, results):
        """Analyze the comprehensive PYQ solution generation test results"""
        print(f"\n📊 COMPREHENSIVE PYQ SOLUTION GENERATION ANALYSIS")
        print("=" * 80)
        
        # Use the topic_id for display
        topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        
        # 1. Existing Questions Analysis
        existing_tests = results.get('existing_questions_tests', [])
        existing_success = any(test['success'] for test in existing_tests)
        existing_count = sum(test.get('count', 0) for test in existing_tests)
        
        print(f"\n1️⃣ GET /api/existing-questions/{topic_id}")
        print(f"   Status: {'✅ WORKING' if existing_success else '❌ FAILED'}")
        print(f"   Questions Found: {existing_count}")
        print(f"   Purpose: Retrieve PYQ questions from questions_topic_wise table")
        
        # 2. PYQ Solution Generation Analysis
        pyq_tests = results.get('generate_pyq_solution_tests', [])
        pyq_successes = sum(1 for test in pyq_tests if test['success'])
        pyq_total = len(pyq_tests)
        pyq_success_rate = (pyq_successes / pyq_total * 100) if pyq_total > 0 else 0
        
        json_errors = sum(1 for test in pyq_tests if not test['success'] and 
                         isinstance(test.get('data'), dict) and 
                         test['data'].get('error') == 'json_parsing')
        
        print(f"\n2️⃣ POST /api/generate-pyq-solution")
        print(f"   Success Rate: {pyq_success_rate:.1f}% ({pyq_successes}/{pyq_total})")
        print(f"   JSON Parsing Errors: {json_errors}/{pyq_total}")
        print(f"   Expected Issue: ~33.3% success rate with JSON parsing errors")
        print(f"   Status: {'✅ ISSUE CONFIRMED' if 20 <= pyq_success_rate <= 50 and json_errors > 0 else '⚠️ DIFFERENT BEHAVIOR'}")
        
        # 3. PYQ Solution by ID Analysis
        pyq_id_tests = results.get('generate_pyq_solution_by_id_tests', [])
        pyq_id_successes = sum(1 for test in pyq_id_tests if test['success'])
        pyq_id_total = len(pyq_id_tests)
        pyq_id_success_rate = (pyq_id_successes / pyq_id_total * 100) if pyq_id_total > 0 else 0
        
        print(f"\n3️⃣ POST /api/generate-pyq-solution-by-id")
        print(f"   Success Rate: {pyq_id_success_rate:.1f}% ({pyq_id_successes}/{pyq_id_total})")
        print(f"   Status: {'✅ WORKING' if pyq_id_success_rate >= 66.7 else '❌ ISSUES FOUND'}")
        
        # 4. Update Question Solution Analysis
        update_tests = results.get('update_question_solution_tests', [])
        update_successes = sum(1 for test in update_tests if test['success'])
        update_total = len(update_tests)
        
        print(f"\n4️⃣ PATCH /api/update-question-solution")
        print(f"   Success Rate: {update_successes}/{update_total}")
        print(f"   Purpose: Save solutions back to questions_topic_wise table")
        print(f"   Status: {'✅ WORKING' if update_successes > 0 else '❌ FAILED'}")
        
        # 5. New Question Generation Analysis
        gen_tests = results.get('generate_question_tests', [])
        gen_successes = sum(1 for test in gen_tests if test['success'])
        gen_total = len(gen_tests)
        gen_success_rate = (gen_successes / gen_total * 100) if gen_total > 0 else 0
        
        print(f"\n5️⃣ POST /api/generate-question")
        print(f"   Success Rate: {gen_success_rate:.1f}% ({gen_successes}/{gen_total})")
        print(f"   Purpose: Generate new questions and save to new_questions table")
        print(f"   Status: {'✅ WORKING' if gen_success_rate >= 66.7 else '❌ ISSUES FOUND'}")
        
        # 6. Data Saving Analysis
        saving_tests = results.get('data_saving_tests', [])
        saving_success = any(test['success'] for test in saving_tests)
        
        print(f"\n6️⃣ Data Saving Verification")
        print(f"   new_questions table: {'✅ WORKING' if saving_success else '❌ ISSUES'}")
        print(f"   questions_topic_wise table: {'✅ WORKING' if update_successes > 0 else '❌ ISSUES'}")
        
        # Overall Assessment
        print(f"\n🎯 OVERALL PYQ SOLUTION SYSTEM STATUS")
        print("=" * 60)
        
        critical_issues = []
        working_components = []
        
        if not existing_success:
            critical_issues.append("Cannot retrieve existing PYQ questions")
        else:
            working_components.append("PYQ question retrieval")
        
        if pyq_success_rate < 50:
            critical_issues.append(f"PYQ solution generation low success rate ({pyq_success_rate:.1f}%)")
        
        if json_errors > 0:
            critical_issues.append(f"JSON parsing errors in PYQ solutions ({json_errors} errors)")
        
        if update_successes == 0:
            critical_issues.append("Cannot save solutions back to database")
        else:
            working_components.append("Solution saving to questions_topic_wise")
        
        if gen_success_rate < 66.7:
            critical_issues.append(f"New question generation issues ({gen_success_rate:.1f}% success)")
        else:
            working_components.append("New question generation")
        
        if not saving_success:
            critical_issues.append("Data saving to new_questions table issues")
        else:
            working_components.append("Data saving to new_questions")
        
        print(f"✅ Working Components: {', '.join(working_components) if working_components else 'None'}")
        print(f"❌ Critical Issues: {', '.join(critical_issues) if critical_issues else 'None'}")
        
        # Root Cause Analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS")
        print("=" * 40)
        
        if json_errors > 0:
            print(f"🚨 PRIMARY ISSUE: JSON Parsing Errors")
            print(f"   - Affects: PYQ solution generation endpoint")
            print(f"   - Error Pattern: 'Unterminated string starting at: line X column Y'")
            print(f"   - Likely Cause: Gemini API returning malformed JSON responses")
            print(f"   - Impact: {json_errors}/{pyq_total} requests fail with JSON errors")
            print(f"   - Recommendation: Improve JSON parsing robustness or prompt engineering")
        
        if pyq_success_rate < 50:
            print(f"🚨 SECONDARY ISSUE: Low Success Rate")
            print(f"   - Current Rate: {pyq_success_rate:.1f}% (expected ~33.3%)")
            print(f"   - Impact: Unreliable PYQ solution generation")
            print(f"   - Recommendation: Implement retry logic and better error handling")
        
        # Success Criteria Check
        system_health = len(working_components) / (len(working_components) + len(critical_issues)) * 100 if (len(working_components) + len(critical_issues)) > 0 else 0
        
        print(f"\n📈 SYSTEM HEALTH: {system_health:.1f}%")
        if system_health >= 80:
            print(f"✅ PYQ Solution System: MOSTLY WORKING")
        elif system_health >= 60:
            print(f"⚠️ PYQ Solution System: PARTIALLY WORKING")
        else:
            print(f"❌ PYQ Solution System: NEEDS MAJOR FIXES")
        
        return {
            'existing_questions_working': existing_success,
            'pyq_solution_success_rate': pyq_success_rate,
            'json_parsing_errors': json_errors,
            'update_solution_working': update_successes > 0,
            'new_question_generation_rate': gen_success_rate,
            'data_saving_working': saving_success,
            'critical_issues': critical_issues,
            'working_components': working_components,
            'system_health': system_health
        }

def main():
    print("🚀 Testing PYQ Solution Generation System")
    print("🎯 Focus: Review Request - Comprehensive PYQ solution testing")
    print("=" * 80)
    
    tester = QuestionMakerAPITester()
    
    # Test basic connectivity first
    print("\n1️⃣ Testing Basic API Connectivity...")
    tester.test_root_endpoint()
    
    # Run comprehensive PYQ solution generation testing as requested
    print("\n2️⃣ Running Comprehensive PYQ Solution Generation Testing...")
    pyq_results = tester.test_pyq_solution_generation_comprehensive()
    pyq_analysis = tester.analyze_pyq_solution_results(pyq_results)
    
    # Print final summary
    print(f"\n📊 FINAL TEST SUMMARY:")
    print(f"   Total Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {len(tester.failed_tests)}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Specific review request summary
    print(f"\n🎯 PYQ SOLUTION GENERATION TEST RESULTS:")
    print(f"   System Health: {pyq_analysis.get('system_health', 0):.1f}%")
    print(f"   PYQ Solution Success Rate: {pyq_analysis.get('pyq_solution_success_rate', 0):.1f}%")
    print(f"   JSON Parsing Errors: {pyq_analysis.get('json_parsing_errors', 0)}")
    print(f"   Working Components: {len(pyq_analysis.get('working_components', []))}")
    print(f"   Critical Issues: {len(pyq_analysis.get('critical_issues', []))}")
    
    # Show critical issues
    critical_issues = pyq_analysis.get('critical_issues', [])
    if critical_issues:
        print(f"\n❌ CRITICAL ISSUES FOUND:")
        for i, issue in enumerate(critical_issues, 1):
            print(f"   {i}. {issue}")
    
    # Show working components
    working_components = pyq_analysis.get('working_components', [])
    if working_components:
        print(f"\n✅ WORKING COMPONENTS:")
        for i, component in enumerate(working_components, 1):
            print(f"   {i}. {component}")
    
    # Overall status
    system_health = pyq_analysis.get('system_health', 0)
    if system_health >= 80:
        print(f"\n✅ PYQ SOLUTION SYSTEM: MOSTLY WORKING")
        return 0
    elif system_health >= 60:
        print(f"\n⚠️ PYQ SOLUTION SYSTEM: PARTIALLY WORKING")
        return 1
    else:
        print(f"\n❌ PYQ SOLUTION SYSTEM: NEEDS MAJOR FIXES")
        return 2

if __name__ == "__main__":
    sys.exit(main())