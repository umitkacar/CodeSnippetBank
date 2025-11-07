"""
OAuth2 Device Authorization Flow
Production-ready device flow for TV/IoT devices without browsers
"""
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import requests
from dataclasses import dataclass


@dataclass
class DeviceCode:
    """Device code data"""
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class OAuth2DeviceFlow:
    """OAuth2 Device Authorization Flow Implementation"""

    def __init__(
        self,
        device_authorization_url: str,
        token_url: str,
        client_id: str,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None
    ):
        """
        Initialize OAuth2 Device Flow

        Args:
            device_authorization_url: Device authorization endpoint
            token_url: Token endpoint
            client_id: Client ID
            client_secret: Optional client secret
            scope: Optional scope
        """
        self.device_authorization_url = device_authorization_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

    def request_device_code(self) -> Optional[DeviceCode]:
        """
        Request device and user codes

        Returns:
            DeviceCode object or None if failed
        """
        data = {
            'client_id': self.client_id
        }

        if self.scope:
            data['scope'] = self.scope

        try:
            response = requests.post(
                self.device_authorization_url,
                data=data,
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            return DeviceCode(
                device_code=result['device_code'],
                user_code=result['user_code'],
                verification_uri=result['verification_uri'],
                verification_uri_complete=result.get(
                    'verification_uri_complete',
                    result['verification_uri']
                ),
                expires_in=result['expires_in'],
                interval=result.get('interval', 5)
            )

        except requests.exceptions.RequestException as e:
            print(f"Device code request failed: {e}")
            return None

    def poll_for_token(
        self,
        device_code: str,
        interval: int = 5,
        timeout: int = 300
    ) -> Optional[Dict]:
        """
        Poll token endpoint for authorization

        Args:
            device_code: Device code from device authorization
            interval: Polling interval in seconds
            timeout: Maximum time to poll in seconds

        Returns:
            Token response or None
        """
        data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': device_code,
            'client_id': self.client_id
        }

        if self.client_secret:
            data['client_secret'] = self.client_secret

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.post(
                    self.token_url,
                    data=data,
                    timeout=10
                )

                # Check for successful response
                if response.status_code == 200:
                    return response.json()

                # Handle authorization pending
                result = response.json()
                error = result.get('error')

                if error == 'authorization_pending':
                    # Continue polling
                    time.sleep(interval)
                    continue

                elif error == 'slow_down':
                    # Increase interval
                    interval += 5
                    time.sleep(interval)
                    continue

                elif error == 'expired_token':
                    print("Device code expired")
                    return None

                elif error == 'access_denied':
                    print("User denied authorization")
                    return None

                else:
                    print(f"Token request error: {error}")
                    return None

            except requests.exceptions.RequestException as e:
                print(f"Polling error: {e}")
                time.sleep(interval)
                continue

        print("Polling timeout")
        return None

    def authorize_device(self) -> Optional[Dict]:
        """
        Complete device flow authorization

        Returns:
            Token response or None
        """
        # Step 1: Request device code
        device_code_data = self.request_device_code()

        if not device_code_data:
            return None

        # Display instructions to user
        print("\n" + "="*60)
        print("DEVICE AUTHORIZATION")
        print("="*60)
        print(f"\nVisit: {device_code_data.verification_uri}")
        print(f"Enter code: {device_code_data.user_code}")
        print(f"\nOr scan QR code / visit: {device_code_data.verification_uri_complete}")
        print(f"\nWaiting for authorization...")
        print("="*60 + "\n")

        # Step 2: Poll for token
        tokens = self.poll_for_token(
            device_code_data.device_code,
            device_code_data.interval,
            device_code_data.expires_in
        )

        if tokens:
            print("✓ Authorization successful!")

        return tokens


class DeviceCodeServer:
    """Server-side device code management"""

    def __init__(self):
        self.device_codes: Dict[str, Dict] = {}
        self.user_codes: Dict[str, str] = {}

    def generate_codes(
        self,
        client_id: str,
        scope: Optional[str] = None
    ) -> DeviceCode:
        """
        Generate device and user codes

        Args:
            client_id: Client ID
            scope: Requested scope

        Returns:
            DeviceCode object
        """
        # Generate device code (long, secure)
        device_code = secrets.token_urlsafe(32)

        # Generate user code (short, readable)
        # Format: ABCD-EFGH
        user_code = self._generate_user_code()

        # Store device code
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        self.device_codes[device_code] = {
            'client_id': client_id,
            'user_code': user_code,
            'scope': scope,
            'expires_at': expires_at.isoformat(),
            'authorized': False,
            'user_id': None
        }

        # Map user code to device code
        self.user_codes[user_code] = device_code

        return DeviceCode(
            device_code=device_code,
            user_code=user_code,
            verification_uri="https://example.com/device",
            verification_uri_complete=f"https://example.com/device?user_code={user_code}",
            expires_in=900,  # 15 minutes
            interval=5
        )

    def _generate_user_code(self) -> str:
        """Generate readable user code"""
        # Use only easily readable characters
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        code = ''.join(secrets.choice(chars) for _ in range(8))
        return f"{code[:4]}-{code[4:]}"

    def authorize_device(
        self,
        user_code: str,
        user_id: int
    ) -> bool:
        """
        Authorize device using user code

        Args:
            user_code: User code from display
            user_id: User ID authorizing the device

        Returns:
            True if authorized
        """
        device_code = self.user_codes.get(user_code)

        if not device_code:
            return False

        device_data = self.device_codes.get(device_code)

        if not device_data:
            return False

        # Check expiration
        expires_at = datetime.fromisoformat(device_data['expires_at'])
        if datetime.utcnow() > expires_at:
            return False

        # Authorize
        device_data['authorized'] = True
        device_data['user_id'] = user_id

        return True

    def check_device_authorization(
        self,
        device_code: str
    ) -> Optional[Dict]:
        """
        Check if device is authorized

        Args:
            device_code: Device code

        Returns:
            Authorization data or None
        """
        device_data = self.device_codes.get(device_code)

        if not device_data:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(device_data['expires_at'])
        if datetime.utcnow() > expires_at:
            return None

        if not device_data['authorized']:
            return {'status': 'pending'}

        return {
            'status': 'authorized',
            'user_id': device_data['user_id'],
            'scope': device_data['scope']
        }


# Example usage
if __name__ == "__main__":
    # Client side example
    print("OAuth2 Device Flow Example\n")

    # Note: Replace with actual endpoints
    device_flow = OAuth2DeviceFlow(
        device_authorization_url="https://oauth.example.com/device/code",
        token_url="https://oauth.example.com/token",
        client_id="your_client_id",
        scope="openid profile email"
    )

    # This would normally poll and wait for user authorization
    # tokens = device_flow.authorize_device()

    # Server side example
    print("\nServer Side Example:")
    server = DeviceCodeServer()

    # Generate codes
    codes = server.generate_codes("client_123", "read write")

    print(f"Device Code: {codes.device_code}")
    print(f"User Code: {codes.user_code}")
    print(f"Verification URI: {codes.verification_uri}")
    print(f"Expires in: {codes.expires_in} seconds")

    # Simulate user authorization
    success = server.authorize_device(codes.user_code, user_id=123)
    print(f"\nAuthorization: {success}")

    # Check authorization status
    status = server.check_device_authorization(codes.device_code)
    print(f"Status: {status}")
