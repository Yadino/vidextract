import os
import cv2
from datetime import datetime
from scenedetect import detect, AdaptiveDetector, ContentDetector, split_video_ffmpeg



class SceneDetector:
    def extract_scenes_by_diff(self, video_path, frame_skip=24, diff_threshold=40):
        """
        Detects scene changes in a video by comparing grayscale frame differences.

        Parameters:
            video_path (str): Path to the input video file.
            frame_skip (int): Number of frames to skip between comparisons. Higher values speed up processing but may miss fast cuts. Default is 24.
            diff_threshold (float): Threshold for average pixel intensity difference to consider a scene change. Default is 30.0.

        Returns:
            List[float]: List of timestamps (in seconds) where scene changes are detected.
        """
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)

            # Get FPS 
            fps = cap.get(cv2.CAP_PROP_FPS)

            prev_frame = None  # Previous frame (grayscale)
            scenes = []  # List of scene change timestamps
            timestamp = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    # Calculate difference
                    diff = cv2.absdiff(gray, prev_frame)
                    avg_diff = diff.mean()

                    if avg_diff > diff_threshold:
                        scenes.append(timestamp)

                prev_frame = gray
                timestamp += frame_skip / fps
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(timestamp * fps))

            return scenes
        finally:
            if cap is not None:
                cap.release()

    def extract_scenes_smart(self, video_path):
        """
        Use scenedetect's ContentDetector to extract changing shots.
        
            video_path (str): Path to the input video file.
        
        Returns:
            List[float]: List of timestamps (in seconds) of the middle of each detected scene.
        """
    
        scene_list = detect(video_path, ContentDetector())
                
        # Get the middle of a scene which is the beginning + ((end - beginning) / 2)
        seconds_middle = [scene[0].get_seconds() + (scene[1].get_seconds() - scene[0].get_seconds()) / 2.0 for scene in scene_list]
        
        return(self.frames_by_seconds(video_path, seconds_middle))

    
    def frames_by_seconds(self, video_path, seconds):
        """
        Extracts raw frames at given timestamps.

        Parameters:
            video_path (str): Path to video.
            seconds (List[float]): Timestamps in seconds.

        Returns:
            List[Tuple[float, np.ndarray]]: (timestamp, frame) pairs.
        """
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []

            for t in seconds:
                cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
                ret, frame = cap.read()
                if ret:
                    frames.append((t, frame))

            return frames
        finally:
            if cap is not None:
                cap.release()

    def save_frames(self, video_path, frames, output_root="output"):
        """
        Saves (timestamp, frame) pairs as image files.

        Parameters:
            frames (List[Tuple[float, np.ndarray]]): Frames to save.
            video_path (str): Used for naming output folder.
            output_root (str): Output folder root.
        """
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        run_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_root, f"{video_name}_{run_time}")
        os.makedirs(output_dir, exist_ok=True)

        for t, frame in frames:
            filename = os.path.join(output_dir, f"{t:.2f}s.jpg")
            cv2.imwrite(filename, frame)

