import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class LLMClient:
    def __init__(self, model_name: str = "gpt-4.1"):
        self.model_name = model_name
        self.client = self._initialize_client()
        
    def _initialize_client(self) -> OpenAI:
        """Initialize the OpenAI client."""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            return OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            raise
            
    def get_completion(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Get completion from OpenAI Responses API with web search capability.
        
        Args:
            system_prompt: System prompt for the conversation
            user_prompt: User prompt for the analysis request
            
        Returns:
            Optional[str]: The completion response or None if failed
        """
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_output_tokens=4000
            )
            return response.output_text
        except Exception as e:
            print(f"Error getting completion: {str(e)}")
            return None
        
if __name__ == "__main__":
    llm_client = LLMClient()
    result = llm_client.get_completion(
        "Please be concise and to the point. Do not include any other information.",
        'What is the date today?',
    )
    if result:
        print(result)
