from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.email

class Threshold(models.Model):
    threshold_id = models.CharField(max_length=50, primary_key=True)
    ram = models.IntegerField()
    cpu = models.IntegerField()
    traffic = models.IntegerField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class KPI(models.Model):
    kpi_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Router(models.Model):
    router_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
    threshold = models.ForeignKey(Threshold, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Interface(models.Model):
    interface_id = models.AutoField(primary_key=True)
    traffic = models.DecimalField(max_digits=15, decimal_places=2)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)

    def __str__(self):
        return f"Interface {self.interface_id}"

class Alert(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()
    log_date = models.DateTimeField()

    class Meta:
        unique_together = (('interface', 'log_id'),)

    def __str__(self):
        return f"Alert {self.interface_id} - {self.log_id}"

class User_Router(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'router'),)

    def __str__(self):
        return f"{self.user} <-> {self.router}"

class Router_Interface_Log(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()

    class Meta:
        unique_together = (('router', 'interface', 'log_id'),)

    def __str__(self):
        return f"Router {self.router} - Interface {self.interface} - Log {self.log_id}"

class Threshold_KPI(models.Model):
    threshold = models.ForeignKey(Threshold, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('threshold', 'kpi'),)

    def __str__(self):
        return f"Threshold {self.threshold} - KPI {self.kpi}"

class KPI_Interface_Log(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    log_id = models.IntegerField()
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('interface', 'log_id', 'kpi'),)

    def __str__(self):
        return f"Interface {self.interface} - Log {self.log_id} - KPI {self.kpi}"