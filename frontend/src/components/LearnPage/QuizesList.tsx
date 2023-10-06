import QuizDetails from "./QuizDetails";
import { TabList, Tabs, Tab, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";

function QuizesList() {
  return (
    <div className="h-full overflow-y-auto bg-slate-200">
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
      <QuizDetails />
    </div>
  );
}
export default QuizesList;
