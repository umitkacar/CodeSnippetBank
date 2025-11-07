"""Input Sanitization"""
class InputSanitization:
    @staticmethod
    def sanitize(input_str: str) -> str:
        import html
        return html.escape(input_str.strip())
