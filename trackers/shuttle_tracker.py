from inference_scripts.wasb_inference import run_inference as wasb_inference
import cv2
import pickle
import numpy as np
import pandas as pd
# Map models to their corresponding inference functions, I am using only wasb, if needed more we can add here check out WASB gitHub repo
MODEL_INFERENCE_MAP = {
    "wasb": wasb_inference
}

class ShuttleTracker:
    def __init__(self, model_path):
        self.model_path = model_path
        self.__inference_function = MODEL_INFERENCE_MAP["wasb"]
        self.__is_interpolated = False

    def get_hit_frame(self, shuttle_detections):
        if not self.__is_interpolated:
            print("LOG : dataset contain NaN values")
            return shuttle_detections
        DIRECTIONS = {0: "Steady", 1: "Upper Court", 2: "Bottom Court"}
        pass

    def get_ball_positions(self, input_path, read_from_stub=False, stub_path=None):
        if not read_from_stub:
            ball_detections = self.__inference_function(weights=self.model_path, input_path=input_path)
            if stub_path:
                with open(stub_path, 'wb') as f:
                    # noinspection PyTypeChecker
                    pickle.dump(ball_detections, f)
        else:
            if not stub_path:
                raise Exception("Stub path missing")
            with open(stub_path, 'rb') as f:
                ball_detections = pickle.load(f)
        return ball_detections

    def draw_circle(self, video_frames, shuttle_detections, is_interpolated=True):
        self.__is_interpolated = True
        for frame, shuttle_detection in zip(video_frames, shuttle_detections):
            frame_num, is_detected, x, y, cnf = shuttle_detection
            if is_interpolated or is_detected:
                cv2.circle(frame,[int(x), int(y)], radius=5, color=(255, 255, 255), thickness=2)
            cv2.putText(frame, f"Confidence of shuttle detection: {round(cnf, 2)}", (800, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def interpolate_shuttle_position(self, shuttle_detections):
        np_shuttle_detections = np.array(shuttle_detections, dtype=np.float32)
        np_shuttle_detections[np_shuttle_detections[:, 1] == 0, 2:4] = np.nan
        shuttle_detections_df = pd.DataFrame(np_shuttle_detections)
        shuttle_detections_df = shuttle_detections_df.bfill(axis=0)
        shuttle_detections_df.to_csv("dfo.csv", index=False)
        shuttle_detections_df[2] = shuttle_detections_df[2].interpolate()
        shuttle_detections_df[3] = shuttle_detections_df[3].interpolate()
        np_shuttle_detections = shuttle_detections_df.to_numpy()
        shuttle_detections_df.to_csv("dfm.csv", index=False)
        self.__is_interpolated = True
        return np_shuttle_detections.tolist()






