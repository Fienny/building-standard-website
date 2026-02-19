"""
PayMe payment integration service.
Docs: https://developer.help.paycom.uz/
"""

import base64
import hashlib
import time
from typing import Dict, Optional

import requests
from flask import current_app


class PaymeService:
    """Service for PayMe (Paycom) payment system integration."""

    BASE_URL = "https://checkout.paycom.uz/api"

    # PayMe transaction states
    STATE_CREATED = 1
    STATE_COMPLETED = 2
    STATE_CANCELLED = -1
    STATE_CANCELLED_AFTER_COMPLETE = -2

    # PayMe error codes
    ERROR_INVALID_AMOUNT = -31001
    ERROR_TRANSACTION_NOT_FOUND = -31003
    ERROR_INVALID_ACCOUNT = -31050
    ERROR_COULD_NOT_PERFORM = -31008

    @staticmethod
    def generate_auth_header() -> str:
        """
        Generate Basic Auth header for PayMe requests.

        Returns:
            Base64 encoded auth string
        """
        merchant_id = current_app.config.get("PAYME_MERCHANT_ID")
        secret_key = current_app.config.get("PAYME_SECRET_KEY")

        if not merchant_id or not secret_key:
            raise ValueError("PayMe credentials not configured")

        # PayMe uses Paycom:{merchant_id} for login
        auth_string = f"Paycom:{secret_key}"
        encoded = base64.b64encode(auth_string.encode()).decode()

        return f"Basic {encoded}"

    @classmethod
    def prepare_payment(
        cls,
        amount: int,
        account_id: str,
        description: str = "",
        return_url: str = "",
    ) -> Dict:
        """
        Prepare PayMe payment and get payment URL.

        Args:
            amount: Amount in tiyin (1 sum = 100 tiyin)
            account_id: Merchant account ID (purchase_id)
            description: Payment description
            return_url: URL to redirect after payment

        Returns:
            dict with payment_url and encoded params
        """
        merchant_id = current_app.config.get("PAYME_MERCHANT_ID")

        if not merchant_id:
            raise ValueError("PayMe merchant ID not configured")

        # PayMe expects amount in tiyin
        amount_tiyin = amount * 100

        # Build params for payment URL
        params = {
            "m": merchant_id,
            "a": amount_tiyin,
            "ac.purchase_id": account_id,  # our purchase ID
        }

        if description:
            params["d"] = description

        if return_url:
            params["cr"] = return_url

        # Encode params to base64 for payment URL
        params_str = ";".join(f"{k}={v}" for k, v in params.items())
        encoded_params = base64.b64encode(params_str.encode()).decode()

        payment_url = f"https://checkout.paycom.uz/{encoded_params}"

        return {
            "payment_url": payment_url,
            "encoded_params": encoded_params,
            "amount_tiyin": amount_tiyin,
        }

    @classmethod
    def verify_callback(cls, method: str, params: Dict) -> Dict:
        """
        Process PayMe RPC callback.

        PayMe uses JSON-RPC 2.0 protocol.

        Args:
            method: RPC method name
            params: RPC params

        Returns:
            RPC response dict
        """
        # Map methods to handlers
        handlers = {
            "CheckPerformTransaction": cls._check_perform_transaction,
            "CreateTransaction": cls._create_transaction,
            "PerformTransaction": cls._perform_transaction,
            "CancelTransaction": cls._cancel_transaction,
            "CheckTransaction": cls._check_transaction,
        }

        handler = handlers.get(method)
        if not handler:
            return {
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                }
            }

        try:
            return {"result": handler(params)}
        except Exception as e:
            return {
                "error": {
                    "code": cls.ERROR_COULD_NOT_PERFORM,
                    "message": str(e),
                }
            }

    @classmethod
    def _check_perform_transaction(cls, params: Dict) -> Dict:
        """
        Check if transaction can be performed.

        Args:
            params: {amount, account: {purchase_id}}

        Returns:
            {allow: true} or error
        """
        amount = params.get("amount")
        account = params.get("account", {})
        purchase_id = account.get("purchase_id")

        if not purchase_id:
            raise ValueError("Invalid account")

        # TODO: Verify purchase exists and amount matches
        # This should be implemented in routes/payments.py

        return {"allow": True}

    @classmethod
    def _create_transaction(cls, params: Dict) -> Dict:
        """
        Create transaction (reserve money).

        Args:
            params: {id, time, amount, account}

        Returns:
            {create_time, transaction, state}
        """
        transaction_id = params.get("id")  # PayMe transaction ID
        time_ms = params.get("time")
        amount = params.get("amount")
        account = params.get("account", {})

        # TODO: Create Payment record with state=STATE_CREATED
        # This should be implemented in routes/payments.py

        return {
            "create_time": int(time.time() * 1000),
            "transaction": str(transaction_id),
            "state": cls.STATE_CREATED,
        }

    @classmethod
    def _perform_transaction(cls, params: Dict) -> Dict:
        """
        Perform transaction (complete payment).

        Args:
            params: {id}

        Returns:
            {transaction, perform_time, state}
        """
        transaction_id = params.get("id")

        # TODO: Update Payment state to STATE_COMPLETED
        # This should be implemented in routes/payments.py

        return {
            "transaction": str(transaction_id),
            "perform_time": int(time.time() * 1000),
            "state": cls.STATE_COMPLETED,
        }

    @classmethod
    def _cancel_transaction(cls, params: Dict) -> Dict:
        """
        Cancel transaction.

        Args:
            params: {id, reason}

        Returns:
            {transaction, cancel_time, state}
        """
        transaction_id = params.get("id")
        reason = params.get("reason")

        # TODO: Update Payment state to STATE_CANCELLED
        # This should be implemented in routes/payments.py

        return {
            "transaction": str(transaction_id),
            "cancel_time": int(time.time() * 1000),
            "state": cls.STATE_CANCELLED,
        }

    @classmethod
    def _check_transaction(cls, params: Dict) -> Dict:
        """
        Check transaction status.

        Args:
            params: {id}

        Returns:
            {create_time, perform_time, cancel_time, transaction, state, reason}
        """
        transaction_id = params.get("id")

        # TODO: Fetch Payment record and return status
        # This should be implemented in routes/payments.py

        return {
            "create_time": int(time.time() * 1000),
            "transaction": str(transaction_id),
            "state": cls.STATE_CREATED,
        }
