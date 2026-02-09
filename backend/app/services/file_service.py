from fastapi import UploadFile, HTTPException
import io
from PyPDF2 import PdfReader

class FileService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    async def read_file(self, file: UploadFile) -> str:
        # Validate file size
        content = await file.read()
        
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {self.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Validate file is not empty
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Check if it's a PDF file
        file_extension = None
        if file.filename:
            file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else None
        
        if file_extension == ".pdf" or file.content_type == "application/pdf":
            # Extract text from PDF
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PdfReader(pdf_file)
                
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="PDF appears to be empty or contains only images. Please upload a PDF with text content."
                    )
                
                return text.strip()
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to read PDF file: {str(e)}"
                )
        else:
            # Handle text files
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not decode file as UTF-8. Please upload a text file or PDF."
                )
            finally:
                await file.close()
            
            return text

file_service = FileService()
