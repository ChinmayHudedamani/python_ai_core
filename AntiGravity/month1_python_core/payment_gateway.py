import json
import hashlib
from typing import Dict, Any

class RazorpayUPIPaymentEngine:
    """
    Generates instant UPI / Razorpay payment link payloads
    for initial consultation slot reservation fees (e.g. ₹500).
    """

    def generate_consultation_fee_link(self, patient_name: str, patient_phone: str, amount_inr: int = 500) -> Dict[str, Any]:
        """Generates a secure UPI payment link and payload for WhatsApp integration."""
        tx_id: str = f"PAY-{hashlib.sha256(f'{patient_phone}:{amount_inr}'.encode('utf-8')).hexdigest()[:12].upper()}"
        upi_link: str = f"upi://pay?pa=apexdental@icici&pn=Apex%20Dental&am={amount_inr}&tn={tx_id}&cu=INR"
        razorpay_short_link: str = f"https://rzp.io/l/apex_{tx_id.lower()}"

        message_body: str = (
            f"💳 *APEX DENTAL SLOT RESERVATION PAYMENT* 💳\n\n"
            f"Hello {patient_name}! To lock in your exclusive consultation slot, please complete the initial reservation fee payment:\n\n"
            f"💰 **Fee Amount**: ₹{amount_inr} (Adjustable against final treatment bill)\n"
            f"🔗 **Instant Payment Link**: {razorpay_short_link}\n"
            f"📲 **UPI Direct ID**: `apexdental@icici`\n\n"
            f"Click the link above to pay via GPay, PhonePe, Paytm, or Credit Card."
        )

        return {
            "status": "PAYMENT_LINK_GENERATED",
            "transaction_id": tx_id,
            "amount_inr": amount_inr,
            "razorpay_url": razorpay_short_link,
            "upi_link": upi_link,
            "whatsapp_text": message_body
        }


if __name__ == "__main__":
    engine = RazorpayUPIPaymentEngine()
    link = engine.generate_consultation_fee_link("Ananya Roy", "+91-9988776655")
    print(json.dumps(link, indent=2))
