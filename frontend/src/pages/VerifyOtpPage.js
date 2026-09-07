import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AlertCircle, ArrowLeft, Mail } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import * as authService from "../services/authService";
import { getErrorMessage } from "../utils/helpers";

function maskEmail(email) {
  if (!email || !email.includes("@")) return "your email address";
  const [local, domain] = email.split("@");
  return `${local.slice(0, 1)}${"*".repeat(Math.max(1, local.length - 1))}@${domain}`;
}

export default function VerifyOtpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { verifyRegistration } = useAuth();
  const inputs = useRef([]);
  const [email] = useState(() => sessionStorage.getItem("nyayaai_pending_email") || "");
  const [maskedEmail, setMaskedEmail] = useState(location.state?.maskedEmail || maskEmail(email));
  const [digits, setDigits] = useState(["", "", "", ""]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => { inputs.current[0]?.focus(); }, []);
  useEffect(() => {
    if (!cooldown) return undefined;
    const timer = window.setInterval(() => setCooldown((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [cooldown]);

  const updateDigit = (index, value) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    setDigits((current) => current.map((item, itemIndex) => itemIndex === index ? digit : item));
    if (digit && index < 3) inputs.current[index + 1]?.focus();
  };

  const handleKeyDown = (index, event) => {
    if (event.key === "Backspace" && !digits[index] && index > 0) inputs.current[index - 1]?.focus();
  };

  const handlePaste = (event) => {
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 4);
    if (!pasted) return;
    event.preventDefault();
    setDigits([0, 1, 2, 3].map((index) => pasted[index] || ""));
    inputs.current[Math.min(pasted.length, 4) - 1]?.focus();
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    if (!email) { setError("No pending email verification found."); return; }
    const otp = digits.join("");
    if (!/^\d{4}$/.test(otp)) { setError("Please enter the 4-digit verification code."); return; }
    setLoading(true);
    try {
      await verifyRegistration(email, otp);
      sessionStorage.removeItem("nyayaai_pending_email");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally { setLoading(false); }
  };

  const resend = async () => {
    if (!email || cooldown) return;
    setError("");
    setResending(true);
    try {
      const response = await authService.resendOtp(email);
      setMaskedEmail(response.data.data.email);
      setDigits(["", "", "", ""]);
      setCooldown(60);
      inputs.current[0]?.focus();
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setResending(false); }
  };

  if (!email) return (
    <div className="text-center py-6">
      <Mail size={32} className="mx-auto text-navy-600 mb-4" />
      <h2 className="text-2xl font-bold text-navy-600">No Pending Verification</h2>
      <p className="text-gray-500 text-sm mt-2 mb-6">No pending email verification found.</p>
      <Link to="/register" className="btn-primary inline-flex px-5 py-2.5 rounded-xl">Back to Registration</Link>
    </div>
  );

  return (
    <>
      <div className="text-center mb-7">
        <div className="w-12 h-12 rounded-2xl bg-navy-50 text-navy-600 flex items-center justify-center mx-auto mb-4"><Mail size={22} /></div>
        <p className="section-label">Email Verification</p>
        <h2 className="text-2xl font-bold text-navy-600">Verify Your Email</h2>
        <p className="text-gray-500 text-sm mt-2">We've sent a 4-digit verification code to</p>
        <p className="text-navy-600 font-semibold text-sm mt-1">{maskedEmail}</p>
      </div>
      {error && <div className="mb-5 flex items-start gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm"><AlertCircle size={16} className="shrink-0 mt-0.5" /><span>{error}</span></div>}
      <form onSubmit={submit}>
        <div className="flex justify-center gap-3 mb-6" onPaste={handlePaste}>
          {digits.map((digit, index) => <input key={index} ref={(element) => { inputs.current[index] = element; }} value={digit} onChange={(event) => updateDigit(index, event.target.value)} onKeyDown={(event) => handleKeyDown(index, event)} inputMode="numeric" pattern="[0-9]*" maxLength={1} aria-label={`Verification digit ${index + 1}`} className="w-12 h-14 text-center text-xl font-bold text-navy-600 border-2 border-gray-200 rounded-xl focus:border-gold-400 focus:outline-none" />)}
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full py-3 rounded-xl">{loading ? <><span className="spinner" /> Verifying...</> : "Verify & Continue"}</button>
      </form>
      <div className="text-center mt-6 space-y-3">
        <button type="button" onClick={resend} disabled={resending || cooldown > 0} className="text-sm font-semibold text-navy-600 disabled:text-gray-400">{resending ? "Sending..." : cooldown ? `Resend available in ${cooldown} seconds.` : "Resend OTP"}</button>
        <Link to="/register" className="flex items-center justify-center gap-1 text-sm text-gray-500 hover:text-navy-600"><ArrowLeft size={14} /> Change email</Link>
      </div>
    </>
  );
}
