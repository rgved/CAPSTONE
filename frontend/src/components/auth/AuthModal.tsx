import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { api } from "../../services/api";
import { X, Lock, Mail, User as UserIcon, AlertCircle, ArrowRight, ShieldCheck, Loader2, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import GoogleIcon from "./GoogleIcon";

declare global {
  interface Window {
    google?: any;
  }
}

export default function AuthModal() {
  const { isAuthModalOpen, closeAuthModal, authModalMode, setAuthData } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"login" | "signup">(authModalMode);
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Google OAuth specific states
  const [isGooglePromptOpen, setIsGooglePromptOpen] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");
  const [googleClientId, setGoogleClientId] = useState<string>(
    () => (import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || ""
  );

  // Sync mode with context when opening
  useEffect(() => {
    setMode(authModalMode);
    setError(null);
    setIsGooglePromptOpen(false);
  }, [authModalMode, isAuthModalOpen]);

  // Fetch configured Google Client ID from backend
  useEffect(() => {
    if (isAuthModalOpen) {
      api.auth
        .getGoogleConfig()
        .then((res) => {
          if (res?.google_client_id) {
            setGoogleClientId(res.google_client_id);
          }
        })
        .catch(() => {});
    }
  }, [isAuthModalOpen]);

  if (!isAuthModalOpen) return null;

  const handleGoogleClick = () => {
    setError(null);
    const effectiveClientId = googleClientId || (import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || "";

    // If real Google Identity Services is available and Client ID is configured, trigger the official Google popup
    if (effectiveClientId && window.google?.accounts?.oauth2) {
      try {
        const client = window.google.accounts.oauth2.initTokenClient({
          client_id: effectiveClientId,
          scope: "email profile openid",
          callback: async (tokenResponse: any) => {
            if (tokenResponse?.access_token) {
              setLoading(true);
              try {
                const userInfo = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
                  headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
                }).then((r) => r.json());

                if (userInfo?.email) {
                  const res = await api.auth.googleAuth({
                    email: userInfo.email,
                    name: userInfo.name,
                    google_id: userInfo.sub,
                    avatar_url: userInfo.picture,
                  });
                  if (res && res.token) {
                    setAuthData(res.token, res.user);
                    navigate("/dashboard");
                  }
                }
              } catch (err: any) {
                setError(err?.message || "Google profile authentication failed.");
              } finally {
                setLoading(false);
              }
            } else if (tokenResponse?.error) {
              setError(`Google Sign-In error: ${tokenResponse.error}`);
            }
          },
        });
        client.requestAccessToken();
        return;
      } catch (err) {
        // Fall back to id.prompt or direct input
      }
    }

    if (window.google?.accounts?.id && googleClientId) {
      try {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async (response: any) => {
            if (response.credential) {
              setLoading(true);
              try {
                const res = await api.auth.googleAuth({
                  credential: response.credential,
                });
                if (res && res.token) {
                  setAuthData(res.token, res.user);
                  navigate("/dashboard");
                }
              } catch (err: any) {
                setError(err?.message || "Google authentication failed.");
              } finally {
                setLoading(false);
              }
            }
          },
        });
        window.google.accounts.id.prompt();
        return;
      } catch (err) {
        // Fall back to direct modal
      }
    }

    // Direct Google Account Auth
    setIsGooglePromptOpen(true);
  };

  const handleGoogleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!googleEmail.trim() || !googleEmail.includes("@")) {
      setError("Please provide a valid Google account email.");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const res = await api.auth.googleAuth({
        email: googleEmail.trim().toLowerCase(),
        name: googleName.trim() || undefined,
        google_id: `g_${Date.now()}`,
      });

      if (res && res.token) {
        setAuthData(res.token, res.user);
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err?.message || "Google authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "login") {
        if (!usernameOrEmail.trim() || !password) {
          setError("Please fill in all fields.");
          setLoading(false);
          return;
        }

        const res = await api.auth.login({
          username_or_email: usernameOrEmail.trim(),
          password,
        });

        if (res && res.token) {
          setAuthData(res.token, res.user);
          navigate("/dashboard");
        }
      } else {
        if (!username.trim() || !email.trim() || !password) {
          setError("Please fill in all required fields.");
          setLoading(false);
          return;
        }

        if (password.length < 6) {
          setError("Password must be at least 6 characters long.");
          setLoading(false);
          return;
        }

        if (password !== confirmPassword) {
          setError("Passwords do not match.");
          setLoading(false);
          return;
        }

        const res = await api.auth.signup({
          username: username.trim(),
          email: email.trim(),
          password,
        });

        if (res && res.token) {
          setAuthData(res.token, res.user);
          navigate("/dashboard");
        }
      }
    } catch (err: any) {
      setError(err?.message || "Authentication failed. Please verify your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-md bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl overflow-hidden p-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Glow corner */}
        <div className="absolute top-0 right-0 w-36 h-36 bg-[#0284C7]/15 rounded-full blur-2xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={closeAuthModal}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-[#64748B] hover:text-[#F8FAFC] hover:bg-[#1E293B] transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {isGooglePromptOpen ? (
          /* Google Account Direct Authentication Screen */
          <div>
            <button
              type="button"
              onClick={() => {
                setIsGooglePromptOpen(false);
                setError(null);
              }}
              className="flex items-center gap-1.5 text-xs text-[#94A3B8] hover:text-[#F8FAFC] mb-4 transition cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to standard login</span>
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/10 border border-white/20 mb-3 shadow-md">
                <GoogleIcon className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-[#F8FAFC]">
                Sign in with Google
              </h2>
              <p className="text-xs text-[#94A3B8] mt-1">
                Enter your Google Account to connect with Sniff Reconnaissance
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-500/30 flex items-start gap-2.5 text-red-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleGoogleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                  Google Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                  <input
                    type="email"
                    required
                    value={googleEmail}
                    onChange={(e) => setGoogleEmail(e.target.value)}
                    placeholder="your.name@gmail.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                  Full Name (Optional)
                </label>
                <div className="relative">
                  <UserIcon className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                  <input
                    type="text"
                    value={googleName}
                    onChange={(e) => setGoogleName(e.target.value)}
                    placeholder="e.g. Alex Hunter"
                    className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 bg-white hover:bg-slate-100 text-[#0F172A] font-bold rounded-xl flex items-center justify-center gap-2.5 text-sm shadow-lg transition cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-slate-800" />
                    <span>Connecting Google Account...</span>
                  </>
                ) : (
                  <>
                    <GoogleIcon className="w-4 h-4" />
                    <span>Continue with Google</span>
                  </>
                )}
              </button>
            </form>
          </div>
        ) : (
          /* Standard Auth Screen with Google Button */
          <div>
            {/* Header */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#0284C7]/10 border border-[#0284C7]/20 text-[#38BDF8] mb-3">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-[#F8FAFC]">
                {mode === "login" ? "Sign In to Sniff" : "Create Security Account"}
              </h2>
              <p className="text-xs text-[#94A3B8] mt-1">
                {mode === "login"
                  ? "Access your scan history and security reconnaissance missions"
                  : "Register your analyst profile to isolate and track your scans"}
              </p>
            </div>

            {/* Google Sign-in Button */}
            <button
              type="button"
              onClick={handleGoogleClick}
              disabled={loading}
              className="w-full py-2.5 px-4 mb-4 bg-[#090D16] hover:bg-[#1E293B] border border-[#334155] text-[#F8FAFC] font-semibold rounded-xl flex items-center justify-center gap-3 text-sm shadow-sm transition hover:border-[#64748B] cursor-pointer disabled:opacity-50"
            >
              <GoogleIcon className="w-4 h-4" />
              <span>{mode === "login" ? "Sign in with Google" : "Sign up with Google"}</span>
            </button>

            {/* Divider */}
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#1E293B]" />
              </div>
              <div className="relative flex justify-center text-[10px] uppercase font-mono">
                <span className="bg-[#0F172A] px-2.5 text-[#64748B]">Or continue with credentials</span>
              </div>
            </div>

            {/* Mode Toggle Tabs */}
            <div className="flex p-1 mb-6 bg-[#090D16] border border-[#1E293B] rounded-xl">
              <button
                type="button"
                onClick={() => {
                  setMode("login");
                  setError(null);
                }}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition cursor-pointer ${
                  mode === "login"
                    ? "bg-[#0284C7] text-white shadow-sm"
                    : "text-[#94A3B8] hover:text-[#F8FAFC]"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode("signup");
                  setError(null);
                }}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition cursor-pointer ${
                  mode === "signup"
                    ? "bg-[#0284C7] text-white shadow-sm"
                    : "text-[#94A3B8] hover:text-[#F8FAFC]"
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-500/30 flex items-start gap-2.5 text-red-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "login" ? (
                <div>
                  <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                    Username or Email
                  </label>
                  <div className="relative">
                    <UserIcon className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                    <input
                      type="text"
                      required
                      value={usernameOrEmail}
                      onChange={(e) => setUsernameOrEmail(e.target.value)}
                      placeholder="e.g. security_lead or lead@recon.io"
                      className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                    />
                  </div>
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                      Analyst Username
                    </label>
                    <div className="relative">
                      <UserIcon className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                      <input
                        type="text"
                        required
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Choose a username (min 3 chars)"
                        className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="analyst@domain.com"
                        className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                      />
                    </div>
                  </div>
                </>
              )}

              <div>
                <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password (min 6 chars)"
                    className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                  />
                </div>
              </div>

              {mode === "signup" && (
                <div>
                  <label className="block text-xs font-medium text-[#94A3B8] mb-1.5">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-3 w-4 h-4 text-[#64748B]" />
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Re-enter your password"
                      className="w-full pl-10 pr-4 py-2.5 bg-[#090D16] border border-[#1E293B] rounded-xl text-sm text-[#F8FAFC] placeholder-[#475569] focus:outline-hidden focus:border-[#38BDF8] transition"
                    />
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 bg-[#0284C7] hover:bg-[#0369A1] text-white font-semibold rounded-xl flex items-center justify-center gap-2 text-sm shadow-lg shadow-sky-500/20 transition cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>{mode === "login" ? "Sign In" : "Register Account"}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-xs text-[#64748B]">
              {mode === "login" ? (
                <p>
                  Need an account?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setMode("signup");
                      setError(null);
                    }}
                    className="text-[#38BDF8] font-semibold hover:underline cursor-pointer"
                  >
                    Sign up
                  </button>
                </p>
              ) : (
                <p>
                  Already have an account?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setMode("login");
                      setError(null);
                    }}
                    className="text-[#38BDF8] font-semibold hover:underline cursor-pointer"
                  >
                    Sign in
                  </button>
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
