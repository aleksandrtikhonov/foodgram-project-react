from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)

    email = models.EmailField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_follow"),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")), name="self_follow"
            ),
        ]
