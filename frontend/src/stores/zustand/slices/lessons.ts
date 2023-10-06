import { StateCreator } from "zustand";
import { Store } from "..";
import { getLessons } from "../../../services";
import { Lessons } from "../../../types";

export interface LessonSlice {
  lessonInformation: {
    [key: string]: {
      progress: number;
    };
  };
  updateLessonProgress: (lessonName: string, word: string) => void;
  lessons: {
    [key: string]: Array<string>;
  };
  fetchLessons: () => Promise<void>;
}
export const createLessonSlice: StateCreator<Store, [], [], LessonSlice> = (
  set
) => ({
  lessonInformation: {},
  updateLessonProgress: (lessonName, word) => {
    // get the current progress of the lesson
    set((state) => {
      const lessonProgress = state.lessonInformation[lessonName];
      // if the lesson is not in the lessonInformation object, set it to 0
      if (!lessonProgress) {
        return {
          lessonInformation: {
            ...state.lessonInformation,
            [lessonName]: {
              progress: 0,
            },
          },
        };
      }
      // if the lesson is in the lessonInformation object, check if the word is in the lesson
      if (state.lessons[lessonName].includes(word)) {
        // if the word is in the lesson, check if the progress is less than the length of the lesson
        if (lessonProgress.progress < state.lessons[lessonName].length) {
          // if the progress is less than the length of the lesson, increment the progress by 1
          return {
            lessonInformation: {
              ...state.lessonInformation,
              [lessonName]: {
                progress: lessonProgress.progress + 1,
              },
            },
          };
        }
      }
      return state;
    });
  },
  lessons: {},
  fetchLessons: async () => {
    const lessons = await getLessons();
    //sort them by alphabetical order of the lesson name
    const sortedLessons = Object.keys(lessons)
      .sort((a, b) => a.localeCompare(b) || a.length - b.length)
      .reduce((acc: Lessons, key) => {
        acc[key] = lessons[key as keyof typeof lessons];
        return acc;
      }, {});
    set(() => {
      return {
        lessons: sortedLessons,
      };
    });
  },
});
