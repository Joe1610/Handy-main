import React, { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import SignToText from "./components/SignToText";
import TextToSign from "./components/TextToSign";
import FormatBar from "./components/TranslatePage/FormatBar";
import LessonsList from "./components/LearnPage/LessonsList";
import LessonContent from "./components/LearnPage/LessonContent";
import LessonDetails from "./components/LearnPage/LessonDetails";
import LearnPage from "./components/LearnPage/LearnPage";
import QuizContent from "./components/LearnPage/QuizContent";
import Navbar from "./components/NavBar";
import TranslatePage from "./components/TranslatePage";
import useGlobalStore from "./stores/zustand";
import { getMediapipeInstance } from "./components/MediapipeCamera/MediapipeCameraInstance";

const App = () => {
  const fetchLessons = useGlobalStore((state) => state.fetchLessons);
  const [loading, setLoading] = React.useState(true);
  const initApp = async () => {
    setLoading(true);
    await fetchLessons();
    getMediapipeInstance();
    setLoading(false);
  };
  useEffect(() => {
    initApp();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }
  return (
    <div className="main-background flex h-screen w-screen flex-grow flex-col overflow-y-hidden bg-slate-200 ">
      <BrowserRouter>
        <div className="flex flex-grow flex-col overflow-auto p-2">
          <Routes>
            <Route path="/learn" element={<LearnPage />} />
            <Route path="learn/lesson/:lesson" element={<LessonContent />} />
            {/* <Route path="/quiz" element={<QuizContent />} /> */}
            <Route path="/translate" element={<TranslatePage />} />
            <Route path="/texttosign" element={<TextToSign />} />
          </Routes>
        </div>
        <Navbar />
      </BrowserRouter>
    </div>
  );
};

export default App;
