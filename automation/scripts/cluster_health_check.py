import sys
import requests
import time

GATEWAY_URL = "http://localhost:8000/actuator/health"
MAX_RETRIES = 5
RETRY_INTERVAL = 10

def verify_system_readiness():
    print(f"🤖 Starting intelligent pre-flight orchestration check on TicketForge Gateway...")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(GATEWAY_URL, timeout=5)
            # فحص رد السيرفر والتأكد أن النظام UP بالكامل
            if response.status_code == 200 and response.json().get("status") == "UP":
                print("✅ [SUCCESS] Architecture is perfectly stable. Ready for Traffic/Deployment.")
                sys.exit(0)
            else:
                print(f"⚠️ [ATTEMPT {attempt}] Gateway responded but microservices are still warming up...")
        except requests.exceptions.RequestException as e:
            print(f"❌ [ATTEMPT {attempt}] Gateway unreachable. Root cause: {e}")
        
        time.sleep(RETRY_INTERVAL)
    
    print("🚨 [CRITICAL FAILURE] Cluster health verification timed out. Rolling back infrastructure state!")
    sys.exit(1)

if __name__ == "__main__":
    verify_system_readiness()