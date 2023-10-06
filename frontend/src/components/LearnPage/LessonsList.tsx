import { useEffect, useState } from "react";
import LessonDetails from "./LessonDetails";
import "react-tabs/style/react-tabs.css";

import useGlobalStore from "../../stores/zustand";

function LessonsList() {
  const { fetchLessons, lessons } = useGlobalStore((state) => ({
    lessons: state.lessons,
    fetchLessons: state.fetchLessons,
  }));

  useEffect(() => {
    fetchLessons();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <div className="h-full overflow-y-auto bg-slate-200">
      {Object.keys(lessons).map((lesson) => (
        <LessonDetails words={lessons[lesson]} key={lesson} lesson={lesson} />
      ))}
    </div>
  );
}
export default LessonsList;
