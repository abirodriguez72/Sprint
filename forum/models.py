from django.db import models
import uuid

class Post(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='forum_posts', default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Reply(models.Model):
    post = models.ForeignKey(Post, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.post.title}"
