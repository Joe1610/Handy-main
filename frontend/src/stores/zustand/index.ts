import create from "zustand";

import { persist, devtools } from "zustand/middleware";

import { LessonSlice, createLessonSlice } from "./slices/lessons";

export type Store = LessonSlice;

export const useGlobalStore = create<Store>()(
  devtools(
    persist(
      (...a) => ({
        ...createLessonSlice(...a),
      }),
      {
        name: "data", // name of item in the storage (must be unique)
        partialize: (state) => ({
          lessonInformation: state.lessonInformation,
        }), // only persist the user slice
      }
    )
  )
);
export default useGlobalStore;
