import { Results } from "@mediapipe/holistic";
import React, { useRef, useState } from "react";

import { MediapipeCamera } from "../MediapipeCamera";
import { PredictType } from "../../types";
import { FRAMES_FOR_PREDICTION } from "../../utils";

//@ts-ignore
import PredictionWorker from "worker-loader!./predictionWorker.ts"; // eslint-disable-line import/no-webpack-loader-syntax

type CameraProps = {
  startRef: React.MutableRefObject<boolean>;
  setPrediction: React.Dispatch<React.SetStateAction<string[]>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
};

const Camera = ({ startRef, setPrediction, setLoading }: CameraProps) => {
  const resultsRef = useRef<PredictType[]>([]);

  const onResults = async (res: Results) => {
    if (startRef.current) {
      resultsRef.current.push({
        leftHandLandmarks: res.leftHandLandmarks,
        rightHandLandmarks: res.rightHandLandmarks,
      });
      //reset the prediction
      //setPrediction([]);
    }
    if (resultsRef.current.length >= FRAMES_FOR_PREDICTION * 1.2) {
      predictFrames(structuredClone(resultsRef.current));
      resultsRef.current = resultsRef.current.slice(FRAMES_FOR_PREDICTION);
    }
  };

  const predictFrames = (frames: PredictType[]) => {
    const framesCopy = [...frames];
    resultsRef.current = [];
    const worker = new PredictionWorker();
    worker.onmessage = function (event: any) {
      const result = event.data;
      console.log(result);
      setPrediction((prev) => [...prev, ...result]);
    };
    worker.postMessage({
      results: framesCopy,
    });
  };
  return (
    <div className="flex h-full flex-col">
      <MediapipeCamera onResult={onResults} />
    </div>
  );
};
export default Camera;
