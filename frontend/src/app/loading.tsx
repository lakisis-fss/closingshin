export default function Loading() {
  return (
    <div className="min-h-screen bg-canvas flex flex-col items-center justify-center p-8 transition-opacity duration-500">
      <div className="relative">
        {/* Animated Background Block */}
        <div className="absolute inset-0 bg-bauhaus-yellow transform -skew-x-6 translate-x-2 translate-y-2 animate-pulse opacity-50 shadow-hard" />
        
        {/* Logo Text */}
        <div className="relative bg-ink text-white px-8 py-4 transform -skew-x-6 border-4 border-ink shadow-hard">
          <h2 className="text-4xl font-black uppercase tracking-tighter flex items-center gap-2">
            Closing<span className="text-bauhaus-yellow">SHIN</span>
            <span className="inline-block w-3 h-3 bg-bauhaus-red rounded-full animate-bounce ml-2" />
          </h2>
        </div>
      </div>
      
      {/* Loading Message */}
      <div className="mt-12 text-center">
        <div className="inline-block border-b-4 border-bauhaus-red pb-1 mb-2">
          <p className="font-black text-xl uppercase tracking-widest text-ink">
            Synchronizing Market Data
          </p>
        </div>
        <p className="text-sm font-bold text-gray-500 font-sans">
          최적화된 병렬 데이터 수집이 진행 중입니다...
        </p>
      </div>

      {/* Decorative Bauhaus Elements */}
      <div className="mt-16 flex gap-4 opacity-30">
        <div className="w-8 h-8 bg-bauhaus-red rounded-full" />
        <div className="w-8 h-8 bg-bauhaus-blue transform rotate-45" />
        <div className="w-8 h-8 bg-bauhaus-yellow" />
      </div>
    </div>
  );
}
