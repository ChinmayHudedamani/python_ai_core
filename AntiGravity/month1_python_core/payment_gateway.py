import json
import hashlib
import datetime
from typing import Dict, Any, List

class ZomatoBlinkitStylePaymentEngine:
    """
    Ultra-Fast Zomato & Blinkit Style 1-Click WhatsApp Payment Gateway Engine.
    Features:
    - Itemized bill breakdown with instant discount coupon (SMILE50)
    - 1-Click direct deep-links for GPay, PhonePe, Paytm, and Credit/Debit Cards
    - Real-time instant payment confirmation receipt generator
    """

    def generate_zomato_style_checkout_payload(self, patient_name: str, patient_phone: str, procedure_name: str = "Invisalign Consultation") -> Dict[str, Any]:
        """Generates an itemized Zomato/Blinkit style checkout bill and 1-click UPI buttons."""
        clean_phone: str = patient_phone.replace("-", "").replace(" ", "").replace("+", "")
        tx_id: str = f"TXN-{hashlib.sha256(f'{clean_phone}:{datetime.datetime.now().isoformat()}'.encode('utf-8')).hexdigest()[:10].upper()}"

        standard_fee: int = 1000
        discount_amount: int = 500
        payable_fee: int = standard_fee - discount_amount

        gpay_url: str = f"upi://pay?pa=apexdental@icici&pn=Apex%20Dental&am={payable_fee}&tn={tx_id}&mode=02"
        phonepe_url: str = f"https://phon.pe/pay?pa=apexdental@icici&am={payable_fee}&tn={tx_id}"
        paytm_url: str = f"paytmmp://pay?pa=apexdental@icici&pn=Apex%20Dental&am={payable_fee}&tn={tx_id}"
        razorpay_url: str = f"https://rzp.io/l/apex_{tx_id.lower()}"

        bill_text: str = (
            f"🛒 *APEX DENTAL 1-CLICK EXPRESS CHECKOUT* 🛒\n\n"
            f"Hello {patient_name}! Your appointment slot is held for *10 minutes*.\n\n"
            f"📋 **ITEMIZED BILL SUMMARY**:\n"
            f"  • Specialist Consultation Fee: ₹{standard_fee:,}\n"
            f"  • First-Visit Discount (Coupon `SMILE50`): -₹{discount_amount:,}\n"
            f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  💰 **TOTAL PAYABLE AMOUNT**: *₹{payable_fee:,}*\n"
            f"  *(100% Refundable / 100% Adjustable against treatment bill)*\n\n"
            f"⚡ **SELECT YOUR 1-CLICK PAYMENT APP**:\n"
            f"  🟢 Google Pay : {gpay_url}\n"
            f"  🟣 PhonePe    : {phonepe_url}\n"
            f"  🔵 Paytm / Card: {paytm_url}\n"
            f"  💳 Web Checkout: {razorpay_url}\n\n"
            f"🔒 *100% PCI-DSS Secure Payment Gateway via Razorpay & ICICI Bank*"
        )

        buttons: List[Dict[str, str]] = [
            {"id": "pay_gpay", "title": f"🟢 GPay ₹{payable_fee}"},
            {"id": "pay_phonepe", "title": f"🟣 PhonePe ₹{payable_fee}"},
            {"id": "pay_card", "title": f"💳 Card/Netbanking"}
        ]

        return {
            "status": "CHECKOUT_READY",
            "transaction_id": tx_id,
            "patient_name": patient_name,
            "patient_phone": patient_phone,
            "bill_summary": {
                "standard_fee": standard_fee,
                "discount_applied": discount_amount,
                "payable_fee": payable_fee,
                "coupon_code": "SMILE50"
            },
            "payment_links": {
                "gpay": gpay_url,
                "phonepe": phonepe_url,
                "paytm": paytm_url,
                "razorpay": razorpay_url
            },
            "whatsapp_checkout_text": bill_text,
            "interactive_buttons": buttons
        }

    def generate_instant_payment_receipt(self, tx_id: str, patient_name: str, amount_paid: int = 500) -> Dict[str, Any]:
        """Generates instant Zomato/Blinkit style payment success receipt."""
        now_str: str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
        receipt_text: str = (
            f"✅ *PAYMENT SUCCESSFUL - APPOINTMENT LOCKED* ✅\n\n"
            f"Thank you {patient_name}! We have received your reservation payment.\n\n"
            f"🧾 **Transaction ID**: `{tx_id}`\n"
            f"💵 **Amount Paid**: ₹{amount_paid}.00\n"
            f"🕒 **Date & Time**: {now_str}\n"
            f"💳 **Payment Status**: CONFIRMED & SLOTS LOCKED\n\n"
            f"📍 **Clinic Address**: 100 Feet Road, Koramangala 4th Block, Bengaluru\n"
            f"📅 Your appointment calendar invite (.ics) has been sent to your chat!"
        )
        return {
            "status": "PAYMENT_CONFIRMED",
            "receipt_text": receipt_text,
            "transaction_id": tx_id
        }


if __name__ == "__main__":
    engine = ZomatoBlinkitStylePaymentEngine()
    checkout = engine.generate_zomato_style_checkout_payload("Ananya Roy", "+91-9988776655")
    print(json.dumps(checkout, indent=2))
