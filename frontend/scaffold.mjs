import fs from 'fs';
import path from 'path';

const dirs = [
  'src/components/layout',
  'src/components/ui',
  'src/pages',
  'src/services',
  'src/store',
  'src/utils',
];

const files = {
  'src/components/layout/Layout.tsx': 
"import { Outlet } from 'react-router-dom';\n" +
"import Sidebar from './Sidebar';\n" +
"import Header from './Header';\n\n" +
"export default function Layout() {\n" +
"  return (\n" +
"    <div className=\"flex h-screen bg-slate-50\">\n" +
"      <Sidebar />\n" +
"      <div className=\"flex-1 flex flex-col overflow-hidden\">\n" +
"        <Header />\n" +
"        <main className=\"flex-1 overflow-x-hidden overflow-y-auto bg-slate-100 p-6\">\n" +
"          <Outlet />\n" +
"        </main>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}",
  'src/components/layout/Sidebar.tsx': 
"import { Link, useLocation } from 'react-router-dom';\n" +
"import { Home, Users, UserCircle, Baby, Calendar, Network, Settings, Bell } from 'lucide-react';\n" +
"import clsx from 'clsx';\n\n" +
"const navItems = [\n" +
"  { name: 'Dashboard', path: '/dashboard', icon: Home, color: 'text-slate-500' },\n" +
"  { name: 'Father Agent', path: '/father', icon: UserCircle, color: 'text-blue-500' },\n" +
"  { name: 'Mother Agent', path: '/mother', icon: UserCircle, color: 'text-pink-500' },\n" +
"  { name: 'Children Agent', path: '/children', icon: Users, color: 'text-amber-500' },\n" +
"  { name: 'Grandparent Agent', path: '/grandparent', icon: UserCircle, color: 'text-emerald-500' },\n" +
"  { name: 'Baby Care', path: '/baby', icon: Baby, color: 'text-violet-500' },\n" +
"  { name: 'Life Planner', path: '/planner', icon: Calendar, color: 'text-indigo-500' },\n" +
"  { name: 'Orchestrator', path: '/orchestrator', icon: Network, color: 'text-slate-500' },\n" +
"];\n\n" +
"export default function Sidebar() {\n" +
"  const location = useLocation();\n" +
"  return (\n" +
"    <div className=\"w-64 bg-white border-r border-slate-200 flex flex-col\">\n" +
"      <div className=\"h-16 flex items-center px-6 border-b border-slate-200\">\n" +
"        <span className=\"text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600\">KinNest OS</span>\n" +
"      </div>\n" +
"      <nav className=\"flex-1 overflow-y-auto py-4\">\n" +
"        {navItems.map((item) => {\n" +
"          const Icon = item.icon;\n" +
"          const isActive = location.pathname === item.path;\n" +
"          return (\n" +
"            <Link key={item.path} to={item.path} className={clsx(\n" +
"              'flex items-center px-6 py-3 text-sm font-medium transition-colors',\n" +
"              isActive ? 'bg-slate-50 text-blue-600 border-r-2 border-blue-600' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'\n" +
"            )}>\n" +
"              <Icon className={clsx(\"w-5 h-5 mr-3\", item.color)} />\n" +
"              {item.name}\n" +
"            </Link>\n" +
"          );\n" +
"        })}\n" +
"      </nav>\n" +
"      <div className=\"p-4 border-t border-slate-200\">\n" +
"        <div className=\"flex items-center space-x-3 mb-2\">\n" +
"          <div className=\"w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold\">U</div>\n" +
"          <div className=\"flex-1 min-w-0\">\n" +
"            <p className=\"text-sm font-medium text-slate-900 truncate\">Current User</p>\n" +
"          </div>\n" +
"        </div>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}",
  'src/components/layout/Header.tsx': 
"import { Bell, Search } from 'lucide-react';\n" +
"import { Link } from 'react-router-dom';\n\n" +
"export default function Header() {\n" +
"  return (\n" +
"    <header className=\"h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6\">\n" +
"      <div className=\"flex-1 max-w-lg\">\n" +
"        <div className=\"relative\">\n" +
"          <Search className=\"absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5\" />\n" +
"          <input type=\"text\" placeholder=\"Global Search...\" className=\"w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow\" />\n" +
"        </div>\n" +
"      </div>\n" +
"      <div className=\"flex items-center space-x-4\">\n" +
"        <Link to=\"/notifications\" className=\"relative p-2 text-slate-400 hover:text-slate-500 transition-colors\">\n" +
"          <Bell className=\"w-6 h-6\" />\n" +
"          <span className=\"absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full\"></span>\n" +
"        </Link>\n" +
"      </div>\n" +
"    </header>\n" +
"  );\n" +
"}",
  'src/store/useAuthStore.ts': 
"import { create } from 'zustand';\n\n" +
"interface AuthState {\n" +
"  isAuthenticated: boolean;\n" +
"  user: any | null;\n" +
"  familyId: string | null;\n" +
"  login: (userData: any, familyId: string) => void;\n" +
"  logout: () => void;\n" +
"}\n\n" +
"export const useAuthStore = create<AuthState>((set) => ({\n" +
"  isAuthenticated: false,\n" +
"  user: null,\n" +
"  familyId: null,\n" +
"  login: (user, familyId) => set({ isAuthenticated: true, user, familyId }),\n" +
"  logout: () => set({ isAuthenticated: false, user: null, familyId: null }),\n" +
"}));"
};

const pages = [
  'Landing', 'Dashboard', 'FatherAgent', 'MotherAgent', 'ChildrenAgent', 
  'GrandparentAgent', 'BabyAgent', 'PlannerAgent', 'Orchestrator', 
  'Notifications', 'Settings', 'WorkspaceFlow'
];

pages.forEach(page => {
  files['src/pages/' + page + '.tsx'] = 
"export default function " + page + "() {\n" +
"  return (\n" +
"    <div className=\"p-6\">\n" +
"      <h1 className=\"text-2xl font-bold mb-4\">" + page + "</h1>\n" +
"      <div className=\"bg-white rounded-xl shadow-sm border border-slate-200 p-6\">\n" +
"        <p className=\"text-slate-600\">Content for " + page + " goes here.</p>\n" +
"      </div>\n" +
"    </div>\n" +
"  );\n" +
"}";
});

// Create directories
dirs.forEach(dir => {
  const fullPath = path.join(process.cwd(), dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
  }
});

// Write files
Object.entries(files).forEach(([filepath, content]) => {
  fs.writeFileSync(path.join(process.cwd(), filepath), content.trim());
});

console.log('Scaffolding complete.');
