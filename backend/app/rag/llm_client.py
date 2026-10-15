import os
import json
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

class LLMClient:
    """
    Multi-provider LLM client with automatic fallback.
    Primary: Google Gemini (gemini-2.5-flash)
    Fallback: Groq (qwen/qwen3.8-27b or custom model)
    """
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip('"\'; ')
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip('"\'; ')
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()
        self.groq_model = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b").strip('"\'; ')

    def generate(self, user_prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """
        Generates text using primary provider, falling back seamlessly if an error occurs.
        """
        # Try Primary: Gemini
        if self.default_provider == "gemini" and self.gemini_key:
            res = self._call_gemini(user_prompt, system_instruction)
            if res.get("success"):
                return res

        # Fallback to Groq
        if self.groq_key:
            res = self._call_groq(user_prompt, system_instruction)
            if res.get("success"):
                return res

        return {
            "text": "Unable to connect to live LLM services. Please verify your internet connection and API keys.",
            "provider": "none",
            "model": "none",
            "success": False
        }

    def _call_gemini(self, user_prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Calls Google Gemini 2.5 Flash API with explicit thinking budget zero to avoid token truncation."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048,
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        # Extract all non-thought text parts
                        full_text = "".join(
                            p.get("text", "") for p in parts 
                            if "text" in p and not p.get("thought", False)
                        ).strip()
                        if full_text:
                            return {
                                "text": full_text,
                                "provider": "Google Gemini",
                                "model": "gemini-2.5-flash",
                                "success": True
                            }
                print(f"[Gemini Error]: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[Gemini Exception]: {e}")

        return {"success": False}

    def _call_groq(self, user_prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Calls Groq API as fallback."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        # Use available active model on Groq
        model_name = "qwen/qwen3.8-27b" if "gpt" in self.groq_model else self.groq_model

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024
        }

        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        text = choices[0]["message"]["content"].strip()
                        return {
                            "text": text,
                            "provider": "Groq",
                            "model": model_name,
                            "success": True
                        }
                print(f"[Groq Error]: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[Groq Exception]: {e}")

        return {"success": False}
