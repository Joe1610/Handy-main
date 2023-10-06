import React, { useState } from "react";
import Button from "@mui/material/Button";
import "./Prediction.css";
type PredictionProps = {
  startRef: React.MutableRefObject<boolean>;
  prediction: string[];
  loading: boolean;
};
function Prediction({ startRef, prediction, loading }: PredictionProps) {
  const [startRecording, setStartRecording] = useState<boolean>(false);
  return (
    <div className="flex h-full flex-col p-2 text-center ">
      <div className=" flex flex-grow flex-col items-center justify-between rounded-xl bg-[#fff6df] text-2xl text-black">
        {prediction.filter((res) => res !== "africa").join(" ")}
      </div>
      <div>
        <Button
          variant="contained"
          onClick={() => {
            setStartRecording((prev) => {
              startRef.current = !prev;
              return !prev;
            });
          }}
          className="w-auto bg-primary"
        >
          {loading ? "Loading" : startRecording ? "Stop" : "Start"}
        </Button>
      </div>
    </div>
  );
}
export default Prediction;
