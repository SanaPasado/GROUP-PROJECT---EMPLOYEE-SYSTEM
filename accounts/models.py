from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False,):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model( email=self.normalize_email(email))
        user_obj.set_password(password)
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email, password=None):
        user=self.create_user(
            email
        , password=password,
          is_active = True,
          is_staff = True,)

        return user


    def create_superuser(self, email, password=None ):
        user=self.create_user(
            email
        , password=password,
          is_active = True,
          is_staff = True,
          is_admin = True)
        return user



class Employee(AbstractBaseUser): #-----> means that we're telling django that we'll use custom user model
    email = models.EmailField( max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_hired = models.DateTimeField(max_length=255)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    salary = models.FloatField()
    phone_number = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='employee_photos', blank=True, null=True)
    # status      = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email' #username
    REQUIRED_FIELDS = []#fields that are needed when creating a superuser or admin account

    objects = UserManager()

    def __str__(self):
        return self.email
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


