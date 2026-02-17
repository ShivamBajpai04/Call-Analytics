from django.db import models


class Topic(models.Model):
    """Maps to the existing Topic table."""
    name = models.TextField(unique=True, db_column="Name")

    class Meta:
        managed = False
        db_table = "Topic"

    def __str__(self):
        return self.name


class File(models.Model):
    """Maps to the existing File table."""
    name = models.TextField(db_column="Name")
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_NULL, null=True, db_column="TopicID"
    )
    extension = models.TextField(null=True, db_column="Extension")
    path = models.TextField(null=True, db_column="Path")
    rate = models.IntegerField(null=True, db_column="Rate")
    min_freq = models.FloatField(null=True, db_column="MinFreq")
    max_freq = models.FloatField(null=True, db_column="MaxFreq")
    bit_depth = models.IntegerField(null=True, db_column="BitDepth")
    channels = models.IntegerField(null=True, db_column="Channels")
    duration = models.FloatField(null=True, db_column="Duration")
    rms_loudness = models.FloatField(null=True, db_column="RMSLoudness")
    zero_crossing_rate = models.FloatField(null=True, db_column="ZeroCrossingRate")
    spectral_centroid = models.FloatField(null=True, db_column="SpectralCentroid")
    eq_20_250 = models.FloatField(null=True, db_column="EQ_20_250_Hz")
    eq_250_2000 = models.FloatField(null=True, db_column="EQ_250_2000_Hz")
    eq_2000_6000 = models.FloatField(null=True, db_column="EQ_2000_6000_Hz")
    eq_6000_20000 = models.FloatField(null=True, db_column="EQ_6000_20000_Hz")
    mfcc_1 = models.FloatField(null=True, db_column="MFCC_1")
    mfcc_2 = models.FloatField(null=True, db_column="MFCC_2")
    mfcc_3 = models.FloatField(null=True, db_column="MFCC_3")
    mfcc_4 = models.FloatField(null=True, db_column="MFCC_4")
    mfcc_5 = models.FloatField(null=True, db_column="MFCC_5")
    mfcc_6 = models.FloatField(null=True, db_column="MFCC_6")
    mfcc_7 = models.FloatField(null=True, db_column="MFCC_7")
    mfcc_8 = models.FloatField(null=True, db_column="MFCC_8")
    mfcc_9 = models.FloatField(null=True, db_column="MFCC_9")
    mfcc_10 = models.FloatField(null=True, db_column="MFCC_10")
    mfcc_11 = models.FloatField(null=True, db_column="MFCC_11")
    mfcc_12 = models.FloatField(null=True, db_column="MFCC_12")
    mfcc_13 = models.FloatField(null=True, db_column="MFCC_13")
    summary = models.TextField(db_column="Summary")
    conflict = models.IntegerField(db_column="Conflict")
    silence = models.FloatField(db_column="Silence")

    class Meta:
        managed = False
        db_table = "File"

    def __str__(self):
        return self.name


class Utterance(models.Model):
    """Maps to the existing Utterance table."""
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name="utterances", db_column="FileID"
    )
    speaker = models.TextField(db_column="Speaker")
    sequence = models.IntegerField(db_column="Sequence")
    start_time = models.FloatField(db_column="StartTime")
    end_time = models.FloatField(db_column="EndTime")
    content = models.TextField(db_column="Content")
    sentiment = models.TextField(db_column="Sentiment")
    profane = models.IntegerField(db_column="Profane")

    class Meta:
        managed = False
        db_table = "Utterance"
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.speaker}: {self.content[:50]}"


class Job(models.Model):
    """Tracks pipeline processing jobs."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    file_url = models.URLField(max_length=2048)
    file_name = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    result_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs"
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Job"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Job {self.pk} - {self.status} - {self.file_name}"
