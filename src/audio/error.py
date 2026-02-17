# Standard library imports
import os
import logging
import subprocess
from typing import Annotated

# Related third party imports
import numpy as np
import librosa

logging.basicConfig(level=logging.INFO)


class DialogueDetecting:
    """
    Class for detecting dialogue in audio files using energy-based speaker
    turn detection.

    This class processes audio files by analyzing speech energy patterns
    and silence gaps to determine if there are likely multiple speakers
    (turn-taking behavior).

    Parameters
    ----------
    chunk_duration : int, optional
        Duration of each analysis chunk in seconds. Defaults to 5.
    sample_rate : int, optional
        Sampling rate for the processed audio. Defaults to 16000.
    channels : int, optional
        Number of audio channels. Defaults to 1.
    delete_original : bool, optional
        If True, deletes the original audio file when no dialogue is detected. Defaults to False.
    skip_if_no_dialogue : bool, optional
        If True, skips further processing if no dialogue is detected. Defaults to False.
    temp_dir : str, optional
        Directory for temporary files. Defaults to ".temp".
    min_silence_duration : float, optional
        Minimum silence gap (seconds) to consider a speaker turn. Defaults to 0.3.
    min_turn_count : int, optional
        Minimum number of speaker turns to consider it a dialogue. Defaults to 3.
    """

    def __init__(self,
                 chunk_duration: int = 5,
                 sample_rate: int = 16000,
                 channels: int = 1,
                 delete_original: bool = False,
                 skip_if_no_dialogue: bool = False,
                 temp_dir: str = ".temp",
                 min_silence_duration: float = 0.3,
                 min_turn_count: int = 3):
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.delete_original = delete_original
        self.skip_if_no_dialogue = skip_if_no_dialogue
        self.temp_dir = temp_dir
        self.min_silence_duration = min_silence_duration
        self.min_turn_count = min_turn_count

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    @staticmethod
    def get_audio_duration(audio_file: Annotated[str, "Path to the audio file"]) -> Annotated[
        float, "Duration of the audio in seconds"]:
        """
        Get the duration of an audio file in seconds.

        Parameters
        ----------
        audio_file : str
            Path to the audio file.

        Returns
        -------
        float
            Duration of the audio file in seconds.

        Examples
        --------
        >>> DialogueDetecting.get_audio_duration("example.wav")
        120.5
        """
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_file],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())

    def _detect_speech_segments(self, audio_path: str):
        """
        Detect speech and silence segments using RMS energy thresholding.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        int
            Number of speech-to-silence-to-speech transitions (speaker turns).
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

        frame_length = int(0.025 * sr)
        hop_length = int(0.010 * sr)
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

        threshold = np.mean(rms) * 0.5
        is_speech = rms > threshold

        min_silence_frames = int(self.min_silence_duration / (hop_length / sr))

        turn_count = 0
        silence_count = 0
        in_speech = False

        for frame_is_speech in is_speech:
            if frame_is_speech:
                if not in_speech and silence_count >= min_silence_frames:
                    turn_count += 1
                in_speech = True
                silence_count = 0
            else:
                if in_speech:
                    silence_count = 1
                    in_speech = False
                else:
                    silence_count += 1

        return turn_count

    def process(self, audio_file: Annotated[str, "Path to the input audio file"]) -> Annotated[
        bool, "True if dialogue detected, False otherwise"]:
        """
        Process the audio file to detect dialogue by analyzing speaker turn patterns.

        Uses energy-based speech/silence detection to count turn-taking events.
        Multiple turns suggest a dialogue between two or more speakers.

        Parameters
        ----------
        audio_file : str
            Path to the audio file.

        Returns
        -------
        bool
            True if dialogue patterns are detected, False otherwise.

        Examples
        --------
        >>> dialogue_detector = DialogueDetecting()
        >>> dialogue_detector.process("example.wav")
        True
        """
        logging.info(f"Detecting dialogue in: {audio_file}")

        turn_count = self._detect_speech_segments(audio_file)
        logging.info(f"Detected {turn_count} speaker turns.")

        has_dialogue = turn_count >= self.min_turn_count

        if not has_dialogue:
            logging.info("No dialogue detected or insufficient speaker turns.")
            if self.delete_original:
                logging.info(f"No dialogue found. Deleting original file: {audio_file}")
                os.remove(audio_file)
            if self.skip_if_no_dialogue:
                logging.info("Skipping further processing due to lack of dialogue.")
                return False

        return has_dialogue


if __name__ == "__main__":
    processor = DialogueDetecting(delete_original=True)
    audio_path = ".data/example/kafkasya.mp3"
    process_result = processor.process(audio_path)
    print("Dialogue detected:", process_result)
