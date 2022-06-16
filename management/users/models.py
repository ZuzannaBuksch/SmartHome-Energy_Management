from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from users.account_manager import AccountManager
from services.smart_home import SmartHome, SmartHomeUser
from django.forms.models import model_to_dict

class User(AbstractBaseUser):
    name = models.CharField(max_length=20, unique=False)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        smart_home = SmartHome()
        user = {"name": self.name, "email": self.email, "id": self.id, "password": self.password}
        smart_user = SmartHomeUser(user)
        smart_home.push_users([smart_user])
