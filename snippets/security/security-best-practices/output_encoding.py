"""Output Encoding"""
class OutputEncoding:
    @staticmethod
    def encode_for_html(text: str) -> str:
        import html
        return html.escape(text)
