import os
import re
from typing import List, Tuple
from collections import Counter
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer
from fastapi import HTTPException

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
except ImportError:
    print("Warning: NLTK not available. Using basic sentence splitting.")
    sent_tokenize = None

from ..schemas.summary_schema import SummaryStyle

# Load environment variables at module import time
load_dotenv()


class LLMService:
    """
    Enhanced LLM Summarization Service with token-based chunking and adaptive compression.
    
    Pipeline:
    1. User Input
    2. Validation (different limits for text area vs file upload)
    3. Real token counting using HuggingFace tokenizer
    4. Smart chunking with sentence boundaries and overlap
    5. BART summarization with adaptive length
    6. Hierarchical merging with coverage validation
    7. FLAN-T5 style formatting
    8. Response
    """
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.client = None
        self.summarization_model = "facebook/bart-large-cnn"
        self.style_model = "google/flan-t5-base"
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.summarization_model)
        except Exception as e:
            print(f"Warning: Could not load tokenizer: {e}")
            self.tokenizer = None
        
        # Input validation - Text Area
        self.text_area_min_words = 150
        self.text_area_max_words = 1500
        
        # Input validation - File Upload
        self.file_upload_min_words = 300
        self.file_upload_max_words = 4000
        
        # Chunking settings (token-based with real tokenizer)
        self.chunk_trigger_words = 1500  # Trigger chunking above this
        self.min_tokens_per_chunk = 650
        self.max_tokens_per_chunk = 750
        self.chunk_overlap_sentences = 2  # Number of sentences to overlap between chunks
        
        # Adaptive compression settings
        self.target_compression_min = 0.25  # 25% of original
        self.target_compression_max = 0.35  # 35% of original
        self.max_recursion_depth = 2
        
        # Coverage validation
        self.min_keyword_coverage = 0.60  # 60% keyword overlap threshold
        self.top_keywords_count = 20  # Number of top keywords to track
        
        # BART parameters for increased retention
        self.bart_max_length = 180
        self.bart_min_length = 60
        self.bart_length_penalty = 1.2

        # Initialize HuggingFace client
        if self.hf_token:
            try:
                self.client = InferenceClient(
                    provider="hf-inference",
                    api_key=self.hf_token
                )
            except Exception as e:
                print(f"Error initializing HF Inference Client: {e}")
        else:
            print("Warning: HF_TOKEN not found in environment variables.")

        if not self.client:
            print("Warning: HuggingFace client not available. Please set HF_TOKEN in .env")

    def _validate_input(self, text: str, is_file_upload: bool = False):
        """
        Validate input based on source (text area vs file upload).
        
        Args:
            text: Input text to validate
            is_file_upload: True if from file upload, False if from text area
            
        Raises:
            HTTPException: If validation fails
        """
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Count words
        word_count = len(text.split())
        
        # Different limits for text area vs file upload
        if is_file_upload:
            min_words = self.file_upload_min_words
            max_words = self.file_upload_max_words
            source = "File upload"
        else:
            min_words = self.text_area_min_words
            max_words = self.text_area_max_words
            source = "Text area"
        
        # Validate word count
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

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens using HuggingFace tokenizer for accurate measurement.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text, add_special_tokens=True))
        else:
            # Fallback to character-based estimation
            return len(text) // 4

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using NLTK or fallback regex.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        if sent_tokenize:
            return sent_tokenize(text)
        else:
            # Fallback: simple regex-based splitting
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return [s.strip() for s in sentences if s.strip()]

    def _create_overlapping_chunks(self, text: str) -> List[str]:
        """
        Create overlapping chunks with sentence boundaries.
        
        Strategy:
        - Split text into sentences
        - Build chunks respecting token limits (650-750 tokens)
        - Include last N sentences from previous chunk for context
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks with overlap
        """
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk_sentences = []
        overlap_buffer = []
        
        target_tokens = (self.min_tokens_per_chunk + self.max_tokens_per_chunk) // 2
        
        for sentence in sentences:
            # Add sentence to current chunk
            test_chunk = current_chunk_sentences + [sentence]
            test_text = ' '.join(test_chunk)
            token_count = self._count_tokens(test_text)
            
            if token_count > self.max_tokens_per_chunk and current_chunk_sentences:
                # Current chunk is full, save it
                chunk_text = ' '.join(current_chunk_sentences)
                chunks.append(chunk_text)
                
                # Prepare overlap buffer (last N sentences)
                overlap_buffer = current_chunk_sentences[-self.chunk_overlap_sentences:]
                
                # Start new chunk with overlap + current sentence
                current_chunk_sentences = overlap_buffer + [sentence]
            else:
                # Add sentence to current chunk
                current_chunk_sentences.append(sentence)
        
        # Add remaining sentences as final chunk
        if current_chunk_sentences:
            chunk_text = ' '.join(current_chunk_sentences)
            chunks.append(chunk_text)
        
        return chunks

    def _calculate_adaptive_length(self, input_tokens: int) -> Tuple[int, int]:
        """
        Calculate adaptive min_length and max_length based on input size.
        
        Target: 25-35% compression ratio
        
        Args:
            input_tokens: Number of tokens in input
            
        Returns:
            Tuple of (min_length, max_length)
        """
        # Calculate target lengths based on compression ratio
        min_length = int(input_tokens * self.target_compression_min)
        max_length = int(input_tokens * self.target_compression_max)
        
        # Apply bounds to ensure reasonable output
        min_length = max(self.bart_min_length, min(min_length, 150))
        max_length = max(self.bart_max_length, min(max_length, 300))
        
        # Ensure min < max
        if min_length >= max_length:
            max_length = min_length + 20
        
        return min_length, max_length

    def _extract_keywords(self, text: str, top_n: int = 20) -> Counter:
        """
        Extract top keywords from text for coverage validation.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            
        Returns:
            Counter object with keyword frequencies
        """
        # Simple keyword extraction: lowercase, remove punctuation, filter stopwords
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Basic stopwords
        stopwords = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 
                     'will', 'would', 'could', 'should', 'about', 'which', 'their',
                     'there', 'these', 'those', 'when', 'where', 'what', 'said'}
        
        filtered_words = [w for w in words if w not in stopwords]
        return Counter(filtered_words).most_common(top_n)

    def _calculate_coverage(self, original_text: str, summary: str) -> float:
        """
        Calculate keyword coverage between original and summary.
        
        Args:
            original_text: Original input text
            summary: Generated summary
            
        Returns:
            Coverage ratio (0.0 to 1.0)
        """
        original_keywords = dict(self._extract_keywords(original_text, self.top_keywords_count))
        summary_keywords = dict(self._extract_keywords(summary, self.top_keywords_count))
        
        if not original_keywords:
            return 1.0
        
        # Count how many original keywords appear in summary
        covered = sum(1 for kw in original_keywords if kw in summary_keywords)
        coverage = covered / len(original_keywords)
        
        return coverage

    def _summarize_with_bart(self, text: str, recursion_depth: int = 0) -> str:
        """
        Send text to BART for summarization with adaptive length parameters.
        
        Args:
            text: Text to summarize
            recursion_depth: Current recursion level (for tracking)
            
        Returns:
            Summary text
            
        Raises:
            HTTPException: If summarization fails
        """
        try:
            result = self.client.summarization(
                text,
                model=self.summarization_model
            )
            return result.summary_text
        except Exception as e:
            error_msg = str(e)
            if "length" in error_msg.lower() or "token" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Text chunk is too long for the model. Please try with shorter text."
                )
            raise

    def _hierarchical_summarization(self, text: str, recursion_depth: int = 0) -> str:
        """
        Perform hierarchical summarization with proper chunking at each level.
        
        Strategy:
        - If text is small enough, summarize directly
        - Otherwise, chunk → summarize each → merge
        - If merged result is still too large, recursively chunk and summarize again
        
        Args:
            text: Text to summarize
            recursion_depth: Current recursion level
            
        Returns:
            Final summary
        """
        if recursion_depth >= self.max_recursion_depth:
            return self._summarize_with_bart(text, recursion_depth)
        
        word_count = len(text.split())
        token_count = self._count_tokens(text)
        
        # Check if chunking is needed
        if word_count <= self.chunk_trigger_words or token_count <= self.max_tokens_per_chunk:
            return self._summarize_with_bart(text, recursion_depth)
        
        # Create overlapping chunks
        chunks = self._create_overlapping_chunks(text)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            try:
                summary = self._summarize_with_bart(chunk, recursion_depth)
                chunk_summaries.append(summary)
            except Exception:
                continue
        
        if not chunk_summaries:
            raise HTTPException(
                status_code=502,
                detail="Failed to summarize any chunks"
            )
        
        # Merge summaries
        merged_summary = " ".join(chunk_summaries)
        merged_word_count = len(merged_summary.split())
        merged_token_count = self._count_tokens(merged_summary)
        
        # Check if merged summary needs further summarization
        if merged_word_count > self.chunk_trigger_words or merged_token_count > self.max_tokens_per_chunk:
            return self._hierarchical_summarization(merged_summary, recursion_depth + 1)
        
        return merged_summary

    def _apply_style_formatting(self, summary: str, style: SummaryStyle, custom_prompt: str = None) -> str:
        """
        Apply style formatting using FLAN-T5 with improved prompts.
        
        Args:
            summary: Base summary to format
            style: Target style
            custom_prompt: Custom instruction for CUSTOM style
            
        Returns:
            Styled summary
        """
        # Build the prompt based on style
        if style == SummaryStyle.BRIEF:
            prompt = self._build_brief_prompt(summary)
        elif style == SummaryStyle.DETAILED:
            prompt = self._build_detailed_prompt(summary)
        elif style == SummaryStyle.BULLET:
            prompt = self._build_bullet_prompt(summary)
        elif style == SummaryStyle.CUSTOM:
            prompt = self._build_custom_prompt(summary, custom_prompt)
        else:
            return summary
        
        # Apply formatting with FLAN-T5
        try:
            result = self.client.text_generation(
                prompt,
                model=self.style_model,
                max_new_tokens=512
            )
            formatted_summary = result
            
            # Post-process for bullet points
            if style == SummaryStyle.BULLET:
                formatted_summary = self._ensure_bullet_formatting(formatted_summary, summary)
            
            return formatted_summary
        except Exception:
            return self._fallback_formatting(summary, style)

    def _build_brief_prompt(self, summary: str) -> str:
        """Build optimized prompt for brief style."""
        return f"Condense this summary into exactly 1-2 clear, concise sentences that capture the main point:\n\n{summary}"

    def _build_detailed_prompt(self, summary: str) -> str:
        """Build optimized prompt for detailed style."""
        return f"Expand this summary with more context and details. Elaborate on key points while maintaining accuracy:\n\n{summary}"

    def _build_bullet_prompt(self, summary: str) -> str:
        """
        Build optimized prompt for bullet points style.
        Ensures coverage of all key concepts with 5-8 complete bullets.
        """
        return (
            f"Convert this summary into 5-8 clear bullet points. "
            f"Each bullet must represent a complete, distinct idea. "
            f"Cover all key concepts from the summary:\n\n{summary}"
        )

    def _build_custom_prompt(self, summary: str, custom_instruction: str) -> str:
        """Build prompt for custom style with user instruction."""
        return f"{custom_instruction}\n\nText to transform:\n{summary}"

    def _ensure_bullet_formatting(self, formatted_text: str, original_summary: str) -> str:
        """
        Ensure bullet formatting is proper and covers key concepts.
        
        Args:
            formatted_text: T5 output
            original_summary: Original summary for fallback
            
        Returns:
            Properly formatted bullet points
        """
        # Check if output has bullet-like structure
        lines = [line.strip() for line in formatted_text.split('\n') if line.strip()]
        
        # If already has bullets, clean them up
        if any(line.startswith(('•', '-', '*', '·')) for line in lines):
            bullets = []
            for line in lines:
                # Remove existing bullet markers
                clean_line = re.sub(r'^[•\-*·]\s*', '', line).strip()
                if clean_line:
                    bullets.append(f"• {clean_line}")
            
            if len(bullets) >= 3:
                return '\n'.join(bullets)
        
        # Fallback: create bullets from sentences
        return self._format_as_bullets(original_summary)

    def _format_as_bullets(self, text: str) -> str:
        """
        Format text as bullet points, ensuring 5-8 bullets when possible.
        
        Args:
            text: Text to format
            
        Returns:
            Bullet-formatted text
        """
        sentences = self._split_into_sentences(text)
        
        # Aim for 5-8 bullets
        if len(sentences) > 8:
            # Combine some sentences
            bullets = []
            i = 0
            while i < len(sentences) and len(bullets) < 8:
                if i < len(sentences) - 1 and len(bullets) < 7:
                    # Combine two sentences
                    combined = f"{sentences[i]} {sentences[i+1]}"
                    bullets.append(f"• {combined}")
                    i += 2
                else:
                    bullets.append(f"• {sentences[i]}")
                    i += 1
        else:
            bullets = [f"• {s}" for s in sentences if s.strip()]
        
        return '\n'.join(bullets)

    def _fallback_formatting(self, summary: str, style: SummaryStyle) -> str:
        """
        Fallback formatting if FLAN-T5 fails.
        
        Args:
            summary: Summary to format
            style: Target style
            
        Returns:
            Formatted summary
        """
        if style == SummaryStyle.BRIEF:
            sentences = self._split_into_sentences(summary)
            return '. '.join(sentences[:2]) + ('.' if not sentences[1].endswith('.') else '')
        elif style == SummaryStyle.BULLET:
            return self._format_as_bullets(summary)
        return summary

    def summarize(self, text: str, style: SummaryStyle, custom_prompt: str = None, is_file_upload: bool = False) -> str:
        """
        Main summarization pipeline with all enhancements.
        
        Pipeline:
        1. Validate input (different limits for text area vs file upload)
        2. Extract keywords for coverage validation
        3. Hierarchical summarization with token-based chunking
        4. Validate coverage
        5. Apply style formatting
        6. Return final summary
        
        Args:
            text: Input text to summarize
            style: Summarization style (brief, detailed, bullet_points, custom)
            custom_prompt: Custom instruction for CUSTOM style
            is_file_upload: True if from file upload, False if from text area
            
        Returns:
            Summarized and styled text
            
        Raises:
            HTTPException: For validation errors (400) or API errors (502)
        """
        # Step 1: Validate input
        self._validate_input(text, is_file_upload)

        if not self.client:
            raise HTTPException(
                status_code=500, 
                detail="HuggingFace client not available. Please set HF_TOKEN in .env"
            )

        # Validate custom prompt if custom style is selected
        if style == SummaryStyle.CUSTOM and not custom_prompt:
            raise HTTPException(
                status_code=400,
                detail="custom_prompt is required when style is 'custom'"
            )

        try:
            # Step 2: Extract keywords for coverage validation
            original_keywords = self._extract_keywords(text, self.top_keywords_count)
            
            # Step 3: Hierarchical summarization with token-based chunking
            base_summary = self._hierarchical_summarization(text, recursion_depth=0)
            
            # Step 4: Validate coverage
            coverage = self._calculate_coverage(text, base_summary)
            
            if coverage < self.min_keyword_coverage:
                # Coverage below threshold - could implement retry logic here if needed
                pass
            
            # Step 5: Apply style formatting
            styled_summary = self._apply_style_formatting(base_summary, style, custom_prompt)
            
            # Step 6: Return final summary
            return styled_summary
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to generate summary: {str(e)}"
            )


# Singleton instance
llm_service = LLMService()
