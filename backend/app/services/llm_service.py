import os
import re
import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from dotenv import load_dotenv
from fastapi import HTTPException

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
except ImportError:
    sent_tokenize = None

from ..schemas.summary_schema import SummaryStyle

load_dotenv()


class LLMService:
    """
    Simplified LLM Summarization Service using BART-CNN with direct HTTP requests.
    """
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.model = "facebook/bart-large-cnn"
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        } if self.hf_token else {"Content-Type": "application/json"}
        
        # Input validation
        self.text_area_min_words = 50  # Reduced from 150 for better UX
        self.text_area_max_words = 1500
        self.file_upload_min_words = 100  # Reduced from 300
        self.file_upload_max_words = 4000
        
        # Presets for different summary styles
        self.presets = {
            "brief": {
                "max_length": 60,
                "min_length": 10,  # Reduced from 20
                "num_beams": 4,
                "length_penalty": 1.2,
                "do_sample": False,
                "early_stopping": True
            },
            "standard": {
                "max_length": 140,
                "min_length": 30,  # Reduced from 50
                "num_beams": 4,
                "length_penalty": 1.0,
                "do_sample": False,
                "early_stopping": True
            },
            "detailed": {
                "max_length": 230,
                "min_length": 60,  # Reduced from 110
                "num_beams": 5,
                "length_penalty": 0.9,
                "do_sample": False,
                "early_stopping": True
            },
            "bullet": {
                "max_length": 160,
                "min_length": 30,  # Reduced from 40
                "num_beams": 4,
                "length_penalty": 1.0,
                "do_sample": False,
                "early_stopping": True
            }
        }

        if not self.hf_token:
            print("Warning: HF_TOKEN not found in environment variables.")

    def _validate_input(self, text: str, is_file_upload: bool = False):
        """Validate input based on source."""
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        word_count = len(text.split())
        
        if is_file_upload:
            min_words = self.file_upload_min_words
            max_words = self.file_upload_max_words
            source = "File upload"
        else:
            min_words = self.text_area_min_words
            max_words = self.text_area_max_words
            source = "Text area"
        
        if word_count < min_words:
            raise HTTPException(
                status_code=400,
                detail=f"{source}: Text too short. Minimum {min_words} words required. Your text has {word_count} words."
            )
        
        if word_count > max_words:
            raise HTTPException(
                status_code=400,
                detail=f"{source}: Text too long. Maximum {max_words} words allowed. Your text has {word_count} words."
            )

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for summarization."""
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        # Ensure text ends with proper punctuation
        text = text.strip()
        if text and text[-1] not in '.!?':
            text += '.'
        
        # Ensure minimum sentence structure
        # BART needs at least a few sentences to work properly
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            raise HTTPException(
                status_code=400,
                detail="Text must contain at least 3 complete sentences for summarization."
            )
        
        return text

    def _split_into_sentences(self, text: str):
        """Split text into sentences using NLTK or fallback regex."""
        if sent_tokenize:
            return sent_tokenize(text)
        else:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return [s.strip() for s in sentences if s.strip()]

    def _hf_summarize(self, text: str, preset: str, timeout: int = 60) -> str:
        """
        Summarize text using HuggingFace Inference API with the chosen preset.
        """
        if preset not in self.presets:
            raise ValueError(f"Unknown preset '{preset}'. Choose one of: {list(self.presets)}")
        
        # Preprocess text
        clean_text = self._preprocess_text(text)
        
        # Check if text is too short after cleaning
        if len(clean_text.split()) < 30:
            raise HTTPException(
                status_code=400,
                detail="Text is too short after preprocessing. Please provide more content."
            )
        
        payload = {
            "inputs": clean_text,
            "parameters": self.presets[preset]
        }
        
        try:
            resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=timeout)
            resp.raise_for_status()
        except Timeout:
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Try with shorter text."
            )
        except HTTPError as e:
            content = resp.text if 'resp' in locals() else "<no response body>"
            # Parse error message for better user feedback
            error_msg = content
            try:
                error_data = resp.json()
                if isinstance(error_data, dict) and 'error' in error_data:
                    error_msg = error_data['error']
            except:
                pass
            
            raise HTTPException(
                status_code=502,
                detail=f"Model error: {error_msg}. Try with different text or shorter content."
            )
        except RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"Network error calling HF Inference API: {e}"
            )
        
        data = resp.json()
        
        # Handle HF error responses
        if isinstance(data, dict) and data.get("error"):
            error_msg = data['error']
            # Provide user-friendly error messages
            if "index out of range" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Text format issue. Please ensure your text has proper sentences and punctuation."
                )
            raise HTTPException(
                status_code=502,
                detail=f"Model error: {error_msg}"
            )
        
        # Extract summary from response
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            summary = data[0].get("summary_text") or data[0].get("generated_text") or str(data[0])
            return summary.strip()
        
        # Fallback
        return str(data)

    def _format_as_bullets(self, text: str) -> str:
        """Format text as bullet points using NLTK."""
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return text
        
        bullets = [f"• {sentence.strip()}" for sentence in sentences if sentence.strip()]
        return '\n'.join(bullets)

    def summarize(self, text: str, style: SummaryStyle, custom_prompt: str = None, is_file_upload: bool = False) -> str:
        """
        Main summarization method.
        
        Args:
            text: Input text to summarize
            style: Summarization style (brief, detailed, bullet_points, standard, custom)
            custom_prompt: Custom instruction (not used with BART-only)
            is_file_upload: True if from file upload, False if from text area
            
        Returns:
            Summarized text
        """
        # Validate input
        self._validate_input(text, is_file_upload)

        if not self.hf_token:
            raise HTTPException(
                status_code=500, 
                detail="HuggingFace token not available. Please set HF_TOKEN in .env"
            )

        try:
            # Map style to preset
            if style == SummaryStyle.BRIEF:
                preset = "brief"
            elif style == SummaryStyle.DETAILED:
                preset = "detailed"
            elif style == SummaryStyle.BULLET:
                preset = "bullet"
            else:  # STANDARD or CUSTOM
                preset = "standard"
            
            # Generate summary with BART
            summary = self._hf_summarize(text, preset)
            
            # Format as bullets if needed
            if style == SummaryStyle.BULLET:
                summary = self._format_as_bullets(summary)
            
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Summarization error: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to generate summary: {str(e)}"
            )


# Singleton instance
llm_service = LLMService()
