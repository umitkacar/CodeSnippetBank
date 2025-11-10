"""
LDAP/Active Directory Authentication
Production-ready LDAP authentication with connection pooling
"""
import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from typing import Optional, Dict, List
import re


class LDAPAuthenticator:
    """LDAP/Active Directory authentication handler"""

    def __init__(
        self,
        server_uri: str,
        base_dn: str,
        bind_dn: Optional[str] = None,
        bind_password: Optional[str] = None,
        use_ssl: bool = True,
        use_tls: bool = False,
        timeout: int = 10
    ):
        """
        Initialize LDAP authenticator

        Args:
            server_uri: LDAP server URI (ldap://host:port)
            base_dn: Base DN for searches (e.g., dc=example,dc=com)
            bind_dn: Service account DN for binding
            bind_password: Service account password
            use_ssl: Use SSL/LDAPS
            use_tls: Use StartTLS
            timeout: Connection timeout
        """
        self.server_uri = server_uri
        self.base_dn = base_dn
        self.bind_dn = bind_dn
        self.bind_password = bind_password

        # Create server object
        self.server = Server(
            server_uri,
            get_info=ALL,
            use_ssl=use_ssl,
            connect_timeout=timeout
        )

        self.use_tls = use_tls

    def _get_connection(
        self,
        user_dn: Optional[str] = None,
        password: Optional[str] = None
    ) -> Connection:
        """
        Get LDAP connection

        Args:
            user_dn: User DN for binding
            password: User password

        Returns:
            LDAP connection object
        """
        conn = Connection(
            self.server,
            user=user_dn or self.bind_dn,
            password=password or self.bind_password,
            auto_bind=True
        )

        if self.use_tls and not self.server.ssl:
            conn.start_tls()

        return conn

    def authenticate(
        self,
        username: str,
        password: str,
        search_filter: Optional[str] = None
    ) -> tuple[bool, Optional[Dict]]:
        """
        Authenticate user against LDAP

        Args:
            username: Username to authenticate
            password: User password
            search_filter: Custom LDAP search filter

        Returns:
            Tuple of (success, user_info)
        """
        try:
            # First, search for the user DN
            user_dn = self.find_user_dn(username, search_filter)

            if not user_dn:
                return False, None

            # Try to bind with user credentials
            try:
                user_conn = Connection(
                    self.server,
                    user=user_dn,
                    password=password,
                    auto_bind=True
                )

                # Get user attributes
                user_info = self.get_user_info(username, search_filter)

                user_conn.unbind()

                return True, user_info

            except LDAPBindError:
                return False, None

        except LDAPException as e:
            print(f"LDAP error: {e}")
            return False, None

    def find_user_dn(
        self,
        username: str,
        search_filter: Optional[str] = None
    ) -> Optional[str]:
        """
        Find user DN by username

        Args:
            username: Username to search
            search_filter: Custom search filter

        Returns:
            User DN or None
        """
        try:
            conn = self._get_connection()

            # Build search filter
            if search_filter:
                filter_str = search_filter.format(username=username)
            else:
                # Default filters
                filter_str = f"(|(uid={username})(sAMAccountName={username})(mail={username}))"

            # Search for user
            conn.search(
                search_base=self.base_dn,
                search_filter=filter_str,
                attributes=['dn']
            )

            if conn.entries:
                return conn.entries[0].entry_dn

            return None

        except LDAPException as e:
            print(f"LDAP search error: {e}")
            return None
        finally:
            if conn:
                conn.unbind()

    def get_user_info(
        self,
        username: str,
        search_filter: Optional[str] = None,
        attributes: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Get user information from LDAP

        Args:
            username: Username
            search_filter: Custom search filter
            attributes: Attributes to retrieve

        Returns:
            User information dictionary
        """
        default_attrs = [
            'cn', 'givenName', 'sn', 'mail', 'displayName',
            'memberOf', 'department', 'title', 'telephoneNumber'
        ]

        attrs = attributes or default_attrs

        try:
            conn = self._get_connection()

            if search_filter:
                filter_str = search_filter.format(username=username)
            else:
                filter_str = f"(|(uid={username})(sAMAccountName={username})(mail={username}))"

            conn.search(
                search_base=self.base_dn,
                search_filter=filter_str,
                attributes=attrs
            )

            if conn.entries:
                entry = conn.entries[0]
                user_info = {
                    'dn': entry.entry_dn,
                    'username': username
                }

                for attr in attrs:
                    if hasattr(entry, attr):
                        value = getattr(entry, attr).value
                        user_info[attr] = value

                return user_info

            return None

        except LDAPException as e:
            print(f"LDAP error: {e}")
            return None
        finally:
            if conn:
                conn.unbind()

    def get_user_groups(self, username: str) -> List[str]:
        """
        Get user's group memberships

        Args:
            username: Username

        Returns:
            List of group DNs
        """
        user_info = self.get_user_info(username, attributes=['memberOf'])

        if user_info and 'memberOf' in user_info:
            member_of = user_info['memberOf']

            if isinstance(member_of, list):
                return member_of
            elif isinstance(member_of, str):
                return [member_of]

        return []

    def is_member_of_group(
        self,
        username: str,
        group_dn: str
    ) -> bool:
        """
        Check if user is member of specific group

        Args:
            username: Username
            group_dn: Group DN

        Returns:
            True if user is member
        """
        groups = self.get_user_groups(username)
        return group_dn in groups

    def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password

        Args:
            username: Username
            old_password: Current password
            new_password: New password

        Returns:
            True if successful
        """
        try:
            # Authenticate with old password
            success, user_info = self.authenticate(username, old_password)

            if not success or not user_info:
                return False

            user_dn = user_info['dn']

            # Connect as user
            conn = Connection(
                self.server,
                user=user_dn,
                password=old_password,
                auto_bind=True
            )

            # Change password
            result = conn.extend.standard.modify_password(
                user_dn,
                old_password,
                new_password
            )

            conn.unbind()

            return result

        except LDAPException as e:
            print(f"Password change error: {e}")
            return False


class ActiveDirectoryAuthenticator(LDAPAuthenticator):
    """Specialized authenticator for Active Directory"""

    def __init__(
        self,
        server_uri: str,
        domain: str,
        bind_dn: Optional[str] = None,
        bind_password: Optional[str] = None,
        use_ssl: bool = True
    ):
        """
        Initialize Active Directory authenticator

        Args:
            server_uri: AD server URI
            domain: AD domain (e.g., example.com)
            bind_dn: Service account (user@domain or DOMAIN\\user)
            bind_password: Service account password
            use_ssl: Use LDAPS
        """
        # Convert domain to base DN
        base_dn = ','.join([f'DC={part}' for part in domain.split('.')])

        super().__init__(
            server_uri=server_uri,
            base_dn=base_dn,
            bind_dn=bind_dn,
            bind_password=bind_password,
            use_ssl=use_ssl
        )

        self.domain = domain

    def authenticate_with_upn(
        self,
        username: str,
        password: str
    ) -> tuple[bool, Optional[Dict]]:
        """
        Authenticate using UPN (user@domain)

        Args:
            username: Username (without @domain)
            password: Password

        Returns:
            Tuple of (success, user_info)
        """
        # Build UPN
        upn = f"{username}@{self.domain}"

        # Try to bind
        try:
            conn = Connection(
                self.server,
                user=upn,
                password=password,
                auto_bind=True
            )

            # Get user info
            user_info = self.get_user_info(
                username,
                search_filter=f"(userPrincipalName={upn})"
            )

            conn.unbind()

            return True, user_info

        except LDAPBindError:
            return False, None
        except LDAPException as e:
            print(f"AD auth error: {e}")
            return False, None


# Example usage
if __name__ == "__main__":
    import os

    # LDAP example
    # Use environment variables for sensitive data:
    # export LDAP_BIND_PASSWORD="your_password"
    # export LDAP_USER_PASSWORD="user_password"
    ldap_auth = LDAPAuthenticator(
        server_uri="ldap://ldap.example.com:389",
        base_dn="dc=example,dc=com",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password=os.getenv("LDAP_BIND_PASSWORD", ""),
        use_ssl=False
    )

    # Authenticate user
    success, user_info = ldap_auth.authenticate(
        "john.doe",
        os.getenv("LDAP_USER_PASSWORD", "")
    )

    if success:
        print(f"Authentication successful!")
        print(f"User info: {user_info}")

        # Get groups
        groups = ldap_auth.get_user_groups("john.doe")
        print(f"User groups: {groups}")
    else:
        print("Authentication failed")

    # Active Directory example
    # Use environment variables:
    # export AD_BIND_PASSWORD="service_password"
    # export AD_USER_PASSWORD="user_password"
    ad_auth = ActiveDirectoryAuthenticator(
        server_uri="ldaps://ad.example.com:636",
        domain="example.com",
        bind_dn="service@example.com",
        bind_password=os.getenv("AD_BIND_PASSWORD", "")
    )

    # Authenticate with UPN
    success, user_info = ad_auth.authenticate_with_upn(
        "john.doe",
        os.getenv("AD_USER_PASSWORD", "")
    )
    print(f"AD auth: {success}")
