import useGlobalStore from "../../stores/zustand";
import Camera from "../TranslatePage/Camera";
import { useRef, useState } from "react";
function LessonTest({ word, lesson }: { word: string; lesson: string }) {
  const startRef = useRef<boolean>(true);
  const updateLessonProgress = useGlobalStore(
    (state) => state.updateLessonProgress
  );

  const [prediction, setPrediction] = useState<Array<string>>([]);

  console.log(prediction);

  const checkSign = () => {
    if (prediction.includes(word)) {
      updateLessonProgress(lesson, word);
      return true;
    }
    return false;
  };

  return (
    <div className="flex h-full w-full flex-col">
      <Camera
        startRef={startRef}
        setPrediction={setPrediction}
        setLoading={() => {}}
      />
      {prediction.length ? (
        checkSign() ? (
          <div className="flex justify-center text-2xl font-bold text-green-500">
            You are correct
          </div>
        ) : (
          <div className="flex justify-center text-2xl font-bold text-red-600">
            You are wrong
          </div>
        )
      ) : (
        <div className="flex justify-center">Start making the sign</div>
      )}
    </div>
  );
}
export default LessonTest;
