"""Builds the Indian-context dataset.
  indian_train.csv : template-generated (synthetic) scam + legit messages (English + Hinglish)
  indian_test.csv  : 80 HAND-WRITTEN messages, kept separate from the templates
"""
import random, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

rng = random.Random(7)
BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Bank of Baroda", "Kotak Bank", "Canara Bank"]
HINGLISH = {"aapka", "aapke", "karein", "turant", "aaj", "bhai", "yaar", "kal", "jayega", "kamayein", "jeeta",
            "inaam", "bijli", "khata", "mein", "tera", "nahi", "abhi", "roz", "wapas", "bhejein", "kahan",
            "raha", "rahe", "mat", "bhulna", "hoon", "aaunga", "dekha", "kamaal", "paayein", "chahiye", "ho"}

def slug(b): return b.lower().replace(" bank", "").replace(" ", "")
def rnd(n): return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(n))
def dig(n): return "".join(rng.choice("0123456789") for _ in range(n))
def phone(): return rng.choice("6789") + dig(9)
def amt(lo=500, hi=60000): return f"{rng.randint(lo, hi):,}"

def bad_url(bank):
    s = slug(bank)
    return rng.choice([
        f"bit.ly/{rnd(7)}", f"tinyurl.com/{rnd(8)}", f"cutt.ly/{rnd(6)}",
        f"http://{s}-{rng.choice(['kyc', 'verify', 'secure', 'update', 'rewards'])}.{rng.choice(['xyz', 'top', 'live', 'click'])}/{rnd(5)}",
        f"https://{s}{rng.choice(['-login', '-care', 'online'])}.{rng.choice(['xyz', 'top', 'site'])}"])

SCAM = {
 "kyc": ["Dear {bank} customer, your KYC has expired and your account will be blocked today. Update now: {url}",
         "{bank} ALERT: Your account is suspended due to pending KYC. Verify PAN immediately {url}",
         "URGENT! Complete KYC within 24 hours or {bank} will freeze your account. Click {url} or call {phone}",
         "Aapka {bank} account band ho jayega. Aaj hi KYC update karein: {url}"],
 "reward": ["{bank} Reward: {pts} points expiring today. Redeem Rs {amt} cashback now {url}",
            "Congratulations! You have won Rs {amt} cashback on your {bank} card. Claim now: {url}",
            "Aapke {pts} reward points aaj expire ho rahe hain. Turant redeem karein {url}"],
 "electricity": ["Dear consumer, your electricity connection will be disconnected tonight at 9.30 pm due to unpaid bill. Call officer {phone} immediately",
                 "Power supply to be cut today. Bill of Rs {amt} pending. Pay now: {url}",
                 "Bijli bill pending hai. Aaj raat connection kat jayega, turant call karein {phone}"],
 "courier": ["Your parcel is on hold due to incomplete address. Pay Rs {small} redelivery fee here: {url}",
             "India Post: delivery attempt failed. Update address in 24 hours or package will be returned. {url}",
             "Customs has seized your parcel. Pay Rs {amt} clearance charge to release. Call {phone}"],
 "job": ["Work from home and earn Rs {amt} per day. No experience needed. Join now {url}",
         "Part time job offer: earn Rs {amt} weekly. Pay Rs {small} registration fee to confirm. WhatsApp {phone}",
         "Ghar baithe Rs {amt} roz kamayein. Abhi join karein {url}"],
 "loan": ["Pre-approved loan of Rs {amt} in 5 minutes, no documents. Processing fee Rs {small} only. Apply: {url}",
          "Your loan is sanctioned. Pay insurance charge Rs {small} to release amount. Call {phone}",
          "Instant loan chahiye? Sirf Aadhaar aur PAN se Rs {amt} paayein: {url}"],
 "creditcard": ["Your {bank} credit card limit is increased to Rs {amt}. Verify card number and CVV to activate: {url}",
                "{bank} card blocked for suspicious activity. Share the OTP received to unblock. Call {phone}",
                "Aapka {bank} credit card block ho gaya hai. Unblock karne ke liye OTP bhejein."],
 "taxrefund": ["Income Tax Dept: refund of Rs {amt} pending. Submit bank details at {url}",
               "You are eligible for IT refund Rs {amt}. Confirm account number within 24 hours {url}"],
 "lottery": ["Congratulations! You have won Rs {big} in KBC lucky draw. Call {phone} to claim your prize",
             "You are selected for a free iPhone. Pay Rs {small} delivery charge: {url}",
             "Aapne {big} ka inaam jeeta hai! Claim ke liye turant call karein {phone}"],
 "aadhaar": ["Your Aadhaar will be deactivated today. Link mobile number now: {url}",
             "Aadhaar verification pending. Reply with Aadhaar number and OTP to avoid penalty."],
 "simblock": ["Your SIM will be blocked in 2 hours as per TRAI rules. Call {phone} immediately for verification",
              "Aapka mobile number aaj band ho jayega. Verification ke liye call karein {phone}"],
 "upi_refund": ["Rs {amt} credited by mistake to your account. Please refund by approving the UPI collect request",
                "You received cashback of Rs {amt}. Enter UPI PIN to accept: {url}",
                "Paytm refund Rs {amt} pending. Scan QR on this link to receive {url}"],
}

HAM = [
 "Rs {amt} debited from A/c XX{d4} on {date} towards {merchant} via UPI. Ref {d12}. Not you? Contact your bank's official helpline.",
 "Rs {amt} credited to your a/c XX{d4} on {date}. Avl bal Rs {amt2}.",
 "{otp} is your OTP for {app}. Valid for 10 minutes. Do not share it with anyone.",
 "Your {shop} order #{d4} is out for delivery today. Track it at https://www.{shop_l}.in/orders",
 "Recharge of Rs {small} successful. Validity 28 days. Thank you for choosing {telco}.",
 "Are we still on for dinner at {time}?",
 "Can you send me the notes from today's class?",
 "Running late, will reach by {time}.",
 "Bhai kal {time} baje milte hain canteen mein.",
 "Mummy ne bola ghar jaldi aana.",
 "Assignment submit kar diya kya? Last date kal hai.",
 "Kal ka lecture kaun lega yaar?",
 "Reminder: DBMS lab tomorrow at {time}. Bring your journals.",
 "Your electricity bill of Rs {amt} for {month} is generated. Pay by the due date through the official app.",
 "Your appointment with Dr. {name} is confirmed for {date} at {time}.",
 "PNR {d10}: Your IRCTC ticket is confirmed. Coach S4, Berth 23.",
 "{bank}: Never share your OTP, PIN or CVV with anyone, including bank staff.",
 "Thanks for shopping with {shop}. Your invoice is available in the app.",
 "Dinner ready hai, jaldi aa jao.",
 "Tera kya plan hai weekend ka? Movie chalein?",
 "Your {shop} order has been shipped and will arrive by {date}.",
 "Meeting moved to {time} tomorrow. Please update the team.",
 "Hey {name}, happy birthday! Party at {time} tonight?",
 "Your ride receipt for Rs {small} has been emailed to you. Thanks for riding with {app}.",
 "Fee receipt: Rs {amt} received for Semester {d4}. Thank you.",
 "Rs {small} debited from your {app} wallet for bill payment. Transaction ID {d10}.",
 "Booking confirmed. Ref {d10}, departs {time} from Mumbai Central.",
 "OTP {otp} for your {app} login. Do not disclose to anyone.",
]

def fields(bank=None):
    bank = bank or rng.choice(BANKS)
    shop = rng.choice(["Amazon", "Flipkart", "Myntra", "Swiggy", "Zomato"])
    return dict(bank=bank, url=bad_url(bank), phone=phone(), amt=amt(), amt2=amt(), small=rng.choice([25, 99, 199, 499, 999]),
                big=rng.choice(["25,00,000", "10,00,000", "5,00,000"]), pts=rng.randint(1500, 9999),
                d4=dig(4), d10=dig(10), d12=dig(12), otp=dig(6), shop=shop, shop_l=shop.lower(),
                app=rng.choice(["Swiggy", "Paytm", "IRCTC", "Zomato", "Ola"]), merchant=rng.choice(["Zomato", "Amazon", "Uber", "BigBasket"]),
                telco=rng.choice(["Jio", "Airtel", "Vi"]), time=rng.choice(["5 pm", "6:30 pm", "8 pm", "10 am", "4 pm"]),
                date=rng.choice(["12-09-25", "03-10-25", "21 Sep", "5 Nov"]), month=rng.choice(["September", "October", "August"]),
                name=rng.choice(["Rahul", "Priya", "Anil", "Sneha", "Mehta"]))

def build_train(n_per_type=40, n_ham=480):
    rows = []
    for t, temps in SCAM.items():
        for _ in range(n_per_type):
            rows.append((rng.choice(temps).format(**fields()), 1, t))
    for _ in range(n_ham):
        rows.append((rng.choice(HAM).format(**fields()), 0, "ham"))
    df = pd.DataFrame(rows, columns=["text", "label", "scam_type"]).drop_duplicates("text")
    return df.sample(frac=1, random_state=1).reset_index(drop=True)

TEST_SCAM = [
 ("HDFC Bank: Your net banking will be suspended tonight. Complete your PAN verification now at hdfc-verify-kyc.top/login to avoid deactivation.", "kyc"),
 ("Dear SBI user, KYC expired. Account freeze in 24 hrs. Update here: http://bit.ly/3xKyc9 or call 9876501234", "kyc"),
 ("Aapka Axis Bank khata block hone wala hai. Abhi KYC verify karein warna service band: tinyurl.com/axs-kyc", "kyc"),
 ("ICICI Alert!! Your account is on hold due to incomplete KYC. Click link to reactivate immediately https://icici-secure.xyz/update", "kyc"),
 ("Last warning: your SBI YONO account will lapse today. Install YONO KYC update app: sbi-yono-kyc.net/app", "kyc"),
 ("Congrats! You have 8,450 reward points in your credit card expiring today. Redeem as cash: cutt.ly/rwdNow", "reward"),
 ("HDFC Reward: Rs 9,999 cashback is ready. Claim before midnight by installing our app: hdfcrewards-india.net/apk", "reward"),
 ("Aapke reward points aaj raat expire ho rahe hain. Turant redeem karein: bit.ly/redeem-9k", "reward"),
 ("Dear consumer your electricity will be disconnected tonight 9.30 pm as previous month bill was not updated. Contact officer 8123456790 immediately", "electricity"),
 ("MSEDCL: Bill unpaid. Power supply will be cut today. Pay Rs 1,230 now via http://mseb-pay.top/bill", "electricity"),
 ("Bijli ka bill pending hai, aaj raat connection kat jayega. Turant is number par call karein: 9988776655", "electricity"),
 ("Final notice: Adani Electricity connection will be terminated today. Update details at adani-bill-update.top", "electricity"),
 ("India Post: Your parcel is held at the depot due to incorrect address. Pay Rs 25 redelivery fee at indiapost-track.xyz/pay", "courier"),
 ("Your package could not be delivered. Update your address within 12 hours or it will be returned: tinyurl.com/pkg-help", "courier"),
 ("Customs: parcel in your name is stuck. Pay clearance charges Rs 4,500 to release. WhatsApp 9123456780", "courier"),
 ("BlueDart: delivery failed 2nd attempt. Reschedule and pay Rs 30 at bluedart-resched.top", "courier"),
 ("Work from home! Earn Rs 3,000 daily by liking YouTube videos. No experience needed. Join Telegram now: t.me/earnfast_jobs", "job"),
 ("Hiring part time data entry. Salary Rs 25,000/week. Pay Rs 500 registration fee to confirm your seat. Reply YES", "job"),
 ("Ghar baithe kamayein 5000 rozana. Sirf mobile chahiye. Abhi WhatsApp karein 9871234560", "job"),
 ("Amazon is hiring home-based reviewers, Rs 800 per review. Send Rs 300 deposit to start. Info: wa.me/919876500011", "job"),
 ("Pre-approved personal loan of Rs 5 lakh in 10 minutes. No documents needed. Pay processing fee Rs 999 to receive: quickcash-loan.live", "loan"),
 ("Your loan is approved! Disbursal pending - transfer insurance charge Rs 1,500 to activate. Call 9090909090", "loan"),
 ("Instant loan app: Rs 50,000 credited in 5 mins, just share Aadhaar, PAN and selfie: easyloan-now.xyz", "loan"),
 ("Your credit card limit has been increased to Rs 2,00,000! Verify card number and CVV here to activate: bit.ly/cc-limit-up", "creditcard"),
 ("Axis Bank card blocked due to suspicious activity. Share the OTP sent to you with our executive to unblock.", "creditcard"),
 ("Income Tax Dept: Refund of Rs 15,490 is pending. Submit bank details at incometax-refund.top to receive within 2 days.", "taxrefund"),
 ("You are eligible for a tax refund. Confirm your account number and PAN now: cutt.ly/itr-ref", "taxrefund"),
 ("KBC Lucky Draw: Your number won Rs 25,00,000! Contact manager Mr. Rana on 9812398123 to claim your prize.", "lottery"),
 ("Congratulations!! You are selected for iPhone 15 giveaway. Pay delivery charge Rs 199 only: bit.ly/iphone-free", "lottery"),
 ("Aapne jeeta hai 10 lakh ka inaam! Claim ke liye abhi call karein 9755512345", "lottery"),
 ("Dear winner, Jio Lucky Customer 2025 prize of Rs 1,00,000 awaits. Register now: jio-winner.live", "lottery"),
 ("Your Aadhaar will be deactivated if not linked with mobile. Update immediately: uidai-link.xyz/verify", "aadhaar"),
 ("Aadhaar update mandatory today. Send your Aadhaar number and OTP on this number to avoid penalty.", "aadhaar"),
 ("TRAI Notice: Your SIM will be blocked in 2 hours for illegal activity. Press 9 to speak to officer.", "simblock"),
 ("Your mobile number will be disconnected today due to incomplete verification. Call 9345678123 now.", "simblock"),
 ("Aapka SIM aaj raat band ho jayega. Verification ke liye turant call karein 9456123780", "simblock"),
 ("PhonePe: Rs 4,999 refund received by mistake. Please return it by approving the collect request on UPI immediately.", "upi_refund"),
 ("You have received Rs 2,000 cashback. Enter your UPI PIN to receive the amount: paytm-cashback.top", "upi_refund"),
 ("Google Pay refund of Rs 850 is waiting. Scan the QR code in this link to collect: bit.ly/gp-qr-refund", "upi_refund"),
]
TEST_HAM = [
 "Your OTP for logging in to Swiggy is 482913. It is valid for 10 minutes. Do not share it with anyone.",
 "Rs 1,250.00 debited from A/c XX4821 on 14-09-25 towards Zomato via UPI. Not you? Call the bank on its official number.",
 "Rs 20,000 credited to your account XX9034 by NEFT from Infosys Ltd. Avl bal Rs 31,420.",
 "Your Amazon order for wireless mouse will be delivered by tomorrow 8 pm. Track in the Amazon app.",
 "Hey, are we still meeting at the library after the lecture?",
 "Kal practical ka journal laana mat bhulna, sir check karenge.",
 "Bhai thodi der mein pahunch raha hoon, tu gate pe ruk.",
 "Reminder: your electricity bill of Rs 1,120 is due on 25th. You can pay using the official app or website.",
 "Your Airtel recharge of Rs 299 was successful. 1.5GB/day for 28 days. Thank you.",
 "Dr. Mehta's clinic: your appointment is confirmed for Saturday 11:30 am.",
 "PNR 4512367890 confirmed. S5, berth 41. Train 12951 departs 17:35 from Mumbai Central.",
 "Mom: pick up some milk and bread on your way home please",
 "Class 5B parent meeting is on Friday at 4 pm in the school hall.",
 "Team standup moved to 11 am tomorrow. Please update the sprint board before the call.",
 "Happy birthday Riya! Hope you have an amazing day. Party at 7 tonight?",
 "Tera assignment submit ho gaya kya? Last date kal hai.",
 "SBI: Never share your OTP, PIN or CVV with anyone, including bank staff.",
 "Your cab is arriving in 3 minutes. Driver Ramesh, MH02 AB 1234. Share OTP 5521 with the driver to start the ride.",
 "Thanks for shopping at Reliance Trends. Your invoice is available at the store counter.",
 "Your Zerodha account statement for September is ready on the Console.",
 "Lunch kahan karna hai? Canteen ya bahar?",
 "Library book 'Operating Systems' is due for return on 22 Oct. Please renew or return.",
 "Rs 540 debited from your Paytm wallet for electricity bill payment. Transaction ID 99120342.",
 "Your flight 6E 213 to Delhi is on time. Web check-in opens 48 hours before departure.",
 "Can you share the PPT of yesterday's session? I missed the first half.",
 "Hi, this is Anil from the hostel office. Your room inspection is on Monday.",
 "Aaj ka match dekha? Kohli ne kamaal kar diya yaar.",
 "Your HDFC credit card statement for September is generated. Total due Rs 4,320, due date 10 Oct. Pay via the HDFC app.",
 "Dinner ready hai, jaldi aa jao.",
 "Netflix: Your payment of Rs 199 was successful. Enjoy streaming.",
 "OTP 774120 for your IRCTC login. Do not disclose to anyone.",
 "College fee receipt: Rs 45,000 received for Semester 5. Thank you.",
 "Reminder: Gym membership renews on 1 Nov. Visit the front desk to extend.",
 "Congrats on the new job! Let's celebrate this weekend.",
 "Your order from Domino's is confirmed. Estimated delivery 30 mins.",
 "We have received your application for Data Analyst role. Our team will contact you if shortlisted.",
 "Maths test postponed to Thursday. Syllabus remains the same.",
 "Ola: Your ride receipt for Rs 215 has been emailed to you.",
 "Bank holiday on 2 Oct. Branches will remain closed; UPI and net banking services will work normally.",
 "Yaar mera phone charge nahi hai, mom ko bol dena main late aaunga.",
]

def is_hinglish(t):
    return int(any(w.strip(".,!?:") in HINGLISH for w in t.lower().split()))

def build_test():
    rows = [(t, 1, ty) for t, ty in TEST_SCAM] + [(t, 0, "ham") for t in TEST_HAM]
    return pd.DataFrame(rows, columns=["text", "label", "scam_type"])

if __name__ == "__main__":
    tr, te = build_train(), build_test()
    for d in (tr, te):
        d["hinglish"] = d["text"].map(is_hinglish)
    tr.to_csv(config.INDIAN_TRAIN, index=False); te.to_csv(config.INDIAN_TEST, index=False)
    print(f"train: {len(tr)} rows ({tr.label.sum()} scam) | test: {len(te)} rows ({te.label.sum()} scam, {te.hinglish.sum()} hinglish)")
