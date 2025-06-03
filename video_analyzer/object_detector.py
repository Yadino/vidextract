import os
import cv2
import torch
from ultralytics import YOLO
from transformers import Blip2Processor, Blip2ForConditionalGeneration


class ObjectDetector:
    def __init__(self, extract_captions=False):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO("models/yolov8l.pt").to(self.device)     # small & fast

        self.extract_captions = extract_captions        
        if self.extract_captions:
            # Added BLIP2 model for captioning
            self.blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
            self.blip_model = Blip2ForConditionalGeneration.from_pretrained(
                "Salesforce/blip2-flan-t5-xl", torch_dtype=torch.float16
            ).to(self.device)

    def read_frames_from_path(self, directory_path):
        """
        Loads all JPG images from a directory.

        Parameters:
            directory_path (str): Path to folder containing JPG images.

        Returns:
            List[str, np.ndarray]: A list of image frames (as NumPy arrays).
        """
        
        frames = []
        for filename in sorted(os.listdir(directory_path)):
            if filename.lower().endswith('.jpg'):
                full_path = os.path.join(directory_path, filename)
                frame = cv2.imread(full_path)
                if frame is not None:
                    frames.append(frame)
        return frames

    def detect_objects_from_frames(self, frames):
        """
        Detects objects in a list of image frames.

        Parameters:
            frames (List[np.ndarray]): A list of image frames (as NumPy arrays), e.g., extracted from a video.

        Returns:
            List[List[str]]: List of detected object class names per frame.
        """
        detections = []
        for frame in frames:
            results = self.model.predict(frame, device=self.device, verbose=False)[0]
            labels = [self.model.names[int(cls)] for cls in results.boxes.cls]
            detections.append(labels)
        return detections

    def generate_captions_from_frames(self, frames):
        """
        Use BLIP to generate captions.
        """
        if not self.extract_captions:
            return None
        
        captions = []
        for frame in frames:
            from PIL import Image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            outputs = self.blip_model.generate(**inputs)
            caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            captions.append(caption)
        return captions
