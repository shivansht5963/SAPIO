from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import ModuleAccess, EmployeeProfile
from .utils import ModulePermission
from .serializers import (
    UserProfileSerializer,
    EmployeeProfileSerializer,
    ModuleAccessSerializer,
    UserListSerializer,
)


class CustomLoginView(APIView):
    """
    POST /api/auth/login/
    Accepts username + password, returns JWT tokens along with
    full user profile, role, scope, and module permissions.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'detail': 'Account is disabled.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check that user has an EmployeeProfile
        if not hasattr(user, 'profile'):
            return Response(
                {'detail': 'User profile not found. Contact admin.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Build response payload
        profile = user.profile
        permissions = ModuleAccess.objects.filter(role=profile.role)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data,
            'profile': EmployeeProfileSerializer(profile).data,
            'permissions': ModuleAccessSerializer(permissions, many=True).data,
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    GET /api/auth/me/
    Returns the logged-in user's profile, role, scope, and permissions.
    Used by the frontend to rehydrate auth state on page reload.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile
        permissions = ModuleAccess.objects.filter(role=profile.role)

        return Response({
            'user': UserProfileSerializer(user).data,
            'profile': EmployeeProfileSerializer(profile).data,
            'permissions': ModuleAccessSerializer(permissions, many=True).data,
        }, status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    """
    GET /api/users/
    Returns a paginated list of users (EmployeeProfiles).
    Scoped by the requesting user's role.
    Supports ?role=field_agent filter.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, ModulePermission('users', 'read')]

    def get_queryset(self):
        qs = EmployeeProfile.objects.filter(
            is_active=True
        ).select_related('user', 'role', 'team', 'region')

        user = self.request.user

        # Role-based scoping
        if hasattr(user, 'profile'):
            role = user.profile.role.name
            if role == 'regional_manager' and user.profile.region:
                qs = qs.filter(region=user.profile.region)
            elif role == 'team_lead' and user.profile.team:
                qs = qs.filter(team=user.profile.team)
            # admin/auditor see all

        # Optional role filter via query param
        role_filter = self.request.query_params.get('role')
        if role_filter:
            qs = qs.filter(role__name=role_filter)

        return qs.order_by('employee_id')

