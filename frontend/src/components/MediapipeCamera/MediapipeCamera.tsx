import React, { useRef, useEffect, useState, useMemo } from "react";
import { Switch, Space, Upload } from "antd";
import { UploadChangeParam, UploadFile } from "antd/es/upload";
import { connect, draw } from "../../utils";
import * as Holistic from "@mediapipe/holistic";
import * as drawingUtils from "@mediapipe/drawing_utils";
import {
  getMediapipeInstance,
  releaseMediapipeInstance,
} from "./MediapipeCameraInstance";

let holistic: Holistic.Holistic | null = null;

const dummyRequest = ({ file, onSuccess }: any) => {
  setTimeout(() => {
    onSuccess("ok");
  }, 0);
};

function MediapipeCamera({
  onResult,
}: {
  onResult: (results: Holistic.Results) => void;
}) {
  const [uploadedVideo, setUploadedVideo] = useState<any>(null);
  const [useCamera, setUseCamera] = useState<boolean>(true);
  const canvasRef = useRef<null | HTMLCanvasElement>(null);
  const cameraRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<any>(null);

  const onMediapipeResults = (results: Holistic.Results): void => {
    onResult(results);
    if (!canvasRef.current) return;
    const canvasCtx = canvasRef.current.getContext("2d");
    if (!canvasCtx) return;
    draw(canvasCtx, results);
  };

  useEffect(() => {
    async function initHolistic() {
      holistic = getMediapipeInstance();
      //   await holistic.initialize();
      holistic.setOptions({
        smoothLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });
      holistic.onResults(onMediapipeResults);
    }
    initHolistic();

    return () => {
      //   releaseMediapipeInstance();
      //   holistic = null;
    };
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    const onFrame = () => {
      const renderCanvas = async () => {
        if (!videoRef.current || !holistic || video.paused || video.ended)
          return;

        await holistic.send({ image: video });

        requestAnimationFrame(renderCanvas);
      };
      renderCanvas();
    };

    async function startCamera() {
      cameraRef.current = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: "user",
          width: 640,
          height: 480,
        },
      });

      console.log({
        facingMode: cameraRef.current !== null,
      });

      if (videoRef.current && useCamera) {
        videoRef.current.srcObject = cameraRef.current;
      } else {
        if (videoRef.current) videoRef.current.srcObject = null;
        if (canvasRef.current) {
          const canvasCtx = canvasRef.current.getContext("2d");
          if (!canvasCtx) return;
          canvasCtx.save();
          canvasCtx.clearRect(
            0,
            0,
            canvasCtx.canvas.width,
            canvasCtx.canvas.height
          );
        }

        if (videoRef.current) videoRef.current.src = uploadedVideo;
      }
    }
    startCamera();

    video.addEventListener("play", onFrame);

    return () => {
      video.removeEventListener("play", onFrame);
      // turn off camera
      if (cameraRef.current) {
        cameraRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [useCamera, uploadedVideo]);

  const handleChange = (info: UploadChangeParam<UploadFile<any>>) => {
    const file = info.file;
    if (!file.originFileObj) return;
    const url = URL.createObjectURL(file.originFileObj);
    setUploadedVideo(url);
  };

  return (
    <div className="flex flex-grow  flex-col items-center justify-center rounded-xl ">
      <canvas
        className="flex aspect-video h-full rounded-xl"
        style={{
          maxWidth: "100%",
          maxHeight: "100%",
        }}
        ref={canvasRef}
      />

      <div style={{ marginTop: "3px" }}>
        <Space
          className="switch"
          direction="vertical"
          onClick={() => {
            setUseCamera((prev) => !prev);
          }}
        >
          <Switch
            checkedChildren="Video"
            unCheckedChildren="Camera"
            className="bg-primary text-primary"
          />
        </Space>
        {!useCamera && (
          <Upload
            className="mt-3 mb-3"
            accept=".mp4"
            maxCount={1}
            customRequest={dummyRequest}
            onChange={handleChange}
            onRemove={() => {
              console.log("remove");
              setUploadedVideo(null);
              videoRef.current.srcObject = null;
              videoRef.current.src = null;
            }}
          >
            <button className="upload-button">Upload</button>
          </Upload>
        )}
      </div>
      <video
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "0px ",
          height: "0px",
        }}
        ref={videoRef}
        src={uploadedVideo}
        muted
        loop
        autoPlay={true}
      />
    </div>
  );
}

export { MediapipeCamera };
