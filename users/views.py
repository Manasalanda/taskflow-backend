from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification
from .serializers import (
    RegisterSerializer, UserSerializer, UserSettingsSerializer,
    ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def send_otp_email(user, otp):
    subject = "TaskFlow AI — Password Reset OTP"
    message = f"""
Hello {user.username},

You requested a password reset for your TaskFlow AI account.

Your OTP Code: {otp}

This code expires in 10 minutes.

If you did not request this, please ignore this email.

— TaskFlow AI Team
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True, None
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        return False, str(e)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserSettingsView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Invalidate all previous unused OTPs
        OTPVerification.objects.filter(
            user=user, is_used=False
        ).update(is_used=True)

        # Generate and save new OTP
        otp = OTPVerification.generate_otp()
        OTPVerification.objects.create(user=user, otp=otp)

        # Send OTP email
        sent, error = send_otp_email(user, otp)

        if not sent:
            return Response(
                {'error': f'Failed to send email: {error}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': f'OTP sent to {email}. Valid for 10 minutes.'
        })


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            otp_obj = OTPVerification.objects.filter(
                user=user,
                otp=otp,
                is_used=False
            ).latest('created_at')

            if not otp_obj.is_valid():
                return Response(
                    {'error': 'OTP has expired. Please request a new one.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'message': 'OTP verified successfully.'
            })

        except OTPVerification.DoesNotExist:
            return Response(
                {'error': 'Invalid OTP. Please check and try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found with this email.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
            otp_obj = OTPVerification.objects.filter(
                user=user,
                otp=otp,
                is_used=False
            ).latest('created_at')

            if not otp_obj.is_valid():
                return Response(
                    {'error': 'OTP expired. Please request a new one.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Reset password
            user.set_password(new_password)
            user.save()

            # Mark OTP as used so it cannot be reused
            otp_obj.is_used = True
            otp_obj.save()

            return Response({
                'message': 'Password reset successfully. You can now log in.'
            })

        except OTPVerification.DoesNotExist:
            return Response(
                {'error': 'Invalid OTP. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'No account found.'},
                status=status.HTTP_404_NOT_FOUND
            )





