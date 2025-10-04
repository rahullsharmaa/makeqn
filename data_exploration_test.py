import requests
import json

def explore_all_data():
    base_url = "https://quizgen-ai-2.preview.emergentagent.com/api"
    
    print("🔍 Exploring all available data...")
    
    # Get all exams
    try:
        exams_response = requests.get(f"{base_url}/exams")
        exams = exams_response.json()
        print(f"\n📚 Found {len(exams)} exams:")
        
        for exam in exams:
            print(f"  - {exam['name']} (ID: {exam['id']})")
            
            # Get courses for each exam
            courses_response = requests.get(f"{base_url}/courses/{exam['id']}")
            courses = courses_response.json()
            print(f"    Courses: {len(courses)}")
            
            for course in courses:
                print(f"      - {course['name']} (ID: {course['id']})")
                
                # Get subjects for each course
                subjects_response = requests.get(f"{base_url}/subjects/{course['id']}")
                subjects = subjects_response.json()
                print(f"        Subjects: {len(subjects)}")
                
                if subjects:
                    for subject in subjects[:2]:  # Show first 2 subjects
                        print(f"          - {subject['name']} (ID: {subject['id']})")
                        
                        # Get units for first subject
                        units_response = requests.get(f"{base_url}/units/{subject['id']}")
                        units = units_response.json()
                        print(f"            Units: {len(units)}")
                        
                        if units:
                            unit = units[0]
                            print(f"              - {unit['name']} (ID: {unit['id']})")
                            
                            # Get chapters
                            chapters_response = requests.get(f"{base_url}/chapters/{unit['id']}")
                            chapters = chapters_response.json()
                            print(f"                Chapters: {len(chapters)}")
                            
                            if chapters:
                                chapter = chapters[0]
                                print(f"                  - {chapter['name']} (ID: {chapter['id']})")
                                
                                # Get topics
                                topics_response = requests.get(f"{base_url}/topics/{chapter['id']}")
                                topics = topics_response.json()
                                print(f"                    Topics: {len(topics)}")
                                
                                if topics:
                                    topic = topics[0]
                                    print(f"                      - {topic['name']} (ID: {topic['id']})")
                                    
                                    # Test question generation
                                    print(f"                        Testing question generation...")
                                    question_data = {
                                        "topic_id": topic['id'],
                                        "question_type": "MCQ"
                                    }
                                    
                                    try:
                                        gen_response = requests.post(f"{base_url}/generate-question", json=question_data, timeout=30)
                                        if gen_response.status_code == 200:
                                            print(f"                        ✅ Question generation works!")
                                            return True
                                        else:
                                            print(f"                        ❌ Question generation failed: {gen_response.status_code}")
                                    except Exception as e:
                                        print(f"                        ❌ Question generation error: {str(e)}")
                                    
                                    return False  # Found data structure, can test frontend
                
                print()  # Empty line between courses
                
    except Exception as e:
        print(f"❌ Error exploring data: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    explore_all_data()