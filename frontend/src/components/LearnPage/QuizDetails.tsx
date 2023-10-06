import PlayCircleFilledWhiteIcon from "@mui/icons-material/PlayCircleFilledWhite";
import { IconButton } from "@mui/material";
import { useNavigate } from "react-router-dom";
function QuizDetails() {
  const navigate = useNavigate();
  return (
    <div
      onClick={() => navigate("/quiz")}
      className="mx-auto my-5 flex h-12 w-3/4 cursor-pointer items-center justify-between rounded-lg bg-primary text-lg font-semibold text-white md:w-1/2"
    >
      <div className="ml-5">Quiz 1</div>
      <div className="mr-2">
        <span>94% </span>
        <IconButton style={{ color: "#ffffff" }}>
          <PlayCircleFilledWhiteIcon fontSize="small" />
        </IconButton>
      </div>
    </div>
  );
}
export default QuizDetails;
