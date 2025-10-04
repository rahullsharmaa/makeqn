import requests
import json
from datetime import datetime

class DataInvestigationTester:
    def __init__(self, base_url="https://questgen-agent-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def get_data(self, endpoint):
        """Get data from an endpoint"""
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error {response.status_code} for {endpoint}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Exception for {endpoint}: {str(e)}")
            return []

    def investigate_database_structure(self):
        """Investigate the complete database structure"""
        print("🔍 INVESTIGATING DATABASE STRUCTURE")
        print("=" * 60)
        
        # Get all exams
        exams = self.get_data("exams")
        print(f"\n📊 EXAMS: {len(exams)} found")
        for exam in exams:
            print(f"  - {exam['name']} ({exam['id']})")
        
        # For each exam, get courses
        exam_course_map = {}
        for exam in exams:
            exam_id = exam['id']
            courses = self.get_data(f"courses/{exam_id}")
            exam_course_map[exam_id] = courses
            print(f"\n📊 COURSES for {exam['name']}: {len(courses)} found")
            for course in courses:
                print(f"  - {course['name']} ({course['id']})")
        
        # For each course, get subjects
        course_subject_map = {}
        for exam_id, courses in exam_course_map.items():
            for course in courses:
                course_id = course['id']
                subjects = self.get_data(f"subjects/{course_id}")
                course_subject_map[course_id] = subjects
                print(f"\n📊 SUBJECTS for {course['name']}: {len(subjects)} found")
                for subject in subjects:
                    print(f"  - {subject['name']} ({subject['id']})")
        
        # For each subject, get units
        subject_unit_map = {}
        for course_id, subjects in course_subject_map.items():
            for subject in subjects:
                subject_id = subject['id']
                units = self.get_data(f"units/{subject_id}")
                subject_unit_map[subject_id] = units
                print(f"\n📊 UNITS for {subject['name']}: {len(units)} found")
                for unit in units:
                    print(f"  - {unit['name']} ({unit['id']})")
        
        # For each unit, get chapters
        unit_chapter_map = {}
        for subject_id, units in subject_unit_map.items():
            for unit in units:
                unit_id = unit['id']
                chapters = self.get_data(f"chapters/{unit_id}")
                unit_chapter_map[unit_id] = chapters
                print(f"\n📊 CHAPTERS for {unit['name']}: {len(chapters)} found")
                for chapter in chapters:
                    print(f"  - {chapter['name']} ({chapter['id']})")
        
        # For each chapter, get topics
        chapter_topic_map = {}
        complete_paths = []
        for unit_id, chapters in unit_chapter_map.items():
            for chapter in chapters:
                chapter_id = chapter['id']
                topics = self.get_data(f"topics/{chapter_id}")
                chapter_topic_map[chapter_id] = topics
                print(f"\n📊 TOPICS for {chapter['name']}: {len(topics)} found")
                for topic in topics:
                    print(f"  - {topic['name']} ({topic['id']})")
                    # This is a complete path
                    complete_paths.append({
                        'topic_id': topic['id'],
                        'topic_name': topic['name'],
                        'chapter_name': chapter['name'],
                        'unit_name': [u['name'] for u in subject_unit_map.values() for u in u if u['id'] == unit_id][0] if unit_id in [u['id'] for units in subject_unit_map.values() for u in units] else 'Unknown',
                        'path': f"Topic: {topic['name']} -> Chapter: {chapter['name']}"
                    })
        
        print(f"\n✅ COMPLETE PATHS FOUND: {len(complete_paths)}")
        for i, path in enumerate(complete_paths[:5]):  # Show first 5
            print(f"  {i+1}. {path['path']}")
        
        return complete_paths

    def test_question_generation_detailed(self, topic_id, question_type):
        """Test question generation with detailed error reporting"""
        print(f"\n🔍 Testing {question_type} generation for topic {topic_id}")
        
        request_data = {
            "topic_id": topic_id,
            "question_type": question_type,
            "part_id": None,
            "slot_id": None
        }
        
        url = f"{self.api_url}/generate-question"
        try:
            response = requests.post(url, json=request_data, timeout=60)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Generated {question_type} question")
                print(f"Question: {data.get('question_statement', '')[:100]}...")
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error Detail: {error_data.get('detail', 'No detail')}")
                except:
                    print(f"Raw Response: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False

def main():
    print("🚀 Starting Database Investigation...")
    print("=" * 60)
    
    tester = DataInvestigationTester()
    
    # Investigate database structure
    complete_paths = tester.investigate_database_structure()
    
    if complete_paths:
        print(f"\n🎯 Testing question generation with first complete path...")
        topic_id = complete_paths[0]['topic_id']
        
        # Test all question types
        question_types = ["MCQ", "MSQ", "NAT", "SUB"]
        success_count = 0
        
        for q_type in question_types:
            if tester.test_question_generation_detailed(topic_id, q_type):
                success_count += 1
        
        print(f"\n📊 QUESTION GENERATION RESULTS: {success_count}/{len(question_types)} successful")
    else:
        print("\n❌ No complete paths found - cannot test question generation")
    
    print("\n" + "=" * 60)
    print("🏁 Investigation Complete")

if __name__ == "__main__":
    main()