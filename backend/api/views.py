from django.http import HttpResponse

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
from .permissions import IsSelfOrAdmin

from .models import Playlist, PlaylistTrack
from .serializers import PlaylistSerializer, PlaylistTrackSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def index(request):
    return HttpResponse(f"Hello, {request.user.username}. You're at the polls index.")

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSelfOrAdmin])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_track(self, request, pk=None):
        playlist = self.get_object()
        serializer = PlaylistTrackSerializer(data=request.data)
        if serializer.is_valid():
            deezer_id = serializer.validated_data.get("deezer_id")

            if playlist.tracks.filter(deezer_id=deezer_id).exists():
                return Response(
                    {"detail": "This track is already in the playlist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(playlist=playlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_track(self, request, pk=None):
        playlist = self.get_object()
        track_id = request.data.get('track_id')
        try:
            track = PlaylistTrack.objects.get(deezer_id=track_id, playlist=playlist)
            track.delete()
            return Response({'detail': 'Track removed'}, status=status.HTTP_204_NO_CONTENT)
        except PlaylistTrack.DoesNotExist:
            return Response({'detail': 'Track not found'}, status=status.HTTP_404_NOT_FOUND)
