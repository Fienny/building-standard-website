"""
Click payment integration service.
Docs: https://docs.click.uz/
"""

import hashlib
import hmac
import time
from typing import Dict, Optional

import requests
from flask import current_app


class ClickService:
    """Service for Click payment system integration."""

    BASE_URL = "https://api.click.uz/v2"

    @staticmethod
    def generate_signature(params: Dict, secret_key: str) -> str:
        """
        Generate HMAC-SHA1 signature for Click request.

        Args:
            params: Request parameters
            secret_key: Merchant secret key

        Returns:
            Hex digest of signature
        """
        # Sort params by key and concatenate values
        sorted_params = sorted(params.items())
        sign_string = "".join(str(v) for k, v in sorted_params)
        sign_string += secret_key

        return hashlib.sha1(sign_string.encode()).hexdigest()

    @classmethod
    def prepare_payment(
        cls,
        amount: int,
        merchant_trans_id: str,
        return_url: str,
        description: str = "",
    ) -> Dict:
        """
        Prepare Click payment and get payment URL.

        Args:
            amount: Amount in tiyin (1 sum = 100 tiyin)
            merchant_trans_id: Unique transaction ID from merchant
            return_url: URL to redirect after payment
            description: Payment description

        Returns:
            dict with payment_url and transaction_id
        """
        merchant_id = current_app.config.get("CLICK_MERCHANT_ID")
        service_id = current_app.config.get("CLICK_SERVICE_ID")
        secret_key = current_app.config.get("CLICK_SECRET_KEY")

        if not all([merchant_id, service_id, secret_key]):
            raise ValueError("Click credentials not configured")

        # Click expects amount in tiyin (1 sum = 100 tiyin)
        amount_tiyin = amount * 100

        # Build payment URL (for redirect method)
        payment_url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={service_id}"
            f"&merchant_id={merchant_id}"
            f"&amount={amount_tiyin}"
            f"&transaction_param={merchant_trans_id}"
            f"&return_url={return_url}"
        )

        return {
            "payment_url": payment_url,
            "transaction_id": merchant_trans_id,
            "amount_tiyin": amount_tiyin,
        }

    @classmethod
    def verify_callback(cls, data: Dict) -> Dict:
        """
        Verify and process Click callback (prepare or complete).

        Args:
            data: Callback data from Click

        Returns:
            Response dict for Click
        """
        secret_key = current_app.config.get("CLICK_SECRET_KEY")

        click_trans_id = data.get("click_trans_id")
        service_id = data.get("service_id")
        merchant_trans_id = data.get("merchant_trans_id")
        amount = data.get("amount")
        action = data.get("action")  # 0 = prepare, 1 = complete
        sign_time = data.get("sign_time")
        sign_string = data.get("sign_string")

        # Verify signature
        params_for_sign = {
            "click_trans_id": click_trans_id,
            "service_id": service_id,
            "merchant_trans_id": merchant_trans_id,
            "amount": amount,
            "action": action,
            "sign_time": sign_time,
        }

        expected_sign = cls.generate_signature(params_for_sign, secret_key)

        if sign_string != expected_sign:
            return {
                "error": -1,
                "error_note": "Invalid signature",
            }

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "amount": amount,
            "action": action,
            "valid": True,
        }

    @classmethod
    def check_status(cls, transaction_id: str) -> Optional[Dict]:
        """
        Check payment status via Click API.

        Args:
            transaction_id: Transaction ID

        Returns:
            Payment status dict or None
        """
        # Click doesn't provide a direct status check API
        # Status updates come via callbacks
        # This method is a placeholder for future implementation
        return None
