import { FRAMES_FOR_PREDICTION, labelMap } from "../../utils/index";
import { Results } from "@mediapipe/holistic";
import { NormalizedLandmark } from "@mediapipe/holistic";
import * as tf from "@tensorflow/tfjs";

function chunkArray(arr: any[], chunkSize: number): any[][] {
  const result = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    result.push(arr.slice(i, i + chunkSize));
  }
  return result;
}

function extractKeypoints(results: Results): number[] {
  let lh: number[] = [];
  if (results.leftHandLandmarks) {
    lh = lh.concat(
      ...results.leftHandLandmarks.map((res: NormalizedLandmark) => [
        res.x,
        res.y,
        res.z,
      ])
    );
  } else {
    lh = Array(21 * 3).fill(0);
  }

  let rh: number[] = [];
  if (results.rightHandLandmarks) {
    rh = rh.concat(
      ...results.rightHandLandmarks.map((res: NormalizedLandmark) => [
        res.x,
        res.y,
        res.z,
      ])
    );
  } else {
    rh = Array(21 * 3).fill(0);
  }
  const final = lh.concat(rh);
  return final;
}

export async function startPrediction(
  model: any,
  results: Results[]
): Promise<any[]> {
  if (results && results.length >= FRAMES_FOR_PREDICTION) {
    const filteredResults = results.filter((result) => {
      const extractedKeypoints = extractKeypoints(result);
      const sum = extractedKeypoints.reduce((a, b) => a + b, 0);
      return sum === 0 ? false : true;
    });
    const chunks = chunkArray(filteredResults, FRAMES_FOR_PREDICTION);

    const sequences = chunks
      .map((chunk) => {
        return chunk.map((result) => extractKeypoints(result));
      })
      .filter((seq) => seq.length === FRAMES_FOR_PREDICTION);

    console.log(chunks);

    //use the layers model to predict the gesture and get the confidence score and the label
    if (model) {
      const prediction = model!.predict(tf.tensor3d(sequences)) as tf.Tensor;
      prediction.data().then((data) => {
        const labels = prediction.argMax(-1).dataSync();
        //get the confidence score and the label of each gesture

        for (let i = 0; i < labels.length; i++) {
          console.log({
            word: labelMap[labels[i].toString() as keyof typeof labelMap],
            confidence: data[i],
            labels,
          });
        }
        //console.log(data);

        const array: any = [];
        for (let i = 0; i < labels.length; i++) {
          const word = labelMap[labels[i].toString() as keyof typeof labelMap];
          if (array[array.length - 1] !== word) {
            array.push(word);
          }
        }
        /*setPrediction((prev) => {
            const newSet = [...prev];
            labels.forEach((label: number) => {
              const word = labelMap[label.toString() as keyof typeof labelMap];
              if (newSet[newSet.length - 1] !== word) {
                newSet.push(word);
              }
            });

            return newSet;
          });*/
        return array;
      });
    }
    return [];
  }
  return [];
}
