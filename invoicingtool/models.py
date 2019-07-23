from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

class AutoDateTimeField(models.DateTimeField):
  def pre_save(self, model_instance, add):
    return timezone.now()

class Invoice(models.Model):
  customer_info = JSONField()
  # You can add customer_id. As of now it can be optional because we are not creating customers or orders or any other tables.
  customer_id = models.IntegerField(null=True)
  product_info = JSONField()
  pricing = JSONField()
  invoice_path = models.CharField(max_length=255, null=True)
  # created_by will have the admin user id who creates the invoice.
  created_by = models.IntegerField(null=True)
  # updated_by will have the last admin user id who updates the invoice.
  updated_by = models.IntegerField(null=True)
  created_at = models.DateTimeField(default=timezone.now, editable=False)#auto_now_add=True, editable=False)
  updated_at = AutoDateTimeField(default=timezone.now)

class UploadedInvoiceFile(models.Model):
  percentage_processed = models.IntegerField(default=0)
  path = models.CharField(max_length=255)
  status = models.CharField(max_length=255, default='pending')
  created_by = models.IntegerField(null=True)
  created_at = models.DateTimeField(default=timezone.now, editable=False)
  updated_at = AutoDateTimeField(default=timezone.now)