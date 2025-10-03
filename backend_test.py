import requests
import sys
import json
from datetime import datetime

class QuestionMakerAPITester:
    def __init__(self, base_url="https://exam-genius-10.preview.emergentagent.com"):
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
        """Test question generation"""
        request_data = {
            "topic_id": topic_id,
            "question_type": question_type,
            "part_id": None,
            "slot_id": None
        }
        
        success, data = self.run_test(
            f"Generate {question_type} Question for Topic {topic_id}", 
            "POST", 
            "generate-question", 
            200, 
            data=request_data
        )
        
        if success and data:
            print(f"   Generated question: {data.get('question_statement', '')[:100]}...")
            return data
        return None

    def test_cascading_flow(self):
        """Test the complete cascading dropdown flow"""
        print("\n🔄 Testing Complete Cascading Flow...")
        
        # Get exams
        exams = self.test_exams_endpoint()
        if not exams:
            print("❌ Cannot proceed - No exams found")
            return False
            
        exam_id = exams[0]['id']
        
        # Get courses
        courses = self.test_courses_endpoint(exam_id)
        if not courses:
            print("❌ Cannot proceed - No courses found")
            return False
            
        course_id = courses[0]['id']
        
        # Get subjects
        subjects = self.test_subjects_endpoint(course_id)
        if not subjects:
            print("❌ Cannot proceed - No subjects found")
            return False
            
        subject_id = subjects[0]['id']
        
        # Get units
        units = self.test_units_endpoint(subject_id)
        if not units:
            print("❌ Cannot proceed - No units found")
            return False
            
        unit_id = units[0]['id']
        
        # Get chapters
        chapters = self.test_chapters_endpoint(unit_id)
        if not chapters:
            print("❌ Cannot proceed - No chapters found")
            return False
            
        chapter_id = chapters[0]['id']
        
        # Get topics
        topics = self.test_topics_endpoint(chapter_id)
        if not topics:
            print("❌ Cannot proceed - No topics found")
            return False
            
        topic_id = topics[0]['id']
        
        # Test parts and slots
        self.test_parts_endpoint(course_id)
        self.test_slots_endpoint(course_id)
        
        # Test existing questions
        self.test_existing_questions_endpoint(topic_id)
        
        # Test question generation for different types
        question_types = ["MCQ", "MSQ", "NAT", "SUB"]
        for q_type in question_types:
            generated = self.test_question_generation(topic_id, q_type)
            if generated:
                print(f"✅ Successfully generated {q_type} question")
            else:
                print(f"❌ Failed to generate {q_type} question")
        
        return True

def main():
    print("🚀 Starting Question Maker API Tests...")
    print("=" * 60)
    
    tester = QuestionMakerAPITester()
    
    # Test basic connectivity
    tester.test_root_endpoint()
    
    # Test cascading flow
    tester.test_cascading_flow()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {len(tester.failed_tests)}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.failed_tests:
        print("\n❌ FAILED TESTS:")
        for failure in tester.failed_tests:
            print(f"  - {failure.get('test', 'Unknown')}: {failure.get('error', failure.get('response', 'Unknown error'))}")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())