"""Content Security Policy"""
class CSPBuilder:
    def __init__(self):
        self.directives = {}
    
    def default_src(self, *sources):
        self.directives['default-src'] = ' '.join(sources)
        return self
    
    def script_src(self, *sources):
        self.directives['script-src'] = ' '.join(sources)
        return self
    
    def style_src(self, *sources):
        self.directives['style-src'] = ' '.join(sources)
        return self
    
    def img_src(self, *sources):
        self.directives['img-src'] = ' '.join(sources)
        return self
    
    def build(self) -> str:
        return '; '.join(f"{k} {v}" for k, v in self.directives.items())

if __name__ == "__main__":
    csp = (CSPBuilder()
           .default_src("'self'")
           .script_src("'self'", "'unsafe-inline'", "https://cdn.example.com")
           .style_src("'self'", "'unsafe-inline'")
           .img_src("'self'", "data:", "https:")
           .build())
    print(f"CSP: {csp}")
