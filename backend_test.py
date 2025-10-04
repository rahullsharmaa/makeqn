import requests
import sys
import json
from datetime import datetime

class QuestionMakerAPITester:
    def __init__(self, base_url="https://quizgen-ai-2.preview.emergentagent.com"):
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
        exam_id = "521d139b-8cf2-4b0f-afad-f4dc0c2c80e7"
        course_id = "85eb29d4-de89-4697-b041-646dbddb1b3a"  # ISI->MSQMS
        
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

    def test_object_object_error_specific(self):
        """Test the specific '[object Object]' error scenarios from review request"""
        print("\n🎯 TESTING SPECIFIC '[object Object]' ERROR SCENARIOS")
        print("=" * 60)
        print("Focus: /api/start-auto-generation endpoint with specific exam/course IDs")
        print("Goal: Identify exact error causing '[object Object]' display in frontend")
        
        # Use the exact IDs from review request
        exam_id = "521d139b-8cf2-4b0f-afad-f4dc0c2c80e7"
        course_id = "85eb29d4-de89-4697-b041-646dbddb1b3a"  # ISI->MSQMS
        
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

def main():
    print("🚀 Testing '[object Object]' Error Investigation")
    print("🎯 Focus: Review Request - Auto-Generation Endpoint Error Analysis")
    print("=" * 60)
    
    tester = QuestionMakerAPITester()
    
    # Test basic connectivity first
    print("\n1️⃣ Testing Basic API Connectivity...")
    tester.test_root_endpoint()
    
    # Run the specific '[object Object]' error investigation
    print("\n2️⃣ Running '[object Object]' Error Investigation...")
    object_error_results = tester.test_object_object_error_specific()
    
    # Print detailed analysis
    print("\n" + "=" * 60)
    print("📊 '[object Object]' ERROR INVESTIGATION RESULTS")
    print("=" * 60)
    
    # Analyze valid scenarios
    print(f"\n✅ VALID SCENARIOS:")
    if object_error_results['valid_new_questions']['success']:
        print(f"   generation_mode='new_questions': ✅ SUCCESS")
        data = object_error_results['valid_new_questions']['data']
        print(f"      Session ID: {data.get('session_id', 'N/A')}")
        print(f"      Total Topics: {data.get('total_topics', 'N/A')}")
        print(f"      Status: {data.get('status', 'N/A')}")
    else:
        print(f"   generation_mode='new_questions': ❌ FAILED")
        
    if object_error_results['valid_pyq_solutions']['success']:
        print(f"   generation_mode='pyq_solutions': ✅ SUCCESS")
        data = object_error_results['valid_pyq_solutions']['data']
        print(f"      Session ID: {data.get('session_id', 'N/A')}")
        print(f"      Total Topics: {data.get('total_topics', 'N/A')}")
        print(f"      Status: {data.get('status', 'N/A')}")
    else:
        print(f"   generation_mode='pyq_solutions': ❌ FAILED")
    
    # Analyze invalid scenarios that cause '[object Object]'
    print(f"\n❌ INVALID SCENARIOS (causing '[object Object]'):")
    object_object_causes = []
    
    for scenario in object_error_results['invalid_scenarios']:
        print(f"   {scenario['name']}: {'✅ HANDLED' if scenario['success'] else '❌ CAUSES ERROR'}")
        if not scenario['success'] and 'error_response' in scenario['data']:
            # Check if this would cause '[object Object]' in frontend
            try:
                import json
                error_data = json.loads(scenario['data']['error_response'])
                if isinstance(error_data, list) or (isinstance(error_data, dict) and isinstance(error_data.get('detail'), list)):
                    object_object_causes.append(scenario['name'])
                    print(f"      🚨 This would display '[object Object]' in frontend!")
            except:
                pass
    
    # Summary and recommendations
    print(f"\n🎯 ROOT CAUSE ANALYSIS:")
    if object_object_causes:
        print(f"   '[object Object]' is caused by: {len(object_object_causes)} scenarios")
        for cause in object_object_causes:
            print(f"      - {cause}")
        print(f"\n   💡 SOLUTION: Frontend needs to handle validation error arrays properly")
        print(f"      When FastAPI returns validation errors, they come as arrays in 'detail' field")
        print(f"      JavaScript displays arrays as '[object Object]' when converted to string")
        print(f"      Frontend should iterate through error arrays and display individual messages")
    else:
        print(f"   No '[object Object]' errors detected in current tests")
    
    # Print final summary
    print(f"\n📊 FINAL TEST SUMMARY:")
    print(f"   Total Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {len(tester.failed_tests)}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Conclusion
    valid_scenarios_working = (object_error_results['valid_new_questions']['success'] and 
                              object_error_results['valid_pyq_solutions']['success'])
    
    if valid_scenarios_working:
        print(f"\n✅ CONCLUSION: Auto-generation endpoint works correctly with valid parameters")
        print(f"   '[object Object]' error only occurs with invalid input validation")
        print(f"   Frontend should implement proper error handling for validation arrays")
    else:
        print(f"\n❌ CONCLUSION: Auto-generation endpoint has issues even with valid parameters")
        print(f"   Need to investigate backend implementation further")
    
    return 0 if valid_scenarios_working else 1

if __name__ == "__main__":
    sys.exit(main())