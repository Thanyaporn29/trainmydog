from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def profile_upload_path(instance, filename):
    return f'profiles/user_{instance.user.id}/{filename}'


class Profile(models.Model):
    class Role(models.TextChoices):
        MEMBER = "member", "สมาชิก"
        TRAINER = "trainer", "ครูผู้ฝึก"
        ADMIN = "admin", "แอดมิน"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        getattr(instance, 'profile', None) and instance.profile.save()
