"""Webhook Implementation"""
import requests
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class WebhookManager:
    """Manage webhook subscriptions and deliveries"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.subscriptions: Dict[str, List[str]] = {}

    def subscribe(self, event_type: str, url: str) -> bool:
        """Subscribe a URL to an event type"""
        try:
            if event_type not in self.subscriptions:
                self.subscriptions[event_type] = []
            if url not in self.subscriptions[event_type]:
                self.subscriptions[event_type].append(url)
            return True
        except Exception as e:
            raise Exception(f"Failed to subscribe: {str(e)}")

    def unsubscribe(self, event_type: str, url: str) -> bool:
        """Unsubscribe a URL from an event type"""
        try:
            if event_type in self.subscriptions and url in self.subscriptions[event_type]:
                self.subscriptions[event_type].remove(url)
                return True
            return False
        except Exception as e:
            raise Exception(f"Failed to unsubscribe: {str(e)}")

    def generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for payload"""
        try:
            return hmac.new(
                self.secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            raise Exception(f"Failed to generate signature: {str(e)}")

    def send_webhook(self, event_type: str, data: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Send webhook to all subscribers"""
        if event_type not in self.subscriptions:
            return {'delivered': 0, 'failed': 0}

        payload = {
            'event': event_type,
            'data': data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        import json
        payload_str = json.dumps(payload)
        signature = self.generate_signature(payload_str)

        delivered = 0
        failed = 0
        errors = []

        for url in self.subscriptions[event_type]:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Webhook-Signature': signature,
                        'X-Webhook-Event': event_type
                    },
                    timeout=timeout
                )
                response.raise_for_status()
                delivered += 1
            except Exception as e:
                failed += 1
                errors.append({'url': url, 'error': str(e)})

        return {
            'delivered': delivered,
            'failed': failed,
            'errors': errors if errors else None
        }

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        try:
            expected_signature = self.generate_signature(payload)
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            raise Exception(f"Failed to verify webhook: {str(e)}")
