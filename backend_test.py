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

def main():
    print("🚀 Testing Updated Question Generation Endpoint...")
    print("🎯 Focus: Gemini 2.0 Flash Structured JSON Output")
    print("=" * 60)
    
    tester = QuestionMakerAPITester()
    
    # Test basic connectivity first
    print("\n1️⃣ Testing Basic API Connectivity...")
    tester.test_root_endpoint()
    
    # Test the specific topic question generation (main focus)
    print("\n2️⃣ Testing Question Generation with Known Working Topic...")
    generation_results = tester.test_specific_topic_question_generation()
    
    # Test cascading endpoints to ensure they still work
    print("\n3️⃣ Testing Cascading Dropdown Endpoints...")
    tester.test_exams_endpoint()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {len(tester.failed_tests)}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Detailed question generation analysis
    if generation_results:
        print(f"\n🎯 QUESTION GENERATION ANALYSIS:")
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
    
    # Determine if JSON parsing issue is resolved
    question_generation_working = any(result['success'] for result in generation_results.values()) if generation_results else False
    
    if question_generation_working:
        print(f"\n✅ CONCLUSION: Gemini 2.0 Flash structured JSON output is working for some question types!")
    else:
        print(f"\n❌ CONCLUSION: JSON parsing issues persist - structured output may need further investigation")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())