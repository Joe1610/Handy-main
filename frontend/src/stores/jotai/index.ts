import { atom } from "jotai";
import { LayersModel } from "@tensorflow/tfjs";

export const isHereAtom = atom(false);

export const modelAtom = atom<undefined | LayersModel>(undefined);
