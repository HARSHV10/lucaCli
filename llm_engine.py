import json
import requests
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMEngine:
    def __init__(self, config):
        self.provider = config.get("provider")
        self.model = config.get("model")
        self.api_key = config.get("api_key")
        self.api_base = config.get("api_base")
        
        if self.provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "ollama":
            self.api_base = self.api_base or "http://localhost:11434"
        elif self.provider == "anthropic":
            pass # No client init needed
        elif self.provider == "gemini":
            pass # No client init needed

    def generate_command(self, user_prompt, os_name="Windows"):
        system_prompt = (
            f"You are a command-line helper. Verify if the user wants to perform an action, is asking a question that requires checking system state, or is asking a general question. "
            f"If it's an action, set 'mode' to 'execute'. "
            f"If it's a system question (e.g., 'what files are here'), set 'mode' to 'query' and provide a command. "
            f"If it's a general question (e.g., 'what is 2+2', 'explain git'), set 'mode' to 'direct' and provide the answer in 'explanation'. Set 'command' to null. "
            f"Target OS: {os_name}. "
            "Return the response in raw JSON format with NO markdown formatting. "
            "The JSON must have the following keys: "
            "'command' (string or null), 'explanation' (string), 'is_destructive' (boolean), 'mode' (string: 'execute', 'query', or 'direct'). "
            "Example: {\"command\": null, \"explanation\": \"The answer is 4.\", \"is_destructive\": false, \"mode\": \"direct\"}"
        )

        if self.provider == "openai":
            return self._query_openai(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return self._query_ollama(system_prompt, user_prompt)
        elif self.provider == "anthropic":
            return self._query_anthropic(system_prompt, user_prompt)
        elif self.provider == "gemini":
            return self._query_gemini(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported or unconfigured provider: {self.provider}")

    def _query_openai(self, system_prompt, user_prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}

    def _query_ollama(self, system_prompt, user_prompt):
        url = f"{self.api_base}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\nUser: {user_prompt}",
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return json.loads(data["response"])
        except Exception as e:
            return {"error": str(e)}

    def _query_anthropic(self, system_prompt, user_prompt):
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["content"][0]["text"]
            
            # Find JSON in the response (in case of extra text)
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return json.loads(content)
                
        except Exception as e:
             return {"error": f"Anthropic Error: {str(e)}"}

    def _query_gemini(self, system_prompt, user_prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser Request: {user_prompt}"}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            try:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return {"error": "Invalid response structure from Gemini API."}

            # Find JSON in the response (in case of extra text)
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If direct parsing fails and no JSON block found, try to clean markdown
                    cleaned = content.replace("```json", "").replace("```", "").strip()
                    return json.loads(cleaned)

        except Exception as e:
             return {"error": f"Gemini Error: {str(e)}"}

    def analyze_output(self, original_prompt, command_output, os_name="Windows"):
        system_prompt = (
            f"You are a helpful assistant analyzing command-line output for {os_name}. "
            f"The user asked: '{original_prompt}'. "
            f"The command output is:\n{command_output}\n\n"
            "Provide a concise, natural language answer to the user's question based on this output."
        )
        
        # Use the configured provider to generate the answer
        # For simplicity, we reuse the existing query methods but treat the result as text, not JSON command data
        # We need a slight modification to the query methods to generic text generation or just wrap it here.
        # To avoid changing all _query methods to handle non-JSON, let's just use a simple request here for the specific provider.
        
        # NOTE: Ideally we refactor _query_* to be more generic, but for now we duplicate the call logic slightly 
        # or we accept that _query_* expects JSON. 
        # Let's try to reuse the provider logic but ask for JSON wrapping to be safe with existing methods?
        # No, better to add a simple text generation capability.
        
        if self.provider == "openai":
             return self._generate_text_openai(system_prompt)
        elif self.provider == "ollama":
             return self._generate_text_ollama(system_prompt)
        elif self.provider == "anthropic":
             return self._generate_text_anthropic(system_prompt)
        elif self.provider == "gemini":
             return self._generate_text_gemini(system_prompt)
        return "Analysis failed: Unsupported provider."

    def _generate_text_openai(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing output: {e}"

    def _generate_text_ollama(self, prompt):
        url = f"{self.api_base}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            return data.get("response", "No response from Ollama.")
        except Exception as e:
            return f"Error: {e}"

    def _generate_text_anthropic(self, prompt):
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            return data["content"][0]["text"]
        except Exception as e:
            return f"Error: {e}"

    def _generate_text_gemini(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error: {e}"
