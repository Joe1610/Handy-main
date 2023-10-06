import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import { IconButton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import useGlobalStore from "../../stores/zustand";

interface LessonDetailsProps {
  lesson: string;
  words: Array<string>;
}
function LessonDetails({ lesson }: LessonDetailsProps) {
  const lessonProgress = useGlobalStore(
    (state) => state.lessonInformation[lesson]?.progress ?? 0
  );
  const navigate = useNavigate();
  return (
    <div
      onClick={() => navigate(`lesson/${lesson}`)}
      className="mx-auto my-5 flex h-12 w-3/4 cursor-pointer items-center justify-between rounded-lg bg-primary text-lg font-semibold text-white md:w-1/2"
    >
      <div className="ml-5">{lesson}</div>
      <div className="mr-2">
        <span>{lessonProgress}% </span>
        <IconButton style={{ color: "#ffffff" }}>
          <PlayCircleIcon fontSize="small" />
        </IconButton>
      </div>
    </div>
  );
}
export default LessonDetails;
