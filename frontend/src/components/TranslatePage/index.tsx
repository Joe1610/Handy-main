import { useState } from "react";
import SigntoText from "../SignToText";
import FormatBar from "./FormatBar";
import TextToSign from "../TextToSign";

const TranslatePage = () => {
  const [translationDirection, setTranslationDirection] = useState<
    "signToText" | "textToSign"
  >("signToText");
  return (
    <div className="flex flex-grow flex-col">
      <FormatBar
        setTranslationDirection={setTranslationDirection}
        translationDirection={translationDirection}
      />
      {translationDirection === "signToText" ? <SigntoText /> : <TextToSign />}
    </div>
  );
};

export default TranslatePage;
