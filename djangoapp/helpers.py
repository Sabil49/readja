import random
from django.core.cache import cache
import requests
from django.conf import settings


def send_otp_to_mobile(mobile, user_obj):
    if cache.get(mobile):
        return False, cache.ttl(mobile)
    try:
        otp_to_sent = random.randint(100000, 999999)
        cache.set(mobile, otp_to_sent, timeout=60)
        user_obj.otp = otp_to_sent
        user_obj.save()
        url = f'https://2factor.in/API/V1/{settings.API_KEY}/SMS/{mobile}/{otp_to_sent}'
        requests.get(url)
        return True, 0
    except Exception as e:
        print(e)
