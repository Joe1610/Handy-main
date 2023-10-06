import { useLocation, useNavigate } from "react-router-dom";
import LearnIcon from "./Icons/LearnIcon";
import HomeIcon from "./Icons/HomeIcon";
import TranslateIcon from "./Icons/TranslateIcon";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const iconWithLabel = (Icon: any, label: any, path: any) => {
    const active = location.pathname.includes(path);
    return (
      <div
        className={`mt-3 flex flex-col items-center hover:cursor-pointer ${
          active ? "opacity-100" : "opacity-50"
        }`}
        onClick={() => navigate(path)}
      >
        <Icon active={active} />

        <span className={`ms-2 mt-1 font-bold text-primary `}>{label}</span>
      </div>
    );
  };
  return (
    <div className=" flex w-full  justify-around rounded-t-2xl bg-white py-2 px-9 shadow-2xl">
      {/* {iconWithLabel(HomeIcon, "Home", "/")} */}
      {iconWithLabel(LearnIcon, "Learn", "/learn")}
      {iconWithLabel(TranslateIcon, "Translate", "/translate")}
      {/* {iconWithLabel(LearnIcon, "Settings", "/")} */}
    </div>
  );
};

export default Navbar;
