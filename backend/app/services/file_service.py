from fastapi import UploadFile, HTTPException
import io

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
        
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400, 
                detail="Could not decode file as UTF-8. Please upload a text file."
            )
        finally:
            await file.close()
        
        return text

file_service = FileService()
