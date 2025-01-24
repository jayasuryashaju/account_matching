from django.urls import path
from .views import MatchRowView, UploadRawDataView

urlpatterns = [
    path('match-row/', MatchRowView.as_view(), name='match-row'),
    path('upload-raw-data/', UploadRawDataView.as_view(), name='upload_raw_data'),
]
