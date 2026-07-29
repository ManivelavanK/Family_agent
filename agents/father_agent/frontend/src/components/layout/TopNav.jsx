import React, { useState, useEffect } from 'react';
import { useFamily } from '../../context/FamilyContext';
import { notificationApi } from '../../services/notificationApi';
import { Menu, Wifi, WifiOff, Bell, User, RefreshCw } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const TopNav = ({ isCollapsed, setIsMobileOpen }) => {
  const { isBackendConnected, isCheckingBackend, checkConnection, familyId, setFamilyId } = useFamily();
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await notificationApi.getNotifications(familyId);
        if (res && res.notifications) {
          setUnreadNotifications(res.notifications.length);
        }
      } catch (err) {
        console.warn('Failed to load notification badge count:', err);
      }
    };
    if (isBackendConnected) {
      fetchNotifications();
    }
  }, [familyId, isBackendConnected]);

  return (
    <header
      className={`sticky top-0 z-40 h-16 bg-[#FFFFFF]/90 backdrop-blur-md border-b border-[#D9E2EC] px-4 lg:px-8 flex items-center justify-between transition-all duration-300 ${
        isCollapsed ? 'lg:ml-20' : 'lg:ml-64'
      }`}
    >
      {/* Left section: Hamburger & Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="lg:hidden p-2 rounded-lg text-[#627D98] hover:text-[#102A43] hover:bg-[#F7F9FC] transition-colors"
        >
          <Menu className="w-6 h-6" />
        </button>

        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-bold text-[#102A43] tracking-wide">KinNest</h1>
            <span className="text-[#D9E2EC]">/</span>
            <span className="text-xs font-semibold text-[#0F766E]">Father AI Online</span>
          </div>
          <p className="text-[11px] text-[#627D98] hidden sm:block">
            Your family's money, intelligently managed.
          </p>
        </div>
      </div>

      {/* Right section: Connection Status, Family Switcher, Notifications */}
      <div className="flex items-center gap-3 sm:gap-5">
        {/* Real Backend Connection Indicator */}
        <div
          onClick={checkConnection}
          title="Click to check connection status"
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border cursor-pointer transition-all duration-200 ${
            isCheckingBackend
              ? 'bg-[#F7F9FC] border-[#D9E2EC] text-[#627D98]'
              : isBackendConnected
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-700 shadow-sm'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-700 shadow-sm'
          }`}
        >
          {isCheckingBackend ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#627D98]" />
              <span>Checking...</span>
            </>
          ) : isBackendConnected ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <Wifi className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5" />
              <span>Offline</span>
            </>
          )}
        </div>

        {/* Family Selector */}
        <div className="flex items-center gap-1.5 bg-[#F7F9FC] border border-[#D9E2EC] rounded-xl px-2.5 py-1 text-xs text-[#172B4D]">
          <User className="w-3.5 h-3.5 text-[#0F766E]" />
          <span className="text-[#627D98] hidden sm:inline">Family:</span>
          <select
            value={familyId}
            onChange={(e) => setFamilyId(Number(e.target.value))}
            className="bg-transparent text-[#172B4D] font-bold focus:outline-none cursor-pointer"
          >
            <option value={1} className="bg-white text-[#172B4D]">ID 1 (Primary)</option>
            <option value={2} className="bg-white text-[#172B4D]">ID 2 (Secondary)</option>
          </select>
        </div>

        {/* Notifications Icon */}
        <NavLink
          to="/notifications"
          className="relative p-2 rounded-xl text-[#627D98] hover:text-[#102A43] hover:bg-[#F7F9FC] transition-colors"
        >
          <Bell className="w-5 h-5" />
          {unreadNotifications > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-[#0F766E] text-[10px] font-bold text-white flex items-center justify-center border border-white">
              {unreadNotifications}
            </span>
          )}
        </NavLink>
      </div>
    </header>
  );
};

export default TopNav;
