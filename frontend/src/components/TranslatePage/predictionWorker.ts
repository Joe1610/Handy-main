import { Results, NormalizedLandmark } from "@mediapipe/holistic";
import { FRAMES_FOR_PREDICTION, labelMap } from "../../utils/index";
import * as tf from "@tensorflow/tfjs";
import { PredictType } from "../../types";

function chunkArray(arr: any[], chunkSize: number): any[][] {
  const result = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    result.push(arr.slice(i, i + chunkSize));
  }
  return result;
}

function extractKeypoints(results: PredictType): number[] {
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
let model: tf.LayersModel | null = null;
async function startPrediction(results: PredictType[]): Promise<string[]> {
  tf.setBackend("cpu");
  if (!model) {
    console.log("loading model");
    console.time("model");
    model = await tf.loadLayersModel("/model.json");
    console.timeEnd("model");
  }
  if (results && results.length >= FRAMES_FOR_PREDICTION) {
    //we have an array that have FRAMES_FOR_PREDICTION * 1.5
    // we want to have am array that have permutations of results of size FRAMES_FOR_PREDICTION

    const filteredResults = results.filter((result) => {
      const extractedKeypoints = extractKeypoints(result);
      const sum = extractedKeypoints.reduce((a, b) => a + b, 0);
      return sum === 0 ? false : true;
    });

    const sequences = filteredResults
      .map((_, i) => {
        return results
          .slice(i, i + FRAMES_FOR_PREDICTION)
          .map((result) => extractKeypoints(result));
      })
      .filter((seq) => seq.length === FRAMES_FOR_PREDICTION);

    // const chunks = chunkArray(filteredResults, FRAMES_FOR_PREDICTION);

    // const sequences = chunks
    //   .map((chunk) => {
    //     return chunk.map((result) => extractKeypoints(result));
    //   })
    //   .filter((seq) => seq.length === FRAMES_FOR_PREDICTION);

    //use the layers model to predict the gesture and get the confidence score and the label
    if (model) {
      const prediction = model!.predict(tf.tensor3d(sequences)) as tf.Tensor;
      //get the label with the highest confidence score\
      const labels = Array.from(prediction.argMax(1).dataSync());
      const data = Array.from(prediction.dataSync());
      //get the confidence score of each label
      const confidenceScores = chunkArray(data, sequences.length).map((arr) =>
        Math.max(...arr)
      );
      const res = labels.map((label, i) => {
        return {
          label: labelMap[label.toString() as keyof typeof labelMap],
          confidenceScore: confidenceScores[i],
        };
      });

      //get the label with the highest confidence score
      const word = res.reduce((prev, current) =>
        prev.confidenceScore > current.confidenceScore ? prev : current
      );
      return [word.label];
    }

    return [];
  }
  return [];
}

/*eslint-disable no-restricted-globals */
self.onmessage = function (event) {
  const data = event.data;
  const { results } = data;
  startPrediction(results).then((res) => {
    self.postMessage(res);
  });
};
