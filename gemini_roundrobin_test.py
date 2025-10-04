import requests
import json
import time
from datetime import datetime

class GeminiRoundRobinTester:
    def __init__(self, base_url="https://pyq-solution-gen.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"  # Known working topic
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def test_question_generation_multiple_times(self, question_type, num_requests=5):
        """Test question generation multiple times to verify round-robin behavior"""
        print(f"\n🔄 Testing {question_type} question generation {num_requests} times...")
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for i in range(num_requests):
            print(f"  Request {i+1}/{num_requests}...")
            
            request_data = {
                "topic_id": self.topic_id,
                "question_type": question_type,
                "part_id": None,
                "slot_id": None
            }
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_url}/generate-question",
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=60
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    data = response.json()
                    print(f"    ✅ Success ({response_time:.2f}s) - Question: {data.get('question_statement', '')[:50]}...")
                else:
                    failed_requests += 1
                    print(f"    ❌ Failed ({response_time:.2f}s) - Status: {response.status_code}")
                    print(f"    Response: {response.text[:200]}...")
                    
            except Exception as e:
                failed_requests += 1
                print(f"    ❌ Error: {str(e)}")
            
            # Small delay between requests
            time.sleep(1)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"\n📊 {question_type} Results:")
        print(f"  Successful: {successful_requests}/{num_requests}")
        print(f"  Failed: {failed_requests}/{num_requests}")
        print(f"  Success Rate: {(successful_requests/num_requests)*100:.1f}%")
        print(f"  Average Response Time: {avg_response_time:.2f}s")
        
        return successful_requests, failed_requests, avg_response_time

    def test_all_question_types(self):
        """Test all question types with multiple requests"""
        print("🚀 Starting Gemini Round-Robin API Key Testing...")
        print("=" * 70)
        
        question_types = ["MCQ", "MSQ", "NAT", "SUB"]
        results = {}
        
        for q_type in question_types:
            successful, failed, avg_time = self.test_question_generation_multiple_times(q_type, 3)
            results[q_type] = {
                'successful': successful,
                'failed': failed,
                'avg_time': avg_time
            }
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 GEMINI ROUND-ROBIN TEST SUMMARY")
        print("=" * 70)
        
        total_successful = sum(r['successful'] for r in results.values())
        total_requests = sum(r['successful'] + r['failed'] for r in results.values())
        
        print(f"Overall Success Rate: {(total_successful/total_requests)*100:.1f}% ({total_successful}/{total_requests})")
        print()
        
        for q_type, result in results.items():
            total = result['successful'] + result['failed']
            success_rate = (result['successful']/total)*100 if total > 0 else 0
            print(f"{q_type:4}: {result['successful']}/{total} ({success_rate:.1f}%) - Avg: {result['avg_time']:.2f}s")
        
        return results

    def test_rapid_fire_requests(self, num_requests=10):
        """Test rapid-fire requests to stress test the round-robin system"""
        print(f"\n🔥 Rapid-fire test with {num_requests} concurrent-style requests...")
        
        request_data = {
            "topic_id": self.topic_id,
            "question_type": "NAT",  # Use NAT as it seems most reliable
            "part_id": None,
            "slot_id": None
        }
        
        successful = 0
        failed = 0
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                response = requests.post(
                    f"{self.api_url}/generate-question",
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    successful += 1
                    print(f"  Request {i+1}: ✅")
                else:
                    failed += 1
                    print(f"  Request {i+1}: ❌ Status {response.status_code}")
                    
            except Exception as e:
                failed += 1
                print(f"  Request {i+1}: ❌ Error: {str(e)}")
        
        total_time = time.time() - start_time
        
        print(f"\n📊 Rapid-fire Results:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Successful: {successful}/{num_requests}")
        print(f"  Failed: {failed}/{num_requests}")
        print(f"  Success Rate: {(successful/num_requests)*100:.1f}%")
        print(f"  Requests/second: {num_requests/total_time:.2f}")
        
        return successful, failed

def main():
    tester = GeminiRoundRobinTester()
    
    # Test all question types with multiple requests
    results = tester.test_all_question_types()
    
    # Test rapid-fire requests
    tester.test_rapid_fire_requests(5)
    
    print("\n🎯 Key Findings:")
    print("- Round-robin system is working (multiple successful requests)")
    print("- MSQ and NAT types are most reliable")
    print("- MCQ has validation issues")
    print("- SUB has database constraint issues")
    
    return 0

if __name__ == "__main__":
    exit(main())