from django.contrib import messages
from django.shortcuts import redirect, render
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from .helpers import *
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 403,
                    'errors': serializer.errors
                })
            serializer.save()
            serializer_data = serializer.data
            serializer_phone = serializer_data['phone']
            serializer_email = serializer_data['email']
            user_obj = User.objects.filter(email=serializer_email)
            status, time = send_otp_to_mobile(serializer_phone, user_obj[0])
            return Response({'status': 200, 'message': 'email and otp sent'})

        except Exception as e:
            print(e)
            return Response({'status': 404, 'error': 'something went wrong'})


class LoginView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            data = request.data
            user_name = data.get('email')
            user_pass = data.get('password')
            user = authenticate(request, username=user_name, password=user_pass)
            if user is not None:
                login(request, user)
                return Response({'status': 200, 'message': 'You have been successfully logged in'})

            return Response({'status': 403, 'message': 'wrong username or password'})
        except Exception as e:
            print(e)
        return Response({'status': 404, 'error': 'something went wrong'})


class VerifyOtp(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            data = request.data
            user_obj = User.objects.get(otp=data.get('otp'))
            otp = data.get('otp')
            print(otp)
            print(user_obj.otp)
            if user_obj and user_obj.otp == otp:
                user_obj.is_phone_verified = True
                user_obj.save()
                return Response({'status': 200, 'message': 'your otp is verified'})

            return Response({'status': 403, 'message': 'Otp did not match'})

        except Exception as e:
            print(e)
        return Response({'status': 404, 'error': 'something went wrong'})


class resendotp(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            data = request.data
            print(data)
            mytoken_cookie = request.COOKIES.get('mytoken')
            print(mytoken_cookie)
            user_obj = User.objects.get(auth_token=mytoken_cookie)
            print(user_obj.phone)
            if user_obj:
                status, time = send_otp_to_mobile(user_obj.phone, user_obj)
                if status:
                    return Response({'status': 200, 'message': 'new otp sent'})

                return Response({'status': 404, 'message': f'try after {time} seconds '})

            return Response({'status': 404, 'message': 'no user found'})

        except Exception as e:
            print(e)

        return Response({'status': 404, 'error': 'something went wrong'})


def verify(request, recipient):
    try:
        user_obj = User.objects.filter(email=recipient).first()
        if user_obj is not None:
            user_obj.is_email_verified = True
            user_obj.save()
            messages.success(request, "Your email account has been verified.")
            return render(request, 'email_verified.html')
        else:
            return None
    except Exception as e:
        print(e)
