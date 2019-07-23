# from django.shortcuts import render

from django.http import JsonResponse
from invoicingtool.services import InvoicesService, InvoiceFinderService, InvoiceCreatorService, InvoiceUploaderService, UploadedInvoiceFileFinderService
from invoicingtool.serializers import InvoiceSerializer, UploadedInvoiceFileSerializer
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist
import json
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
def index(request):
  invoices_service = InvoicesService()
  results = invoices_service.fetch(offset=request.GET.get("offset"),limit=request.GET.get("limit"))
  serializer = InvoiceSerializer(results, many=True)
  return JsonResponse({"data": serializer.data})
  # return JSONRenderer().render(serializer.data)
  # return HttpResponse("Hello, world. You're at the polls index.")

def show(request, invoice_id):
  invoices_search_service = InvoiceFinderService()
  try:
    result = invoices_search_service.find(invoice_id)
    serializer = InvoiceSerializer(result)
    return JsonResponse({"success": True, "data": serializer.data})
  except ObjectDoesNotExist:
    return JsonResponse({"success": False, "error": "Record doesn't exist"})

def create(request):
  body_unicode = request.body.decode('utf-8')
  request_body = json.loads(body_unicode)
  invoices_creator_service = InvoiceCreatorService()
  
  if invoices_creator_service.create(request_body):
    return JsonResponse({"success": True})
  else:
    return JsonResponse({"success": False})


# Ideally File uploads should go to another controller
class FileUploadView(APIView):
  parser_classes = [FileUploadParser]
  def post(self, request, filename, format=None):
    # breakpoint()
    up_file = request.FILES['file']
    service = InvoiceUploaderService()
    resp = service.upload(up_file)
    # Move the below code to uploader service. Once uploaded to should return the id which can be used for polling to check the progress
    # Add a check to create uploaded_files directory if it doesn't exist
    # file_path = "invoicingtool/uploaded_files/" + "---".join(timezone.now().strftime('%B %d, %Y, %I:%M %p').split(" ")) + up_file.name
    # destination = open(file_path, 'wb+')
    # for chunk in up_file.chunks():
    #   destination.write(chunk)
    #   destination.close()
    return JsonResponse(resp)

def checkUploadedFileStatus(request, file_id):
  service = UploadedInvoiceFileFinderService()
  try:
    result = service.find(file_id)
    serializer = UploadedInvoiceFileSerializer(result)
    return JsonResponse({"success": True, "data": serializer.data})
  except ObjectDoesNotExist:
    return JsonResponse({"success": False, "error": "Record doesn't exist"})

# class FileeUploadView(APIView):
#   parser_classes = (MultiPartParser, FormParser)
#   def post(self, request, *args, **kwargs):
#     breakpoint()
#     return JsonResponse({"success": False})  


    

# Invoice Index API
# Invoice Show API
# Create Invoice API
# Upload Invoice API

# Remaining:
# Polling API
# Download Invoice API
# Get public key API


# HTTPS implementation
# Client asks for public key
# Client generates a hash by encoding a randomly generated secret key using the public key
# In all the APIs client generates a hash using all the request parameters and the secret key generated above
# Client sends hashes from both the above steps as request params in the API