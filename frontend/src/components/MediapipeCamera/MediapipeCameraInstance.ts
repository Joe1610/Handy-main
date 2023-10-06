import * as Holistic from "@mediapipe/holistic";

let cachedHolistic: Holistic.Holistic | null = null;
const config = {
  locateFile: (file: any) => {
    return `/holistic/${file}`;
  },
};
export function getMediapipeInstance(): Holistic.Holistic {
  if (cachedHolistic === null) {
    cachedHolistic = new Holistic.Holistic(config);
  }

  return cachedHolistic;
}

export function releaseMediapipeInstance(): void {
  if (cachedHolistic) {
    // Cleanup if needed
  }
}
