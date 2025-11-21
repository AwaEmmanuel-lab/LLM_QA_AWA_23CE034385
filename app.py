import os
import string
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from google import genai
from google.genai.errors import APIError

# Load environment variables
load_dotenv()


class GeminiClient:
    """Wrapper for Google Gemini API client"""
    
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    def __init__(self, api_key: str):
        """Initialize Gemini client with API key"""
        self.api_key = api_key
        self.model = self.DEFAULT_MODEL
        self.client = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the Gemini client"""
        try:
            if not self.api_key:
                raise ValueError("API key is required")
            self.client = genai.Client(api_key=self.api_key)
            print("✓ Gemini API initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            self.client = None
    
    def is_ready(self) -> bool:
        """Check if client is ready to use"""
        return self.client is not None
    
    def generate_response(self, prompt: str) -> str:
        """Generate response from Gemini"""
        if not self.is_ready():
            return None
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text if response and response.text else None
        except APIError as e:
            raise APIError(f"Gemini API Error: {str(e)}")


class QuestionProcessor:
    """Handle question preprocessing and normalization"""
    
    @staticmethod
    def preprocess(question: str) -> dict:
        """Preprocess question with normalization steps"""
        original = question
        lowercased = question.lower()
        no_punct = lowercased.translate(str.maketrans('', '', string.punctuation))
        tokens = no_punct.split()
        processed = ' '.join(tokens)
        
        return {
            "original": original,
            "lowercased": lowercased,
            "punctuation_removed": no_punct,
            "tokens": tokens,
            "processed": processed
        }


class FlaskApp:
    """Application factory for Flask app setup"""
    
    def __init__(self, gemini_client: GeminiClient):
        """Initialize Flask app with dependencies"""
        self.gemini_client = gemini_client
        self.app = Flask(__name__)
        CORS(self.app)
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register all Flask routes"""
        self.app.route("/")(self.index)
        self.app.route("/api/ask", methods=["POST"])(self.ask_question)
    
    def index(self):
        """Serve the main HTML page"""
        return render_template("index.html")
    
    def ask_question(self):
        """API endpoint to receive questions and return AI-generated answers"""
        if not self.gemini_client.is_ready():
            return (
                jsonify({
                    "error": "Gemini service not configured. Please check your API key."
                }),
                500,
            )
        
        try:
            data = request.get_json()
            
            if not data or "question" not in data:
                return jsonify({"error": "No question provided"}), 400
            
            question = data["question"].strip()
            
            if not question:
                return jsonify({"error": "Question cannot be empty"}), 400
            
            # Preprocess question
            preprocessing = QuestionProcessor.preprocess(question)
            
            # Generate response
            answer = self.gemini_client.generate_response(question)
            
            if not answer:
                answer = "I couldn't generate a response. Please try again."
            
            return jsonify({
                "question": question,
                "answer": answer,
                "preprocessing": preprocessing,
                "status": "success"
            }), 200
        
        except APIError as e:
            self.app.logger.error(f"Gemini API Error: {str(e)}")
            return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500
        except Exception as e:
            self.app.logger.error(f"Error: {str(e)}")
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
    def get_app(self):
        """Get the Flask app instance"""
        return self.app


# Initialize application
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = GeminiClient(GEMINI_API_KEY)
flask_app = FlaskApp(gemini_client)
app = flask_app.get_app()


def print_startup_banner() -> None:
    """Print application startup information"""
    print("=" * 60)
    print("AI Question Answering Interface")
    print("=" * 60)
    print("Server starting...")
    
    if not GEMINI_API_KEY:
        print("\n⚠️  WARNING: GEMINI_API_KEY not found!")
        print("Please create a .env file with your Google Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        print("=" * 60)
    
    print("\n✓ Server running at: http://localhost:5000")
    print("✓ Open your browser and navigate to the URL above")
    print("\nPress Ctrl+C to stop the server\n")


def main():
    """Run the Flask application"""
    print_startup_banner()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
