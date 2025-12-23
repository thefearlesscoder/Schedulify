import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import logo from "../assets/logo.png";

const Register = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        "http://localhost:5000/api/auth/register",
        formData
      );
      localStorage.setItem("token", res.data.token);
      navigate("/dashboard");
    } catch (err) {
      alert(err.response?.data?.msg || "Registration Failed");
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-b from-slate-900 to-slate-950">
      {/* LEFT: FORM */}
      <div className="w-full md:w-1/2 flex items-center justify-center px-6">
        <div className="w-full max-w-md bg-slate-800/60 backdrop-blur-md border border-white/5 rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            Create Account 🚀
          </h2>
          <p className="text-gray-400 mb-8">
            Start generating timetables instantly
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <input
              type="text"
              placeholder="Full Name"
              required
              className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-white/10 text-gray-200 focus:outline-none focus:ring-2 focus:ring-violet-500"
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
            />

            <input
              type="email"
              placeholder="Email address"
              required
              className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-white/10 text-gray-200 focus:outline-none focus:ring-2 focus:ring-violet-500"
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
            />

            <input
              type="password"
              placeholder="Password"
              required
              className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-white/10 text-gray-200 focus:outline-none focus:ring-2 focus:ring-violet-500"
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
            />

            <button
              type="submit"
              className="w-full py-3 rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-semibold transition"
            >
              Register
            </button>
          </form>

          <p className="text-sm text-gray-400 mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-violet-400 hover:text-violet-300">
              Login
            </Link>
          </p>
        </div>
      </div>

      {/* RIGHT: LOGO + TAGLINE */}
      <div className="hidden md:flex w-1/2 items-center justify-center">
        <div className="flex flex-col items-center justify-center space-y-4 px-10">
          <img
            src={logo}
            alt="Logo"
            className="w-72 drop-shadow-[0_0_30px_rgba(139,92,246,0.45)]"
          />
          <p className="text-lg text-gray-300 text-center tracking-wide">
            Automate schedules. Save hours.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
