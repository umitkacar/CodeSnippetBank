"""
Single Sign-On (SSO) Implementation
Production-ready SSO with SAML 2.0 support
"""
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from typing import Dict, Optional, List
import json


class SAMLSSOProvider:
    """SAML 2.0 SSO Provider Implementation"""

    def __init__(self, saml_settings: Dict):
        """
        Initialize SAML SSO Provider

        Args:
            saml_settings: SAML configuration dictionary
        """
        self.saml_settings = saml_settings

    def prepare_saml_request(self, request_data: Dict) -> Dict:
        """
        Prepare SAML authentication request

        Args:
            request_data: HTTP request data

        Returns:
            SAML request dictionary
        """
        return {
            'https': 'on' if request_data.get('https') else 'off',
            'http_host': request_data.get('http_host'),
            'script_name': request_data.get('script_name'),
            'server_port': request_data.get('server_port'),
            'get_data': request_data.get('get_data', {}),
            'post_data': request_data.get('post_data', {})
        }

    def initiate_sso(self, request_data: Dict) -> str:
        """
        Initiate SSO authentication

        Args:
            request_data: HTTP request data

        Returns:
            SSO redirect URL
        """
        req = self.prepare_saml_request(request_data)
        auth = OneLogin_Saml2_Auth(req, self.saml_settings)

        # Generate SSO URL
        sso_url = auth.login()
        return sso_url

    def process_saml_response(
        self,
        request_data: Dict
    ) -> Optional[Dict]:
        """
        Process SAML response after authentication

        Args:
            request_data: HTTP request data with SAML response

        Returns:
            User attributes if successful, None otherwise
        """
        req = self.prepare_saml_request(request_data)
        auth = OneLogin_Saml2_Auth(req, self.saml_settings)

        # Process the SAML response
        auth.process_response()

        errors = auth.get_errors()

        if errors:
            print(f"SAML Errors: {errors}")
            print(f"Error Reason: {auth.get_last_error_reason()}")
            return None

        if not auth.is_authenticated():
            return None

        # Get user attributes
        attributes = auth.get_attributes()
        name_id = auth.get_nameid()
        session_index = auth.get_session_index()

        return {
            'name_id': name_id,
            'session_index': session_index,
            'attributes': attributes,
            'email': attributes.get('email', [None])[0],
            'username': attributes.get('username', [None])[0],
            'first_name': attributes.get('first_name', [None])[0],
            'last_name': attributes.get('last_name', [None])[0],
            'groups': attributes.get('groups', [])
        }

    def initiate_slo(
        self,
        request_data: Dict,
        name_id: str,
        session_index: Optional[str] = None
    ) -> str:
        """
        Initiate Single Logout

        Args:
            request_data: HTTP request data
            name_id: User's SAML NameID
            session_index: Session index from login

        Returns:
            SLO redirect URL
        """
        req = self.prepare_saml_request(request_data)
        auth = OneLogin_Saml2_Auth(req, self.saml_settings)

        slo_url = auth.logout(
            name_id=name_id,
            session_index=session_index
        )
        return slo_url

    def process_slo(self, request_data: Dict) -> bool:
        """
        Process Single Logout response

        Args:
            request_data: HTTP request data with SLO response

        Returns:
            True if logout successful
        """
        req = self.prepare_saml_request(request_data)
        auth = OneLogin_Saml2_Auth(req, self.saml_settings)

        auth.process_slo()

        errors = auth.get_errors()

        if errors:
            print(f"SLO Errors: {errors}")
            return False

        return True

    def get_metadata(self) -> str:
        """
        Get SP metadata XML

        Returns:
            SAML metadata XML string
        """
        settings = OneLogin_Saml2_Settings(
            settings=self.saml_settings,
            sp_validation_only=True
        )
        metadata = settings.get_sp_metadata()
        errors = settings.validate_metadata(metadata)

        if errors:
            raise Exception(f"Invalid metadata: {errors}")

        return metadata


class OIDCSSOProvider:
    """OpenID Connect SSO Provider"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        discovery_url: str,
        redirect_uri: str
    ):
        """
        Initialize OIDC SSO Provider

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            discovery_url: OIDC discovery endpoint
            redirect_uri: Redirect URI after authentication
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.discovery_url = discovery_url
        self.redirect_uri = redirect_uri
        self._provider_config = None

    def get_provider_config(self) -> Dict:
        """
        Fetch OIDC provider configuration

        Returns:
            Provider configuration dictionary
        """
        if self._provider_config:
            return self._provider_config

        import requests

        try:
            response = requests.get(self.discovery_url, timeout=10)
            response.raise_for_status()
            self._provider_config = response.json()
            return self._provider_config
        except Exception as e:
            raise Exception(f"Failed to fetch OIDC config: {e}")

    def get_authorization_url(
        self,
        state: str,
        nonce: str,
        scopes: Optional[List[str]] = None
    ) -> str:
        """
        Get authorization URL for SSO

        Args:
            state: State parameter for CSRF protection
            nonce: Nonce for token validation
            scopes: OAuth scopes

        Returns:
            Authorization URL
        """
        from urllib.parse import urlencode

        config = self.get_provider_config()
        auth_endpoint = config['authorization_endpoint']

        scopes = scopes or ['openid', 'profile', 'email']

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
            'nonce': nonce
        }

        return f"{auth_endpoint}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Optional[Dict]:
        """
        Exchange authorization code for tokens

        Args:
            code: Authorization code

        Returns:
            Token response dictionary
        """
        import requests

        config = self.get_provider_config()
        token_endpoint = config['token_endpoint']

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        try:
            response = requests.post(token_endpoint, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Token exchange failed: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """
        Get user information

        Args:
            access_token: Access token

        Returns:
            User info dictionary
        """
        import requests

        config = self.get_provider_config()
        userinfo_endpoint = config['userinfo_endpoint']

        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                userinfo_endpoint,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get user info: {e}")
            return None


# Example SAML settings
EXAMPLE_SAML_SETTINGS = {
    "strict": True,
    "debug": False,
    "sp": {
        "entityId": "https://your-app.com/metadata/",
        "assertionConsumerService": {
            "url": "https://your-app.com/sso/acs/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "https://your-app.com/sso/sls/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    },
    "idp": {
        "entityId": "https://idp.example.com/metadata/",
        "singleSignOnService": {
            "url": "https://idp.example.com/sso/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": "https://idp.example.com/slo/",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "<IDP_CERTIFICATE>"
    }
}


# Example usage
if __name__ == "__main__":
    # OIDC SSO Example
    oidc_provider = OIDCSSOProvider(
        client_id="your_client_id",
        client_secret="your_client_secret",
        discovery_url="https://idp.example.com/.well-known/openid-configuration",
        redirect_uri="https://your-app.com/callback"
    )

    # Get authorization URL
    import secrets
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    auth_url = oidc_provider.get_authorization_url(state, nonce)
    print(f"OIDC Authorization URL: {auth_url}")
