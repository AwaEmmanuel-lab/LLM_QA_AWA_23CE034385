#!/usr/bin/env python3


import os
import string
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# Load environment variables
load_dotenv()


class CLIQuestionProcessor:
    """Process and normalize user questions for CLI"""
    
    @staticmethod
    def preprocess(question: str) -> tuple[str, str]:
        """Preprocess question and return processed and original versions"""
        original = question
        lowercased = question.lower()
        no_punct = lowercased.translate(str.maketrans('', '', string.punctuation))
        tokens = no_punct.split()
        processed = ' '.join(tokens)
        
        print("\n--- Preprocessing Steps ---")
        print(f"Original: {original}")
        print(f"Lowercased: {lowercased}")
        print(f"Punctuation Removed: {no_punct}")
        print(f"Tokens: {tokens}")
        print(f"Processed: {processed}")
        print("-------------------------\n")
        
        return processed, original


class CLIGeminiClient:
    """Wrapper for Gemini API with CLI-specific functionality"""
    
    DEFAULT_MODEL = "gemini-1.5-flash"
    
    def __init__(self, api_key: str):
        """Initialize Gemini client"""
        self.api_key = api_key
        self.model = self.DEFAULT_MODEL
        self.client = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the client"""
        try:
            if not self.api_key:
                raise ValueError("API key required")
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing client: {e}")
            self.client = None
    
    def is_ready(self) -> bool:
        """Check if client is ready"""
        return self.client is not None
    
    def query(self, question: str) -> str:
        """Send question to Gemini and get response"""
        if not self.is_ready():
            return "Client not initialized"
        
        try:
            prompt = f"Answer the following question concisely: {question}"
            print(f"Sending to LLM API (Model: {self.model})...")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text if response and response.text else "No response generated. Please try again."
        except APIError as e:
            return f"API Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"


class CLIApplication:
    """Main CLI application handler"""
    
    def __init__(self):
        """Initialize CLI application"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = CLIGeminiClient(self.api_key) if self.api_key else None
        self.processor = CLIQuestionProcessor()
    
    def print_header(self) -> None:
        """Print application header"""
        print("=" * 60)
        print("LLM Question and Answering CLI")
        print("Name: Osarenkhoe Osatohanmwen")
        print("Matric No: 23CG034140")
        print("=" * 60)
    
    def validate_api_key(self) -> bool:
        """Validate API key is available"""
        if not self.api_key:
            print("\n❌ ERROR: GEMINI_API_KEY not found!")
            print("Please create a .env file with:")
            print("GEMINI_API_KEY=your_api_key_here")
            print("\nGet your key from: https://makersuite.google.com/app/apikey")
            return False
        return True
    
    def print_instructions(self) -> None:
        """Print user instructions"""
        print("\n✓ API Key loaded successfully")
        print("\nType 'quit' or 'exit' to close the application.\n")
    
    def get_user_question(self) -> str:
        """Get and validate user question"""
        print("-" * 60)
        question = input("Enter your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            return None
        
        if not question:
            print("Please enter a valid question.\n")
            return ""
        
        return question
    
    def display_answer(self, answer: str) -> None:
        """Display the answer"""
        print("\n" + "=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print(answer)
        print("=" * 60 + "\n")
    
    def run(self) -> None:
        """Run the CLI application"""
        self.print_header()
        
        if not self.validate_api_key():
            return
        
        self.print_instructions()
        
        while True:
            question = self.get_user_question()
            
            if question is None:
                print("\nThank you for using the LLM Q&A CLI. Goodbye!")
                break
            
            if question == "":
                continue
            
            # Preprocess question
            _, original_question = self.processor.preprocess(question)
            
            # Query LLM
            print("Processing your question...")
            answer = self.gemini_client.query(original_question)
            
            # Display answer
            self.display_answer(answer)


def main():
    """Entry point"""
    app = CLIApplication()
    app.run()


if __name__ == "__main__":
    main()

