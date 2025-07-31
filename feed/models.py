from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} by {self.user.username if hasattr(self, 'user') else 'Anonymous'}"


class Comment(models.Model):
    post = models.ForeignKey(
            Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} on Post {self.post.id}"


class Interaction(models.Model):
    LIKE = 'like'
    SHARE = 'share'
    INTERACTION_TYPES = [(LIKE, 'Like'), (SHARE, 'Share')]

    post = models.ForeignKey(
            Post, related_name="interactions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'type')

    def __str__(self):
        return f"{self.type} by {self.user.username} on Post {self.post.id}"
