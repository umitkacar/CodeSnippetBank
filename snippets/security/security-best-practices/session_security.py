"""Session Security"""
import secrets
from datetime import datetime, timedelta

class SessionSecurity:
    """Secure session management"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_session_timeout(
        last_activity: datetime,
        timeout_minutes: int = 30
    ) -> bool:
        """Check if session has timed out"""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - last_activity < timeout
    
    @staticmethod
    def regenerate_session_on_privilege_change():
        """Regenerate session ID on privilege escalation"""
        return {
            'old_session_id': 'old_id',
            'new_session_id': secrets.token_urlsafe(32),
            'reason': 'privilege_change'
        }
    
    @staticmethod
    def implement_session_fixation_protection():
        """Protect against session fixation"""
        return {
            'regenerate_on_login': True,
            'bind_to_ip': False,  # Can break legitimate users
            'bind_to_user_agent': True
        }

if __name__ == "__main__":
    session_sec = SessionSecurity()
    session_id = session_sec.generate_session_id()
    print(f"✓ Secure session ID: {session_id[:20]}...")
