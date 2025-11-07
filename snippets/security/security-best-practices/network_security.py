"""Network Security"""
class NetworkSecurity:
    @staticmethod
    def use_tls():
        """Always use TLS 1.2+"""
        return {'min_version': 'TLS1.2', 'ciphers': 'strong_ciphers_only'}
