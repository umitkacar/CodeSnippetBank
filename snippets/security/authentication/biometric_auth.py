"""
Biometric Authentication (WebAuthn/FIDO2)
Production-ready biometric authentication using WebAuthn standard
"""
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from typing import List, Dict, Optional
import secrets
import json


class BiometricAuthenticator:
    """WebAuthn/FIDO2 Biometric Authentication"""

    def __init__(
        self,
        rp_id: str,
        rp_name: str,
        origin: str
    ):
        """
        Initialize biometric authenticator

        Args:
            rp_id: Relying Party ID (domain)
            rp_name: Relying Party name
            origin: Expected origin (https://example.com)
        """
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = origin

    def generate_registration_challenge(
        self,
        user_id: str,
        username: str,
        display_name: str,
        existing_credentials: Optional[List[bytes]] = None
    ) -> Dict:
        """
        Generate registration challenge for new credential

        Args:
            user_id: Unique user identifier
            username: Username (email)
            display_name: User's display name
            existing_credentials: List of existing credential IDs to exclude

        Returns:
            Registration options dictionary
        """
        # Convert existing credentials to proper format
        exclude_credentials = []
        if existing_credentials:
            exclude_credentials = [
                PublicKeyCredentialDescriptor(id=cred_id)
                for cred_id in existing_credentials
            ]

        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id.encode('utf-8'),
            user_name=username,
            user_display_name=display_name,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            timeout=60000,  # 60 seconds
        )

        return json.loads(options_to_json(options))

    def verify_registration(
        self,
        credential: Dict,
        expected_challenge: bytes,
        expected_origin: Optional[str] = None
    ) -> Dict:
        """
        Verify registration response

        Args:
            credential: Registration credential from client
            expected_challenge: Expected challenge bytes
            expected_origin: Expected origin (defaults to self.origin)

        Returns:
            Verification result with credential data
        """
        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=expected_challenge,
                expected_rp_id=self.rp_id,
                expected_origin=expected_origin or self.origin
            )

            return {
                'verified': True,
                'credential_id': verification.credential_id,
                'credential_public_key': verification.credential_public_key,
                'sign_count': verification.sign_count,
                'aaguid': verification.aaguid
            }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }

    def generate_authentication_challenge(
        self,
        allowed_credentials: List[bytes]
    ) -> Dict:
        """
        Generate authentication challenge

        Args:
            allowed_credentials: List of allowed credential IDs

        Returns:
            Authentication options dictionary
        """
        allow_credentials = [
            PublicKeyCredentialDescriptor(id=cred_id)
            for cred_id in allowed_credentials
        ]

        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
            timeout=60000
        )

        return json.loads(options_to_json(options))

    def verify_authentication(
        self,
        credential: Dict,
        expected_challenge: bytes,
        credential_public_key: bytes,
        credential_current_sign_count: int,
        expected_origin: Optional[str] = None
    ) -> Dict:
        """
        Verify authentication response

        Args:
            credential: Authentication credential from client
            expected_challenge: Expected challenge bytes
            credential_public_key: Stored public key
            credential_current_sign_count: Current sign count
            expected_origin: Expected origin

        Returns:
            Verification result
        """
        try:
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=expected_challenge,
                expected_rp_id=self.rp_id,
                expected_origin=expected_origin or self.origin,
                credential_public_key=credential_public_key,
                credential_current_sign_count=credential_current_sign_count
            )

            return {
                'verified': True,
                'new_sign_count': verification.new_sign_count
            }

        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }


class BiometricCredentialStore:
    """Store for biometric credentials"""

    def __init__(self):
        self.credentials: Dict[str, List[Dict]] = {}
        self.challenges: Dict[str, bytes] = {}

    def store_credential(
        self,
        user_id: str,
        credential_id: bytes,
        public_key: bytes,
        sign_count: int,
        device_name: Optional[str] = None
    ) -> None:
        """
        Store a biometric credential

        Args:
            user_id: User identifier
            credential_id: Credential ID
            public_key: Public key
            sign_count: Initial sign count
            device_name: Optional device name
        """
        if user_id not in self.credentials:
            self.credentials[user_id] = []

        self.credentials[user_id].append({
            'credential_id': credential_id,
            'public_key': public_key,
            'sign_count': sign_count,
            'device_name': device_name,
            'created_at': secrets.token_urlsafe(16)
        })

    def get_credentials(self, user_id: str) -> List[Dict]:
        """Get all credentials for a user"""
        return self.credentials.get(user_id, [])

    def get_credential(
        self,
        user_id: str,
        credential_id: bytes
    ) -> Optional[Dict]:
        """Get specific credential"""
        user_credentials = self.get_credentials(user_id)

        for cred in user_credentials:
            if cred['credential_id'] == credential_id:
                return cred

        return None

    def update_sign_count(
        self,
        user_id: str,
        credential_id: bytes,
        new_sign_count: int
    ) -> bool:
        """Update sign count after authentication"""
        credential = self.get_credential(user_id, credential_id)

        if credential:
            credential['sign_count'] = new_sign_count
            return True

        return False

    def remove_credential(
        self,
        user_id: str,
        credential_id: bytes
    ) -> bool:
        """Remove a credential"""
        if user_id in self.credentials:
            self.credentials[user_id] = [
                c for c in self.credentials[user_id]
                if c['credential_id'] != credential_id
            ]
            return True

        return False

    def store_challenge(self, user_id: str, challenge: bytes) -> None:
        """Store challenge for verification"""
        self.challenges[user_id] = challenge

    def get_challenge(self, user_id: str) -> Optional[bytes]:
        """Get stored challenge"""
        return self.challenges.get(user_id)

    def clear_challenge(self, user_id: str) -> None:
        """Clear challenge after use"""
        if user_id in self.challenges:
            del self.challenges[user_id]


# Example usage
if __name__ == "__main__":
    # Initialize authenticator
    authenticator = BiometricAuthenticator(
        rp_id="example.com",
        rp_name="Example App",
        origin="https://example.com"
    )

    # Initialize credential store
    store = BiometricCredentialStore()

    # Registration flow
    user_id = "user_123"
    username = "john@example.com"
    display_name = "John Doe"

    # 1. Generate registration challenge
    reg_options = authenticator.generate_registration_challenge(
        user_id=user_id,
        username=username,
        display_name=display_name
    )

    print("Registration Options:")
    print(f"Challenge: {reg_options['challenge'][:50]}...")
    print(f"User ID: {reg_options['user']['id']}")

    # Store challenge
    # challenge_bytes = base64.urlsafe_b64decode(reg_options['challenge'])
    # store.store_challenge(user_id, challenge_bytes)

    # 2. Client creates credential and sends back
    # verification = authenticator.verify_registration(credential, challenge)

    # 3. Store credential
    # if verification['verified']:
    #     store.store_credential(
    #         user_id,
    #         verification['credential_id'],
    #         verification['credential_public_key'],
    #         verification['sign_count']
    #     )

    print("\n✓ Biometric authentication system initialized")
