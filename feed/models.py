from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField()
    likes = models.ManyToManyField("auth.user", related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def like_count(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} - {self.content[:30]}"
