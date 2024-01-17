import uuid
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from core.stationdata.models import Estacion

class UserManager(BaseUserManager):
    def get_object_by_public_id(self, id_usuario):
        try:
            return self.get(id_usuario=id_usuario)
        except (ObjectDoesNotExist, ValueError, TypeError):
            raise Http404

    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, nombre, apellido, password, **extra_fields)

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    custom_permissions = models.ManyToManyField(Permission, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return self.email
    def has_permission(self, permission_name):
        return self.custom_permissions.filter(name=permission_name).exists()
    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}"

# models.py

