"use client";

import { useEffect, useState, ReactNode } from "react";

// 단순 암호 보호 기능을 위한 HOC(Higher-Order Component) 느낌의 래퍼
// SessionStorage를 사용하여 로그인 상태 유지
// 30분 동안 마우스/키보드 움직임이 없으면 자동 잠금

const TIMEOUT_MS = 30 * 60 * 1000; // 30분

export default function PasswordProtection({ children }: { children: ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null); // null = 로딩중 (hydration 문제 방지)
    const [inputPassword, setInputPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    // 컴포넌트 마운트 시 인증 상태 체크
    useEffect(() => {
        const checkAuth = () => {
            const authTime = sessionStorage.getItem("closingShinAuthTime");

            if (authTime) {
                const timePassed = Date.now() - parseInt(authTime, 10);
                if (timePassed < TIMEOUT_MS) {
                    setIsAuthenticated(true);
                    // 갱신 (선택사항 - 페이지 새로고침 시 시간 연장)
                    sessionStorage.setItem("closingShinAuthTime", Date.now().toString());
                } else {
                    // 만료됨
                    sessionStorage.removeItem("closingShinAuthTime");
                    setIsAuthenticated(false);
                }
            } else {
                setIsAuthenticated(false);
            }
        };

        checkAuth();
    }, []);

    // 사용자 활동 감지 타이머
    useEffect(() => {
        if (!isAuthenticated) return;

        let timeoutId: NodeJS.Timeout;

        const resetTimer = () => {
            clearTimeout(timeoutId);
            sessionStorage.setItem("closingShinAuthTime", Date.now().toString());
            timeoutId = setTimeout(() => {
                // 30분 경과 시 자동 로그아웃
                sessionStorage.removeItem("closingShinAuthTime");
                setIsAuthenticated(false);
            }, TIMEOUT_MS);
        };

        // 초기 타이머 설정
        resetTimer();

        // 활동 이벤트 리스너 등록
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

        // 쓰로틀링(Throttling) 적용 - 너무 자주 이벤트가 발생하여 성능이 저하되는 것을 방지
        let isThrottled = false;
        const handleActivity = () => {
            if (!isThrottled) {
                resetTimer();
                isThrottled = true;
                setTimeout(() => { isThrottled = false; }, 10000); // 10초에 한 번만 타이머 갱신
            }
        };

        events.forEach(event => {
            document.addEventListener(event, handleActivity, { passive: true });
        });

        return () => {
            clearTimeout(timeoutId);
            events.forEach(event => {
                document.removeEventListener(event, handleActivity);
            });
        };
    }, [isAuthenticated]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputPassword) return;

        setIsSubmitting(true);
        setError("");

        try {
            const res = await fetch('/api/auth/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: inputPassword })
            });

            if (res.ok) {
                sessionStorage.setItem("closingShinAuthTime", Date.now().toString());
                setIsAuthenticated(true);
            } else {
                setError("비밀번호가 일치하지 않습니다.");
                setInputPassword("");
            }
        } catch (err) {
            setError("인증 서버 오류가 발생했습니다.");
        } finally {
            setIsSubmitting(false);
        }
    };

    // 로딩 중 (Hydration 전)
    if (isAuthenticated === null) {
        return <div className="min-h-screen bg-[#050510] flex items-center justify-center" />;
    }

    // 인증 성공 시 실제 컨텐츠 렌더링
    if (isAuthenticated) {
        return <>{children}</>;
    }

    // 인증 실패 / 미인증 시 잠금 화면 렌더링
    return (
        <div className="min-h-screen bg-[#050510] flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-md bg-[#10101C]/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
                {/* 장식용 글로우 효과 */}
                <div className="absolute -top-20 -right-20 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

                <div className="relative z-10">
                    <div className="text-center mb-10">
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 uppercase tracking-wider mb-2" style={{ fontFamily: 'var(--font-jost)' }}>
                            ClosingSHIN
                        </h1>
                        <p className="text-slate-400 text-sm">시스템 접근을 위해 코드를 입력하세요</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <input
                                type="password"
                                value={inputPassword}
                                onChange={(e) => setInputPassword(e.target.value)}
                                placeholder="Password"
                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-center tracking-widest text-lg"
                                autoFocus
                                autoComplete="off"
                            />
                        </div>

                        {error && (
                            <p className="text-red-400 text-sm text-center animate-pulse">{error}</p>
                        )}

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className={`w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-blue-500/25 active:scale-[0.98] ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
                        >
                            {isSubmitting ? "Verifying..." : "System Login"}
                        </button>
                    </form>

                    <div className="mt-8 text-center text-xs text-slate-600">
                        <p>Session automatically expires after 30 minutes of inactivity.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
