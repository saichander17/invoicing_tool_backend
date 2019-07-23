# We can use the serializers to convert complex data such as model instances to native Python datatypes
# Find the documentation about serializers in https://www.django-rest-framework.org/api-guide/serializers
from rest_framework import serializers
from django.contrib.postgres.fields import JSONField
from invoicingtool.models import Invoice, UploadedInvoiceFile

class InvoiceSerializer(serializers.ModelSerializer):
  # In a model serilaizer, the following lines are unnecessary
  # customer_info = serializers.JSONField()
  # customer_id = serializers.IntegerField()
  # product_info = serializers.JSONField()
  # pricing = serializers.JSONField()
  # invoice_path = serializers.CharField()
  # created_by = serializers.IntegerField()
  # updated_by = serializers.IntegerField()
  # created_at = serializers.DateTimeField()
  # updated_at = serializers.DateTimeField()
  # Add any validations needed in the validate() method (https://www.django-rest-framework.org/api-guide/serializers/#object-level-validation)
  # def validate(self, data):
  #   return data
  class Meta(object):
    model = Invoice
    # Created at and updated at should not be passed from outside. It should be updated from here or from the model
    fields = ['id', 'customer_info', 'customer_id', 'product_info', 'pricing', 'invoice_path', 'created_by', 'updated_by', 'created_at', 'updated_at']

class UploadedInvoiceFileSerializer(serializers.ModelSerializer):
  class Meta(object):
    model = UploadedInvoiceFile
    fields = ['id', 'status', 'path', 'percentage_processed', 'created_by']