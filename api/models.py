from django.db import models
import random
import string


class UrlModel(models.Model):
    url = models.URLField(max_length=255)   
    short_code = models.CharField(max_length=6, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.full_clean()  # This will validate the model fields
        if not self.short_code:
            self.short_code = ''.join(random.choices(string.ascii_letters+string.digits, k=6))
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.short_code
    