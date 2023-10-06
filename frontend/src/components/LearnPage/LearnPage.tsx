import LessonDetails from "./LessonDetails";
import LessonsList from "./LessonsList";
import QuizDetails from "./QuizDetails";
import { TabList, Tabs, Tab, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";
import QuizesList from "./QuizesList";
import React from "react";

function LearnPage() {
  const [tabIndex, setTabIndex] = React.useState(0);
  return (
    <div className="h-full overflow-y-auto bg-slate-200">
      <Tabs selectedTabClassName="text-white bg-primary rounded-md ">
        <TabList className="my-6 mx-auto flex w-1/2 rounded-lg  border-2 border-primary bg-slate-200 font-semibold text-primary shadow-lg md:w-1/6">
          <Tab className="flex flex-grow cursor-pointer justify-center py-2 ">
            Lessons
          </Tab>
        </TabList>
        <TabPanel>
          <LessonsList />
        </TabPanel>
      </Tabs>
    </div>
  );
}
export default LearnPage;
