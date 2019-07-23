from django.urls import path
from django.conf.urls import url
from . import views
from .views import FileUploadView
#,FileeUploadView

urlpatterns = [
    path('invoices', views.index, name='index'),
    path('invoices/create/', views.create, name='create'),
    # path('invoices/upload/', views.upload),
    # path('invoices/upload/', FileeUploadView.as_view()),
    url(r'invoices/upload/(?P<filename>[^/]+)$', FileUploadView.as_view()),
    path('invoices/<int:invoice_id>/', views.show, name='show'),
    path('invoices/uploaded-files/<int:file_id>/', views.checkUploadedFileStatus, name='checkUploadedFileStatus')
]
