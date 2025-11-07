"""File Upload Security"""
import os
import magic
from werkzeug.utils import secure_filename

class SecureFileUpload:
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_MIMETYPES = {
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'text/plain'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SecureFileUpload.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_mimetype(file_path: str) -> bool:
        """Validate file MIME type"""
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)
        return file_mime in SecureFileUpload.ALLOWED_MIMETYPES
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename"""
        return secure_filename(filename)
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Check file size"""
        return file_size <= SecureFileUpload.MAX_FILE_SIZE

if __name__ == "__main__":
    uploader = SecureFileUpload()
    print(f"✓ Allowed: {uploader.allowed_file('image.jpg')}")
    print(f"✓ Sanitized: {uploader.sanitize_filename('../../../etc/passwd')}")
