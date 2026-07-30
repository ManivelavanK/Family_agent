import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import clsx from 'clsx';

export default function Layout() {
  const location = useLocation();
  const isFather = location.pathname === '/father';
  const isChildren = location.pathname === '/children';
  const isBaby = location.pathname === '/baby';
  const isDarkLayout = isFather || isChildren;
  const isZeroPadding = isDarkLayout || isBaby;

  return (
    <div className={clsx(
      "flex h-screen overflow-hidden relative transition-colors duration-300",
      isDarkLayout ? "bg-[#070E16]" : "bg-slate-50"
    )}>
      {/* Background blurs wrapper */}
      {!isDarkLayout && (
        <div className="absolute inset-0 pointer-events-none z-0">
          <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-amber-400/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-emerald-400/10 rounded-full blur-[120px]" />
        </div>
      )}

      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header />
        <main className={clsx("flex-1 overflow-x-hidden overflow-y-auto", isZeroPadding ? "p-0" : "p-8")}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}