import os
import threading
import requests
import asyncio
from urllib.parse import urlparse
from pathlib import Path


def _get_filename_from_url(url):
    """Extract a filename from a URL."""
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name or "." not in name:
        name = "download.mp3"
    return name


def _download_file(url, dest_path):
    """Download a file from a URL to a local path."""
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def _run_pipeline(job_id):
    """Run the Callytics pipeline for a job in a background thread."""
    import django
    django.setup()

    from api.models import Job, File

    job = Job.objects.get(pk=job_id)

    try:
        job.status = "processing"
        job.save()

        input_dir = Path(".data/input")
        input_dir.mkdir(parents=True, exist_ok=True)

        file_name = _get_filename_from_url(job.file_url)
        job.file_name = file_name
        job.save()

        audio_path = str(input_dir / f"job_{job_id}_{file_name}")
        _download_file(job.file_url, audio_path)

        from main import main as callytics_main
        asyncio.run(callytics_main(audio_path))

        latest_file = File.objects.order_by("-id").first()
        if latest_file:
            job.result_file = latest_file
        job.status = "completed"
        job.save()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)[:2000]
        job.save()


def start_pipeline_job(job_id):
    """Launch the pipeline in a background thread."""
    thread = threading.Thread(
        target=_run_pipeline,
        args=(job_id,),
        daemon=True,
    )
    thread.start()
    return thread
