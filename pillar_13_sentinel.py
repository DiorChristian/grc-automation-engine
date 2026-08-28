import json
import requests

class Pillar13PredictiveEngine:
    def __init__(self, ollama_host="http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "llama3"
        
        # Pillar 13: Local Threat Intel Cache
        self.active_threat_patterns = [
            "public_s3_acl_write",
            "unrestricted_sg_0.0.0.0_22",
            "iam_wildcard_admin_assumerole"
        ]

    def evaluate_infrastructure_event(self, event_payload):
        """
        Pillar 13 Core: Evaluates incoming infrastructure events using 
        local LLM reasoning combined with active threat intelligence.
        """
        event_str = json.dumps(event_payload, indent=2)
        
        prompt = f"""
        You are the Pillar 13 Predictive Security Engine for NIST Cloud Sentinel.
        Analyze the following AWS configuration change or provisioning event.
        Cross-reference it with known active cloud exploit patterns.
        
        Active Threat Vectors to Watch For: {self.active_threat_patterns}
        
        Event Payload:
        {event_str}
        
        Provide your output strictly in valid JSON format with exactly three keys:
        - "risk_score": an integer from 0 to 100.
        - "prediction": a one-sentence description of the predicted security failure.
        - "action": must be strictly "ALLOW", "WARN", or "BLOCK".
        """
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_output = json.loads(result['response'])
                return ai_output
                
        except Exception as e:
            print(f"[PILLAR 13 FALLBACK] Local LLM unavailable ({str(e)}). Engaging fail-safe guardrail.")
            
        # Absolute guarantee: Always returns a valid dictionary, never None
        return {
            "risk_score": 50,
            "prediction": "AI evaluation bypassed due to local model offline status; defaulting to safety guardrail.",
            "action": "WARN"
        }