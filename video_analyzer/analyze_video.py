import os
import json
import sys
from pathlib import Path

# Try relative imports first (when running as a package)
try:
    from .scene_detector import SceneDetector
    from .object_detector import ObjectDetector
    from .audio_detector import AudioDetector
    from .prompts import PROMPT_TEMPLATE
except ImportError:
    # If that fails, try absolute imports (when running directly)
    sys.path.append(str(Path(__file__).parent.parent))
    from scene_detector import SceneDetector
    from object_detector import ObjectDetector
    from audio_detector import AudioDetector
    from prompts import PROMPT_TEMPLATE

from openai import OpenAI

class AnalyzeVideo:
    def __init__(self, api_key, model_name, output_dir):
        """
        Initialize the video analyzer with configuration parameters.
        
        Parameters:
            api_key (str): OpenAI API key
            model_name (str): Name of the OpenAI model to use
            output_dir (str): Directory for saving output files
        """
        self.scene_detector = SceneDetector()
        self.object_detector = ObjectDetector()
        self.audio_detector = AudioDetector()
        self.api_key = api_key
        self.model = model_name
        self.output_dir = output_dir
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def process_video(self, video_path):
        # 1. Extract frames from scenes
        frames_info = self.scene_detector.extract_scenes_smart(video_path)
        frame_times, frames = map(list, zip(*frames_info))
        
        # 2. Process frames for object detection and captions
        object_labels = self.object_detector.detect_objects_from_frames(frames)
        captions = self.object_detector.generate_captions_from_frames(frames)

        # 3. Process audio
        audio_file = self.audio_detector.extract_audio(video_path)
        sound_events = self.audio_detector.detect_sound_events(audio_file)
        transcript = self.audio_detector.transcribe_audio(audio_file)

        return {
            "frame_times": frame_times,
            "object_labels": object_labels,
            "captions": captions,
            "sound_events": sound_events,
            "transcript": transcript
        }

    def get_summary_as_json(self, results, video_path, save=True):
        # Get video filename without extension
        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        
        # Prepare the JSON structure
        json_data = {
            "video_name": os.path.basename(video_path),
            "number_of_shots": len(results['frame_times']),
            "shots": [
                {
                    "time": float(f"{time:.2f}"),
                    "objects": labels,
                    "caption": caption if results['captions'] else None
                }
                for time, labels, caption in zip(
                    results['frame_times'],
                    results['object_labels'],
                    results['captions'] if results['captions'] else [None] * len(results['frame_times'])
                )
            ],
            "sound_events": [
                {
                    "time": float(f"{event['time']:.2f}"),
                    "labels": [
                        {
                            "label": label['label'],
                            "confidence": float(f"{label['confidence']:.2f}")
                        }
                        for label in event['labels']
                    ]
                }
                for event in results['sound_events']
            ],
            "transcript": [
                {
                    "start_time": float(f"{start:.2f}"),
                    "end_time": float(f"{end:.2f}"),
                    "text": text
                }
                for start, end, text in results['transcript']
            ]
        }
        
        if save:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save to JSON file
            output_path = os.path.join(self.output_dir, f"{video_filename}_analysis.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nAnalysis saved to: {output_path}")
        
        return json_data

    def prepare_llm_prompt(self, json_data):
        """
        Prepares a prompt for the LLM based on the analysis results.
        
        Parameters:
            json_data (dict): The analysis results in JSON format
            
        Returns:
            str: The formatted prompt for the LLM
        """
        # Convert the JSON data to a minified string
        json_schema = json.dumps(json_data, separators=(',', ':'))
        
        # Format the prompt template with the JSON schema
        prompt = PROMPT_TEMPLATE.format(json_schema=json_schema)
        
        return prompt

    def get_llm_analysis(self, json_data):
        """
        Get analysis from OpenAI LLM using the prepared prompt and JSON data.
        
        Parameters:
            json_data (dict): The analysis results in JSON format
            
        Returns:
            dict: The LLM's analysis in JSON format
        """
        # Prepare the prompt
        prompt = self.prepare_llm_prompt(json_data)
        
        try:
            # Generate content using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes video content and returns results in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            # Parse the response text as JSON
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error getting LLM analysis: {str(e)}")
            return None 