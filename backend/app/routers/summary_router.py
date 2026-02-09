from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from ..schemas.summary_schema import SummaryRequest, SummaryResponse, SummaryStyle
from ..services.llm_service import llm_service
from ..services.file_service import file_service
from typing import Optional

router = APIRouter()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    
    # Validate custom prompt if custom style is selected
    if request.style == SummaryStyle.CUSTOM and not request.custom_prompt:
        raise HTTPException(
            status_code=400, 
            detail="custom_prompt is required when style is 'custom'"
        )
    
    # Text area input - is_file_upload=False
    summary = llm_service.summarize(request.text, request.style, request.custom_prompt, is_file_upload=False)
    return SummaryResponse(
        summary=summary, 
        style=request.style.value, 
        word_count=len(summary.split())
    )

@router.post("/summarize-file", response_model=SummaryResponse)
async def summarize_file(
    file: UploadFile = File(...), 
    style: SummaryStyle = Form(SummaryStyle.BRIEF),
    custom_prompt: Optional[str] = Form(None)
):
    # Validate file type - check both content_type and filename extension
    allowed_types = ["text/plain", "text/csv", "application/json"]
    allowed_extensions = [".txt", ".csv", ".json"]
    
    file_extension = None
    if file.filename:
        file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else None
    
    # Check if either content type or extension is valid
    is_valid = (
        file.content_type in allowed_types or 
        file_extension in allowed_extensions or
        file.content_type is None  # Some clients don't send content_type
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    # Validate custom prompt if custom style is selected
    if style == SummaryStyle.CUSTOM and not custom_prompt:
        raise HTTPException(
            status_code=400, 
            detail="custom_prompt is required when style is 'custom'"
        )
    
    content = await file_service.read_file(file)
    # File upload input - is_file_upload=True
    summary = llm_service.summarize(content, style, custom_prompt, is_file_upload=True)
    return SummaryResponse(
        summary=summary, 
        style=style.value, 
        word_count=len(summary.split())
    )

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Summarization API is running"}

@router.get("/model-info")
def get_model_info():
    """Get information about the loaded models"""
    return {
        "summarization_model": "facebook/bart-large-cnn",
        "style_model": "google/flan-t5-base",
        "available": llm_service.client is not None,
        "input_limits": {
            "text_area": {
                "min_words": llm_service.text_area_min_words,
                "max_words": llm_service.text_area_max_words
            },
            "file_upload": {
                "min_words": llm_service.file_upload_min_words,
                "max_words": llm_service.file_upload_max_words
            }
        },
        "processing": {
            "chunk_trigger_words": llm_service.chunk_trigger_words,
            "token_chunk_size": f"{llm_service.min_tokens_per_chunk}-{llm_service.max_tokens_per_chunk} tokens",
            "target_compression": f"{llm_service.target_compression_min*100}%-{llm_service.target_compression_max*100}%"
        },
        "supported_styles": ["brief", "detailed", "bullet_points", "custom"]
    }
