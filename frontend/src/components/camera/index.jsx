import {
  VideoRecorderCamera,
  VideoRecorderPreviewFrame,
} from "@teamhive/capacitor-video-recorder";

import { Plugins } from "@capacitor/core";
import { useEffect } from "react";
const { VideoRecorder } = Plugins;

const config = {
  id: "video-record",
  stackPosition: "front", // 'front' overlays your app', 'back' places behind your app.
  width: "500",
  height: "500",
  x: 0,
  y: 0,
  borderRadius: "0",
  justifyContent: "center",
};
VideoRecorder.initialize({
  camera: VideoRecorderCamera.FRONT, // Can use BACK
  previewFrames: [config],
});

const CameraComponent = () => {
  const startRecording = async () => {
    await VideoRecorder.startRecording();
  };

  const stopRecording = async () => {
    const result = await VideoRecorder.stopRecording();
    console.log(result);
  };

  useEffect(() => {
    startRecording();
    setTimeout(() => {
      stopRecording();
    }, 5000);
  }, []);
  return (
    <div>
      <video
        id="video-record"
        alt="sad aff"
        style={{ width: "50%", height: "50%" }}
      />
    </div>
  );
};

export default CameraComponent;
