"""Secure Error Handling"""
import logging

class SecureErrorHandler:
    """Handle errors without exposing sensitive info"""
    
    def __init__(self):
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, user_facing: bool = True):
        """Handle error securely"""
        # Log detailed error
        self.logger.error(f"Error: {str(error)}", exc_info=True)
        
        # Return generic message to user
        if user_facing:
            return {
                'error': 'An error occurred',
                'code': 'INTERNAL_ERROR',
                'message': 'Please try again later'
            }
        else:
            # For debugging (never in production)
            return {
                'error': str(error),
                'type': type(error).__name__
            }
    
    def sanitize_error_message(self, error_msg: str) -> str:
        """Remove sensitive info from error messages"""
        # Remove file paths, SQL queries, etc.
        import re
        sanitized = re.sub(r'/[\w/]+\.py', '[file]', error_msg)
        sanitized = re.sub(r'SELECT .+ FROM', 'SELECT ... FROM', sanitized)
        return sanitized

if __name__ == "__main__":
    handler = SecureErrorHandler()
    try:
        raise ValueError("Database connection failed at /etc/app/config.py")
    except Exception as e:
        result = handler.handle_error(e)
        print(f"✓ User sees: {result}")
