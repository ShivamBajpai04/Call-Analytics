from collections import Counter

from rest_framework import serializers
from .models import Topic, File, Utterance, Job


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "name"]


class UtteranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utterance
        fields = [
            "id", "speaker", "sequence", "start_time",
            "end_time", "content", "sentiment", "profane",
        ]


def _sentiment_summary(file_obj):
    """Build a sentiment distribution dict for a File's utterances."""
    sentiments = file_obj.utterances.values_list("sentiment", flat=True)
    counts = Counter(sentiments)
    total = sum(counts.values())
    return {
        "positive": counts.get("Positive", 0),
        "negative": counts.get("Negative", 0),
        "neutral": counts.get("Neutral", 0),
        "total": total,
    }


class FileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing all call analytics."""
    topic_name = serializers.CharField(source="topic.name", default="Unknown")
    utterance_count = serializers.SerializerMethodField()
    sentiment = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id", "name", "extension", "duration",
            "topic_name", "summary", "conflict", "silence",
            "utterance_count", "sentiment",
        ]

    def get_utterance_count(self, obj):
        return obj.utterances.count()

    def get_sentiment(self, obj):
        return _sentiment_summary(obj)


class FileDetailSerializer(serializers.ModelSerializer):
    """Full serializer with utterances for a single call."""
    topic_name = serializers.CharField(source="topic.name", default="Unknown")
    utterances = UtteranceSerializer(many=True, read_only=True)
    sentiment = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id", "name", "extension", "path", "duration",
            "rate", "channels", "bit_depth",
            "min_freq", "max_freq",
            "rms_loudness", "zero_crossing_rate", "spectral_centroid",
            "eq_20_250", "eq_250_2000", "eq_2000_6000", "eq_6000_20000",
            "topic_name", "summary", "conflict", "silence",
            "sentiment", "utterances",
        ]

    def get_sentiment(self, obj):
        return _sentiment_summary(obj)


class JobSerializer(serializers.ModelSerializer):
    result = FileListSerializer(source="result_file", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "file_url", "file_name", "status",
            "error_message", "created_at", "updated_at", "result",
        ]
        read_only_fields = [
            "id", "file_name", "status", "error_message",
            "created_at", "updated_at", "result",
        ]


class AnalyzeRequestSerializer(serializers.Serializer):
    """Validates the POST /api/analyze/ payload."""
    file_url = serializers.URLField(
        help_text="URL of the audio file to download and process."
    )
