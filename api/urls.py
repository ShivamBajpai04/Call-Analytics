from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.AnalyzeView.as_view(), name="analyze"),
    path("jobs/", views.JobListView.as_view(), name="job-list"),
    path("jobs/<int:pk>/", views.JobDetailView.as_view(), name="job-detail"),
    path("analytics/", views.AnalyticsListView.as_view(), name="analytics-list"),
    path("analytics/<int:pk>/", views.AnalyticsDetailView.as_view(), name="analytics-detail"),
]
