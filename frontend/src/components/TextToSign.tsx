import TextToSignPlayer from "./TextToSignPlayer";
import { useState, useCallback, useEffect } from "react";
import debounce from "lodash/debounce";

function TextToSign() {
  const [text, setText] = useState<string[]>([]);

  const filterSearchText = (text: string[]) => {
    return text
      .join(" ")
      .replace("the", "")
      .replace("is", " ")
      .replace("dancing", "dance")
      .split(" ")
      .filter((word) => word !== "");
  };
  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setText(e.target.value.split(" "));
    },
    []
  );
  const debouncedHandleSearch = useCallback(debounce(handleSearch, 200), []);

  return (
    <div className="grid h-full w-full grid-cols-1 grid-rows-[8] overflow-hidden md:grid-cols-2 md:grid-rows-1">
      <div
        className="row-span-6   "
        style={{
          maxHeight: "450px",
        }}
      >
        <TextToSignPlayer text={filterSearchText(text)} />
      </div>
      <div
        style={{
          maxHeight: "450px",
        }}
      >
        <textarea
          style={{
            resize: "none",
          }}
          className="textarea  h-full w-full rounded-lg bg-yellow-50 text-2xl font-extrabold text-black"
          placeholder="Enter text to translate"
          onChange={debouncedHandleSearch}
        />
      </div>
    </div>
  );
}
export default TextToSign;
