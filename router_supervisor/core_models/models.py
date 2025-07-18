from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name='', last_name='', role='', **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'

class Threshold(models.Model):
    threshold_id = models.AutoField(primary_key=True)
    ram = models.IntegerField()
    cpu = models.IntegerField()
    traffic = models.IntegerField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'threshold'

class KPI(models.Model):
    kpi_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'kpi'

class Router(models.Model):
    router_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
    threshold = models.ForeignKey(
        Threshold,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'router'

class Interface(models.Model):
    interface_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="default")
    traffic = models.DecimalField(max_digits=15, decimal_places=2)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="unknown")
    input_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    output_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    errors = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} on {self.router.name}"

    class Meta:
        db_table = 'interface'
        unique_together = (('router', 'name'),)

class Alert(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()
    log_date = models.DateTimeField()

    class Meta:
        unique_together = (('interface', 'log_id'),)
        db_table = 'alert'

    def __str__(self):
        return f"Alert {self.interface_id} - {self.log_id}"

class User_Router(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'router'),)
        db_table = 'user_router'

    def __str__(self):
        return f"{self.user} <-> {self.router}"

class Router_Interface_Log(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()

    class Meta:
        unique_together = (('router', 'interface', 'log_id'),)
        db_table = 'router_interface_log'

    def __str__(self):
        return f"Router {self.router} - Interface {self.interface} - Log {self.log_id}"

class Threshold_KPI(models.Model):
    threshold = models.ForeignKey(Threshold, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('threshold', 'kpi'),)
        db_table = 'threshold_kpi'

    def __str__(self):
        return f"Threshold {self.threshold} - KPI {self.kpi}"

class KPI_Interface_Log(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('interface', 'log_id', 'kpi'),)
        db_table = 'kpi_interface_log'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['interface', 'kpi']),
        ]

    def __str__(self):
        return f"Interface {self.interface} - Log {self.log_id} - KPI {self.kpi}: {self.value}"

class RouterMetricLog(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = "router_metric_log"