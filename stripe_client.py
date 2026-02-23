import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

class StripeClient:
    def create_checkout_session(self, soundcloud_id: str, amount: float, success_url: str, cancel_url: str):
        """
        Creates a Stripe Checkout session for a song submission.
        """
        if not stripe.api_key or stripe.api_key == "your_stripe_secret_key":
            # Return a mock session ID for development
            return "mock_session_id_" + soundcloud_id

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Song Submission: {soundcloud_id}',
                    },
                    'unit_amount': int(amount * 100), # Stripe expects cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "soundcloud_id": soundcloud_id,
                "bid_amount": amount
            }
        )
        return session.id

    def verify_webhook(self, payload, sig_header):
        """
        Verifies Stripe webhook signature.
        """
        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            return event
        except ValueError as e:
            raise e
        except stripe.error.SignatureVerificationError as e:
            raise e

stripe_client = StripeClient()
