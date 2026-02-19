"""
Card payment integration service (Uzcard/Humo via aggregators).
This is a generic service that can work with different card payment aggregators.
"""

import hashlib
import hmac
import time
from typing import Dict, Optional

import requests
from flask import current_app


class CardService:
    """Service for card payment integration (Uzcard/Humo)."""

    # This can be configured to use different aggregators:
    # - Apelsin (https://apelsin.uz/)
    # - Payze (https://payze.io/)
    # - Octo (https://octo.uz/)
    # etc.

    @staticmethod
    def generate_signature(data: str, secret_key: str) -> str:
        """
        Generate HMAC-SHA256 signature.

        Args:
            data: Data to sign
            secret_key: Secret key

        Returns:
            Hex digest of signature
        """
        return hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def prepare_payment(
        cls,
        amount: int,
        order_id: str,
        description: str = "",
        return_url: str = "",
        fail_url: str = "",
    ) -> Dict:
        """
        Prepare card payment and get payment URL.

        This is a generic implementation. Specific aggregator integration
        should be implemented based on chosen provider.

        Args:
            amount: Amount in sum
            order_id: Unique order ID
            description: Payment description
            return_url: Success return URL
            fail_url: Failure return URL

        Returns:
            dict with payment_url and transaction_id
        """
        merchant_id = current_app.config.get("CARD_MERCHANT_ID")
        secret_key = current_app.config.get("CARD_SECRET_KEY")
        api_url = current_app.config.get("CARD_API_URL")

        if not all([merchant_id, secret_key, api_url]):
            raise ValueError("Card payment credentials not configured")

        # Build payment request
        # This is a generic example - adjust based on your aggregator
        payment_data = {
            "merchant_id": merchant_id,
            "order_id": order_id,
            "amount": amount,
            "currency": "UZS",
            "description": description,
            "return_url": return_url,
            "fail_url": fail_url,
            "timestamp": int(time.time()),
        }

        # Generate signature
        sign_string = f"{merchant_id}{order_id}{amount}{payment_data['timestamp']}"
        signature = cls.generate_signature(sign_string, secret_key)
        payment_data["signature"] = signature

        try:
            # Create payment via API
            response = requests.post(
                f"{api_url}/payment/create",
                json=payment_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            return {
                "payment_url": result.get("payment_url"),
                "transaction_id": result.get("transaction_id"),
                "amount": amount,
            }

        except requests.RequestException as e:
            raise ValueError(f"Failed to create payment: {str(e)}")

    @classmethod
    def verify_callback(cls, data: Dict) -> Dict:
        """
        Verify and process card payment callback.

        Args:
            data: Callback data from payment gateway

        Returns:
            Verified transaction data
        """
        secret_key = current_app.config.get("CARD_SECRET_KEY")

        transaction_id = data.get("transaction_id")
        order_id = data.get("order_id")
        amount = data.get("amount")
        status = data.get("status")
        signature = data.get("signature")

        # Verify signature
        sign_string = f"{transaction_id}{order_id}{amount}{status}"
        expected_signature = cls.generate_signature(sign_string, secret_key)

        if signature != expected_signature:
            return {
                "valid": False,
                "error": "Invalid signature",
            }

        return {
            "valid": True,
            "transaction_id": transaction_id,
            "order_id": order_id,
            "amount": amount,
            "status": status,
        }

    @classmethod
    def check_status(cls, transaction_id: str) -> Optional[Dict]:
        """
        Check payment status via API.

        Args:
            transaction_id: Transaction ID

        Returns:
            Payment status dict or None
        """
        merchant_id = current_app.config.get("CARD_MERCHANT_ID")
        secret_key = current_app.config.get("CARD_SECRET_KEY")
        api_url = current_app.config.get("CARD_API_URL")

        if not all([merchant_id, secret_key, api_url]):
            return None

        # Build status check request
        timestamp = int(time.time())
        sign_string = f"{merchant_id}{transaction_id}{timestamp}"
        signature = cls.generate_signature(sign_string, secret_key)

        try:
            response = requests.post(
                f"{api_url}/payment/status",
                json={
                    "merchant_id": merchant_id,
                    "transaction_id": transaction_id,
                    "timestamp": timestamp,
                    "signature": signature,
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            return None

    @classmethod
    def refund_payment(cls, transaction_id: str, amount: Optional[int] = None) -> Dict:
        """
        Refund a payment (full or partial).

        Args:
            transaction_id: Original transaction ID
            amount: Refund amount (None for full refund)

        Returns:
            Refund result dict
        """
        merchant_id = current_app.config.get("CARD_MERCHANT_ID")
        secret_key = current_app.config.get("CARD_SECRET_KEY")
        api_url = current_app.config.get("CARD_API_URL")

        if not all([merchant_id, secret_key, api_url]):
            raise ValueError("Card payment credentials not configured")

        timestamp = int(time.time())
        sign_string = f"{merchant_id}{transaction_id}{amount or ''}{timestamp}"
        signature = cls.generate_signature(sign_string, secret_key)

        refund_data = {
            "merchant_id": merchant_id,
            "transaction_id": transaction_id,
            "timestamp": timestamp,
            "signature": signature,
        }

        if amount:
            refund_data["amount"] = amount

        try:
            response = requests.post(
                f"{api_url}/payment/refund",
                json=refund_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise ValueError(f"Failed to refund payment: {str(e)}")
