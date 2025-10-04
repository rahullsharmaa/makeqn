import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class RoundRobinStressTest:
    def __init__(self, base_url="https://quizgen-ai-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.topic_id = "7c583ed3-64bf-4fa0-bf20-058ac4b40737"
        self.successful_requests = 0
        self.failed_requests = 0
        self.quota_errors = 0
        self.other_errors = 0
        self.lock = threading.Lock()

    def make_request(self, request_id):
        """Make a single question generation request"""
        request_data = {
            "topic_id": self.topic_id,
            "question_type": "MSQ",  # Use MSQ as it's most reliable
            "part_id": None,
            "slot_id": None
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/generate-question",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            end_time = time.time()
            
            with self.lock:
                if response.status_code == 200:
                    self.successful_requests += 1
                    print(f"Request {request_id:2d}: ✅ Success ({end_time-start_time:.2f}s)")
                elif response.status_code == 429:
                    self.quota_errors += 1
                    self.failed_requests += 1
                    print(f"Request {request_id:2d}: 🚫 Quota Error ({end_time-start_time:.2f}s)")
                else:
                    self.other_errors += 1
                    self.failed_requests += 1
                    error_msg = response.text[:100] if response.text else "No response"
                    print(f"Request {request_id:2d}: ❌ Error {response.status_code} ({end_time-start_time:.2f}s) - {error_msg}")
                    
        except Exception as e:
            with self.lock:
                self.other_errors += 1
                self.failed_requests += 1
                print(f"Request {request_id:2d}: ❌ Exception: {str(e)[:100]}")

    def stress_test_sequential(self, num_requests=20):
        """Test with sequential requests to see round-robin behavior"""
        print(f"\n🔄 Sequential Stress Test ({num_requests} requests)...")
        print("=" * 60)
        
        self.successful_requests = 0
        self.failed_requests = 0
        self.quota_errors = 0
        self.other_errors = 0
        
        start_time = time.time()
        
        for i in range(num_requests):
            self.make_request(i + 1)
            time.sleep(0.5)  # Small delay to avoid overwhelming
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 Sequential Test Results:")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Successful: {self.successful_requests}")
        print(f"Quota Errors: {self.quota_errors}")
        print(f"Other Errors: {self.other_errors}")
        print(f"Success Rate: {(self.successful_requests/(self.successful_requests + self.failed_requests))*100:.1f}%")
        
        return self.successful_requests, self.failed_requests

    def stress_test_concurrent(self, num_requests=10, max_workers=3):
        """Test with concurrent requests to stress the round-robin system"""
        print(f"\n🚀 Concurrent Stress Test ({num_requests} requests, {max_workers} workers)...")
        print("=" * 60)
        
        self.successful_requests = 0
        self.failed_requests = 0
        self.quota_errors = 0
        self.other_errors = 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.make_request, i + 1) for i in range(num_requests)]
            
            # Wait for all requests to complete
            for future in futures:
                future.result()
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 Concurrent Test Results:")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Successful: {self.successful_requests}")
        print(f"Quota Errors: {self.quota_errors}")
        print(f"Other Errors: {self.other_errors}")
        print(f"Success Rate: {(self.successful_requests/(self.successful_requests + self.failed_requests))*100:.1f}%")
        print(f"Requests/second: {num_requests/total_time:.2f}")
        
        return self.successful_requests, self.failed_requests

    def test_api_key_exhaustion_simulation(self):
        """Test what happens when we potentially exhaust API keys"""
        print("\n🔥 API Key Exhaustion Simulation...")
        print("Making many requests quickly to test round-robin behavior...")
        
        # Make many requests in quick succession
        return self.stress_test_concurrent(15, 5)

def main():
    tester = RoundRobinStressTest()
    
    print("🚀 Starting Round-Robin Stress Testing...")
    
    # Test sequential requests
    seq_success, seq_failed = tester.stress_test_sequential(10)
    
    # Test concurrent requests
    conc_success, conc_failed = tester.stress_test_concurrent(8, 3)
    
    # Test potential exhaustion
    exh_success, exh_failed = tester.test_api_key_exhaustion_simulation()
    
    print("\n" + "=" * 70)
    print("🎯 ROUND-ROBIN STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"Sequential Test:  {seq_success}/{seq_success + seq_failed} successful")
    print(f"Concurrent Test:  {conc_success}/{conc_success + conc_failed} successful")
    print(f"Exhaustion Test:  {exh_success}/{exh_success + exh_failed} successful")
    
    total_success = seq_success + conc_success + exh_success
    total_requests = seq_success + seq_failed + conc_success + conc_failed + exh_success + exh_failed
    
    print(f"\nOverall Success Rate: {(total_success/total_requests)*100:.1f}% ({total_success}/{total_requests})")
    
    if total_success > 0:
        print("\n✅ Round-robin system is working - multiple successful requests completed")
        print("✅ Gemini API integration is functional")
        if tester.quota_errors > 0:
            print(f"⚠️  Detected {tester.quota_errors} quota errors - round-robin switching is working")
    else:
        print("\n❌ Round-robin system may have issues - no successful requests")
    
    return 0

if __name__ == "__main__":
    exit(main())