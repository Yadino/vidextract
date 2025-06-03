import torch
import whisper
import librosa
from typing import List, Dict
from moviepy import VideoFileClip
from torch_vggish_yamnet import yamnet
from torch_vggish_yamnet.input_proc import WaveformToInput


class AudioDetector:
    def __init__(self, whisper_model_size = "small"):
        """
        Initializes AudioDetector with Whisper and YAMNet models.

        Parameters:
            whisper_model_size (str): Whisper model size to load (default "small").
        """

        self.whisper_model = whisper.load_model(whisper_model_size)
        self.yamnet_model = self.load_yamnet_model()
        self.converter = WaveformToInput()
        self.class_names = self.load_class_names()
        
    def load_yamnet_model(self):
        """
        Loads the pretrained YAMNet model.

        Returns:
            torch.nn.Module: YAMNet model in evaluation mode.
        """

        model = yamnet.yamnet(pretrained=True)
        model.eval()
        return model
        
    def load_class_names(self):
        """
        Loads YAMNet class names from a CSV resource file.

        Returns:
            List[str]: List of class names.
        """

        with open('resources/yamnet_class_map.csv', 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')[1:]  # Skip header
        class_names = [line.split(',')[2] for line in lines]
        return class_names

    def extract_audio(self, video_path, output_wav="output/audio.wav"):
        """
        Extracts audio track from video file and saves as WAV.

        Parameters:
            video_path (str): Path to the input video file.
            output_wav (str): Path for output WAV file (default "output/audio.wav").

        Returns:
            str: Path to the extracted audio WAV file.
        """

        video = VideoFileClip(video_path)
        video.audio.write_audiofile(output_wav, fps=16000, logger=None)
        return output_wav

    def detect_sound_events(self, audio_path, top_k=3, threshold=0.5):
        """
        Detects sound events in audio using YAMNet with a confidence threshold.

        Parameters:
            audio_path (str): Path to input audio WAV file.
            top_k (int): Number of top class predictions to consider per window (default 3).
            threshold (float): Minimum confidence score to include a detected label (default 0.5).

        Returns:
            List[Dict]: List of detected events with timestamps and labels.
        """

        waveform_np, sr = librosa.load(audio_path, sr=16000, mono=True)
        waveform = torch.tensor(waveform_np, dtype=torch.float32)

        window_size = 16000  # 1s
        hop_size = 8000      # 0.5s overlap
        results = []

        for i, start in enumerate(range(0, len(waveform) - window_size, hop_size)):
            chunk = waveform[start:start + window_size].unsqueeze(0)  # [1, T]
            input_tensor = self.converter(chunk, sr)
            _, scores = self.yamnet_model(input_tensor)
            mean_scores = scores.squeeze(0)  # [classes]

            top_indices = torch.topk(mean_scores, k=top_k).indices

            timestamp = round(start / sr, 2)
            labels = [
                {"label": self.class_names[i], "confidence": float(mean_scores[i])}
                for i in top_indices if mean_scores[i] > threshold
            ]

            if labels:
                results.append({"time": timestamp, "labels": labels})

        return results


    def transcribe_audio(self, audio_path):
        """
        Use OpenAI's whisper model to transcribe speech to text.
        
        Parameters:
            audio_path (str): Path to input audio WAV file.

        Returns:
            List[Tuple[float, float, str]]: List of (start time, end time, text) segments.
        """
        r = self.whisper_model.transcribe(audio_path, language="en")
        segments = r.get("segments", [])
        
        results = [(s["start"], s["end"], s["text"]) for s in segments]
        
        return results
