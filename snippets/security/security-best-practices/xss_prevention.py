"""XSS Prevention"""
import html
import bleach
from markupsafe import Markup

class XSSPrevention:
    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML entities"""
        return html.escape(text)
    
    @staticmethod
    def sanitize_html(html_content: str, allowed_tags: list = None) -> str:
        """Sanitize HTML allowing only safe tags"""
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'a']
        
        return bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes={'a': ['href', 'title']},
            strip=True
        )
    
    @staticmethod
    def safe_render(template_var: str) -> Markup:
        """Safely render in templates"""
        return Markup(html.escape(template_var))

if __name__ == "__main__":
    xss = XSSPrevention()
    dangerous = '<script>alert("XSS")</script><p>Safe text</p>'
    print(f"Escaped: {xss.escape_html(dangerous)}")
    print(f"Sanitized: {xss.sanitize_html(dangerous)}")
