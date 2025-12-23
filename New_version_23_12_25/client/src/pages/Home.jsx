import { Link, useNavigate } from "react-router-dom";

const Home = () => {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  return (
    <div className="min-h-screen pt-32 px-6 text-center">
      <h1 className="text-5xl font-extrabold text-white mb-6">
        Smart Timetable Generation
      </h1>

      <p className="text-gray-300 max-w-xl mx-auto mb-10">
        Upload CSVs, generate clash-free schedules, and manage everything from
        one dashboard.
      </p>

      {!token ? (
        <div className="flex justify-center gap-6">
          <Link
            to="/login"
            className="px-8 py-3 bg-violet-600 text-white rounded-full"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="px-8 py-3 border border-violet-500 text-violet-400 rounded-full"
          >
            Register
          </Link>
        </div>
      ) : (
        <div className="flex justify-center gap-6">
          <button
            onClick={() => navigate("/dashboard")}
            className="px-8 py-3 bg-violet-600 text-white rounded-xl"
          >
            Generate Timetable
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="px-8 py-3 bg-slate-700 text-white rounded-xl"
          >
            View Previous
          </button>
        </div>
      )}
    </div>
  );
};

export default Home;
