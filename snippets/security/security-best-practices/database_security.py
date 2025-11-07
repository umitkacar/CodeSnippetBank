"""Database Security Best Practices"""
class DatabaseSecurity:
    """Secure database operations"""
    
    @staticmethod
    def use_parameterized_queries():
        """Always use parameterized queries"""
        # Good
        query = "SELECT * FROM users WHERE id = ?"
        # Bad: "SELECT * FROM users WHERE id = " + user_input
        return query
    
    @staticmethod
    def encrypt_sensitive_fields():
        """Encrypt sensitive database fields"""
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        sensitive_data = b"SSN: 123-45-6789"
        encrypted = cipher.encrypt(sensitive_data)
        return encrypted
    
    @staticmethod
    def implement_least_privilege():
        """Database user should have minimal permissions"""
        return {
            'read_only_user': ['SELECT'],
            'api_user': ['SELECT', 'INSERT', 'UPDATE'],
            'admin_user': ['ALL']
        }
    
    @staticmethod
    def enable_audit_logging():
        """Enable database audit logs"""
        return {
            'log_connections': True,
            'log_queries': True,
            'log_failed_auth': True
        }

if __name__ == "__main__":
    db_sec = DatabaseSecurity()
    print("✓ Database security configured")
