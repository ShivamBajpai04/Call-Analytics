from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Job
from .serializers import (
    FileListSerializer,
    FileDetailSerializer,
    JobSerializer,
    AnalyzeRequestSerializer,
)
from .tasks import start_pipeline_job


class AnalyzeView(APIView):
    """
    POST /api/analyze/
    Submit an audio file URL for processing.

    Request body:
        {"file_url": "https://example.com/call.mp3"}

    Returns the created job with a status you can poll.
    """

    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = Job.objects.create(
            file_url=serializer.validated_data["file_url"],
        )

        start_pipeline_job(job.id)

        return Response(
            JobSerializer(job).data,
            status=status.HTTP_202_ACCEPTED,
        )


class JobDetailView(generics.RetrieveAPIView):
    """
    GET /api/jobs/<id>/
    Check the status of a processing job.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class JobListView(generics.ListAPIView):
    """
    GET /api/jobs/
    List all processing jobs.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class AnalyticsListView(generics.ListAPIView):
    """
    GET /api/analytics/
    List all processed call analytics.
    """
    queryset = File.objects.select_related("topic").all()
    serializer_class = FileListSerializer


class AnalyticsDetailView(generics.RetrieveAPIView):
    """
    GET /api/analytics/<id>/
    Get full details for a single call, including all utterances.
    """
    queryset = File.objects.select_related("topic").prefetch_related("utterances").all()
    serializer_class = FileDetailSerializer
