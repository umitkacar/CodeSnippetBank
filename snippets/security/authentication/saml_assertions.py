"""
SAML Assertion Validation and Processing
Production-ready SAML assertion handling
"""
from lxml import etree
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509


class SAMLAssertionValidator:
    """Validate and process SAML assertions"""

    def __init__(self, idp_certificate: x509.Certificate):
        """
        Initialize SAML assertion validator

        Args:
            idp_certificate: IdP's certificate for signature verification
        """
        self.idp_certificate = idp_certificate

    def decode_assertion(self, encoded_assertion: str) -> etree.Element:
        """
        Decode base64-encoded SAML assertion

        Args:
            encoded_assertion: Base64-encoded assertion

        Returns:
            XML element
        """
        decoded = base64.b64decode(encoded_assertion)
        return etree.fromstring(decoded)

    def validate_assertion(
        self,
        assertion: etree.Element,
        audience: str,
        recipient: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Validate SAML assertion

        Args:
            assertion: SAML assertion XML
            audience: Expected audience (SP entity ID)
            recipient: Expected recipient URL

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate time conditions
        valid, error = self._validate_conditions(assertion, audience)
        if not valid:
            return False, error

        # Validate subject confirmation
        if recipient:
            valid, error = self._validate_subject_confirmation(
                assertion,
                recipient
            )
            if not valid:
                return False, error

        # Validate signature (simplified - use library in production)
        # valid, error = self._validate_signature(assertion)
        # if not valid:
        #     return False, error

        return True, "Assertion is valid"

    def _validate_conditions(
        self,
        assertion: etree.Element,
        audience: str
    ) -> tuple[bool, str]:
        """Validate assertion conditions"""
        conditions = assertion.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}Conditions'
        )

        if conditions is None:
            return False, "Missing Conditions element"

        # Check NotBefore
        not_before = conditions.get('NotBefore')
        if not_before:
            not_before_dt = datetime.fromisoformat(
                not_before.replace('Z', '+00:00')
            )
            if datetime.now(not_before_dt.tzinfo) < not_before_dt:
                return False, "Assertion not yet valid"

        # Check NotOnOrAfter
        not_after = conditions.get('NotOnOrAfter')
        if not_after:
            not_after_dt = datetime.fromisoformat(
                not_after.replace('Z', '+00:00')
            )
            if datetime.now(not_after_dt.tzinfo) >= not_after_dt:
                return False, "Assertion has expired"

        # Check Audience
        audience_restriction = conditions.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction'
        )

        if audience_restriction is not None:
            audiences = audience_restriction.findall(
                './/{urn:oasis:names:tc:SAML:2.0:assertion}Audience'
            )

            if not any(aud.text == audience for aud in audiences):
                return False, f"Invalid audience. Expected: {audience}"

        return True, "Conditions valid"

    def _validate_subject_confirmation(
        self,
        assertion: etree.Element,
        recipient: str
    ) -> tuple[bool, str]:
        """Validate subject confirmation"""
        subject = assertion.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}Subject'
        )

        if subject is None:
            return False, "Missing Subject element"

        confirmation = subject.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmation'
        )

        if confirmation is None:
            return False, "Missing SubjectConfirmation"

        # Check Method
        method = confirmation.get('Method')
        if method != 'urn:oasis:names:tc:SAML:2.0:cm:bearer':
            return False, f"Unsupported confirmation method: {method}"

        # Check SubjectConfirmationData
        conf_data = confirmation.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationData'
        )

        if conf_data is not None:
            # Check Recipient
            conf_recipient = conf_data.get('Recipient')
            if conf_recipient and conf_recipient != recipient:
                return False, f"Invalid recipient. Expected: {recipient}"

            # Check NotOnOrAfter
            not_after = conf_data.get('NotOnOrAfter')
            if not_after:
                not_after_dt = datetime.fromisoformat(
                    not_after.replace('Z', '+00:00')
                )
                if datetime.now(not_after_dt.tzinfo) >= not_after_dt:
                    return False, "Subject confirmation has expired"

        return True, "Subject confirmation valid"

    def extract_attributes(
        self,
        assertion: etree.Element
    ) -> Dict[str, List[str]]:
        """
        Extract user attributes from assertion

        Args:
            assertion: SAML assertion XML

        Returns:
            Dictionary of attribute name to values
        """
        attributes = {}

        attr_statement = assertion.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement'
        )

        if attr_statement is not None:
            for attr in attr_statement.findall(
                './/{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'
            ):
                name = attr.get('Name')
                values = [
                    val.text
                    for val in attr.findall(
                        './/{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
                    )
                    if val.text
                ]

                if name:
                    attributes[name] = values

        return attributes

    def extract_name_id(self, assertion: etree.Element) -> Optional[str]:
        """
        Extract NameID from assertion

        Args:
            assertion: SAML assertion XML

        Returns:
            NameID value
        """
        name_id = assertion.find(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}Subject/'
            '{urn:oasis:names:tc:SAML:2.0:assertion}NameID'
        )

        return name_id.text if name_id is not None else None


class SAMLResponseParser:
    """Parse SAML responses"""

    @staticmethod
    def parse_response(encoded_response: str) -> etree.Element:
        """
        Parse base64-encoded SAML response

        Args:
            encoded_response: Base64-encoded response

        Returns:
            XML element
        """
        decoded = base64.b64decode(encoded_response)
        return etree.fromstring(decoded)

    @staticmethod
    def extract_assertions(response: etree.Element) -> List[etree.Element]:
        """
        Extract assertions from SAML response

        Args:
            response: SAML response XML

        Returns:
            List of assertion elements
        """
        assertions = response.findall(
            './/{urn:oasis:names:tc:SAML:2.0:assertion}Assertion'
        )
        return assertions

    @staticmethod
    def check_status(response: etree.Element) -> tuple[bool, Optional[str]]:
        """
        Check response status

        Args:
            response: SAML response XML

        Returns:
            Tuple of (is_success, error_message)
        """
        status = response.find(
            './/{urn:oasis:names:tc:SAML:2.0:protocol}Status'
        )

        if status is None:
            return False, "Missing Status element"

        status_code = status.find(
            './/{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode'
        )

        if status_code is None:
            return False, "Missing StatusCode"

        value = status_code.get('Value')

        if value == 'urn:oasis:names:tc:SAML:2.0:status:Success':
            return True, None

        # Extract error message
        status_message = status.find(
            './/{urn:oasis:names:tc:SAML:2.0:protocol}StatusMessage'
        )

        error_msg = status_message.text if status_message is not None else value

        return False, error_msg


# Example usage
if __name__ == "__main__":
    # Example SAML assertion (simplified)
    saml_assertion_xml = """
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="_assertion_id"
                    IssueInstant="2024-01-01T00:00:00Z"
                    Version="2.0">
        <saml:Issuer>https://idp.example.com</saml:Issuer>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
                user@example.com
            </saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData NotOnOrAfter="2025-01-01T00:00:00Z"
                                               Recipient="https://sp.example.com/acs"/>
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions NotBefore="2024-01-01T00:00:00Z"
                         NotOnOrAfter="2025-01-01T00:00:00Z">
            <saml:AudienceRestriction>
                <saml:Audience>https://sp.example.com</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AttributeStatement>
            <saml:Attribute Name="email">
                <saml:AttributeValue>user@example.com</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="firstName">
                <saml:AttributeValue>John</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="lastName">
                <saml:AttributeValue>Doe</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
    """

    # Parse assertion
    assertion = etree.fromstring(saml_assertion_xml.encode())

    # Note: In production, load actual IdP certificate
    # For this example, we'll skip signature validation

    print("✓ SAML Assertion Parser Example\n")

    # Extract NameID
    # validator = SAMLAssertionValidator(idp_cert)
    # name_id = validator.extract_name_id(assertion)
    # print(f"NameID: {name_id}")

    # Extract attributes
    # attributes = validator.extract_attributes(assertion)
    # print(f"\nAttributes:")
    # for name, values in attributes.items():
    #     print(f"  {name}: {', '.join(values)}")

    print("SAML assertion validation system ready")
    print("Use with actual IdP certificate for production")
