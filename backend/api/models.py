from django.db import models

from django.db import models
from django.conf import settings

class Playlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='playlists'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    likes = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=75)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    deezer_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    duration = models.IntegerField()
    preview_url = models.URLField(blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"
