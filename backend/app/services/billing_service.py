import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BillingService:

    def create_checkout_session(self, merchant_id: str):

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",

            line_items=[{
                "price": "price_fraud_saas_plan",  # Stripe price ID
                "quantity": 1
            }],

            metadata={
                "merchant_id": merchant_id
            },

            success_url="https://yourapp.com/success",
            cancel_url="https://yourapp.com/cancel",
        )

        return session.url


billing_service = BillingService()