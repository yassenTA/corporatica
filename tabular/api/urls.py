from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path("upload_file", UploadFileView.as_view(), name="upload_file"),
    path("get_file", GetDatasetView.as_view(), name="data_sets"),
    path("update_file", UpdateDatasetView.as_view(), name="data_set_detail"),
    path("delete_file", DeleteDatasetView.as_view(), name="data_set_delete"),
    path("statistics", CalculateStatisticsView.as_view(), name="calculate_statistics"),
    path("chart", PlotChartView.as_view(), name="chart"),
]

# router = DefaultRouter()
# router.register(r"datasets", DataSetViewSet, basename="dataset")

# urlpatterns = router.urls
