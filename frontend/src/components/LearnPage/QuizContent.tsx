import TextToSignPlayer from "../TextToSignPlayer";
import ArrowCircleLeftIcon from "@mui/icons-material/ArrowCircleLeft";
import { useNavigate } from "react-router-dom";

function QuizContent() {
  const navigate = useNavigate();
  return (
    <div className="flex h-full flex-col bg-slate-50  ">
      <div className="flex h-1/6 items-center justify-between ">
        <button className="mx-10 text-primary" onClick={() => navigate("/")}>
          <ArrowCircleLeftIcon fontSize="large" />
        </button>
        <h1 className="mx-10 text-lg font-bold text-primary">Quiz 1</h1>
      </div>
      <div className="flex h-4/5 flex-col ">
        <div className=" my-5 mx-auto h-3/5  w-2/3 ">
          <TextToSignPlayer text={["dance"]} />
        </div>
        <div className="mx-auto  flex  h-1/6  items-end">
          <button className="btn mx-2 border-primary bg-primary text-white md:mx-12">
            {" "}
            {"Word 1"}{" "}
          </button>
          <button className="btn mx-2 border-primary bg-primary text-white md:mx-12">
            {" "}
            {"Word 2"}{" "}
          </button>
          <button className="btn mx-2 border-primary bg-primary text-white md:mx-12">
            {" "}
            {"Word 3"}{" "}
          </button>
        </div>
      </div>
    </div>
  );
}
export default QuizContent;
