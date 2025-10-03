import requests
import sys
import json
from datetime import datetime

class QuestionMakerAPITester:
    def __init__(self, base_url="https://questgen-auto.preview.emergentagent.com"):
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
            "exam_id": exam_id,
            "course_id": course_id,
            "config": {
                "correct_marks": 4.0,
                "incorrect_marks": -1.0,
                "skipped_marks": 0.0,
                "time_minutes": 180.0,
                "total_questions": 10
            },
            "generation_mode": "new_questions"
        }
        
        success, data = self.run_test("Start Auto Generation", "POST", "start-auto-generation", 200, data=request_data)
        if success and data:
            print(f"   Session created with ID: {data.get('session_id', 'N/A')}")
            print(f"   Total topics: {data.get('total_topics', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            return data
        return {}

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

def main():
    print("🚀 Testing Enhanced Question Generation System Backend...")
    print("🎯 Focus: New API Endpoints + Enhanced Question Generation")
    print("=" * 60)
    
    tester = QuestionMakerAPITester()
    
    # Test basic connectivity first
    print("\n1️⃣ Testing Basic API Connectivity...")
    tester.test_root_endpoint()
    
    # Test cascading endpoints to get working IDs
    print("\n2️⃣ Testing Cascading Dropdown Endpoints...")
    exams = tester.test_exams_endpoint()
    
    # Find ISI->MSQMS course for testing
    working_course_id = None
    working_exam_id = None
    
    if exams:
        for exam in exams:
            if "ISI" in exam.get('name', '').upper():
                exam_id = exam['id']
                working_exam_id = exam_id
                print(f"\n🔍 Found ISI exam: {exam['name']} ({exam_id})")
                
                courses = tester.test_courses_endpoint(exam_id)
                for course in courses:
                    if "MSQMS" in course.get('name', '').upper():
                        working_course_id = course['id']
                        print(f"✅ Found MSQMS course: {course['name']} ({working_course_id})")
                        break
                
                if working_course_id:
                    break
    
    # Use fallback IDs if not found
    if not working_course_id:
        working_course_id = "b8f7e2d1-4c3a-4b5e-8f9a-1b2c3d4e5f6g"  # Fallback
        working_exam_id = "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6"  # Fallback
        print(f"⚠️ Using fallback course_id: {working_course_id}")
    
    # Test new endpoints
    print("\n3️⃣ Testing New Enhanced Endpoints...")
    new_endpoint_results = {}
    
    # Update the test method to use found IDs
    tester.working_course_id = working_course_id
    tester.working_exam_id = working_exam_id
    
    # Test new endpoints individually
    topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
    
    # Test 1: All topics with weightage
    print(f"\n3.1️⃣ Testing All Topics with Weightage...")
    success, data = tester.test_all_topics_with_weightage(working_course_id)
    new_endpoint_results['all_topics_with_weightage'] = {'success': success, 'data': data}
    
    # Test 2: PYQ Solution Generation
    print(f"\n3.2️⃣ Testing PYQ Solution Generation...")
    success, data = tester.test_generate_pyq_solution(topic_id)
    new_endpoint_results['generate_pyq_solution'] = {'success': success, 'data': data}
    
    # Test 3: Manual Question Save
    print(f"\n3.3️⃣ Testing Manual Question Save...")
    success, data = tester.test_save_question_manually(topic_id)
    new_endpoint_results['save_question_manually'] = {'success': success, 'data': data}
    
    # Test 4: Auto Generation Start
    print(f"\n3.4️⃣ Testing Auto Generation Start...")
    success, data = tester.test_start_auto_generation(working_exam_id, working_course_id)
    new_endpoint_results['start_auto_generation'] = {'success': success, 'data': data}
    
    # Test enhanced question generation
    print("\n4️⃣ Testing Enhanced Question Generation...")
    generation_results = tester.test_specific_topic_question_generation()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {len(tester.failed_tests)}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # New endpoints analysis
    print(f"\n🆕 NEW ENDPOINTS ANALYSIS:")
    successful_new = [endpoint for endpoint, result in new_endpoint_results.items() if result['success']]
    failed_new = [endpoint for endpoint, result in new_endpoint_results.items() if not result['success']]
    
    for endpoint, result in new_endpoint_results.items():
        status = "✅ WORKING" if result['success'] else "❌ FAILED"
        print(f"   {endpoint}: {status}")
    
    # Enhanced question generation analysis
    if generation_results:
        print(f"\n🎯 ENHANCED QUESTION GENERATION ANALYSIS:")
        for q_type, result in generation_results.items():
            status = "✅ WORKING" if result['success'] else "❌ FAILED"
            print(f"   {q_type}: {status}")
    
    if tester.failed_tests:
        print("\n❌ DETAILED FAILURE ANALYSIS:")
        for failure in tester.failed_tests:
            print(f"\n  🔍 Test: {failure.get('test', 'Unknown')}")
            if 'topic_id' in failure:
                print(f"     Topic ID: {failure['topic_id']}")
            if 'error' in failure:
                print(f"     Error: {failure['error']}")
            if 'response' in failure:
                print(f"     Response: {failure['response'][:200]}...")
    
    # Overall conclusions
    new_endpoints_working = len(successful_new) > 0
    question_generation_working = any(result['success'] for result in generation_results.values()) if generation_results else False
    
    print(f"\n🎯 CONCLUSIONS:")
    if new_endpoints_working:
        print(f"✅ New endpoints: {len(successful_new)}/{len(new_endpoint_results)} working")
    else:
        print(f"❌ New endpoints: All failed - need investigation")
    
    if question_generation_working:
        print(f"✅ Enhanced question generation: Working for some question types")
    else:
        print(f"❌ Enhanced question generation: Issues persist")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())