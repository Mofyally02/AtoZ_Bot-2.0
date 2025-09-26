import { motion } from 'framer-motion';
import {
    Activity,
    BarChart3,
    Bot,
    Briefcase,
    Home,
    Settings
} from 'lucide-react';
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useBotStore } from '../../stores/botStore';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const { botStatus, theme, toggleTheme } = useBotStore();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (href: string) => {
    return location.pathname === href;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Menu Button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => {/* Add mobile menu toggle logic */}}
          className="p-2 rounded-lg bg-card border border-border shadow-lg"
        >
          <Activity className="w-6 h-6 text-foreground" />
        </button>
      </div>

      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border shadow-soft-lg transform -translate-x-full lg:translate-x-0 transition-transform duration-300 ease-in-out">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 border-b border-border">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg">
                <Bot className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <span className="text-xl font-bold text-card-foreground">
                  AtoZ Bot
                </span>
                <p className="text-xs text-muted-foreground">Translation Assistant</p>
              </div>
            </div>
          </div>

          {/* Bot Status */}
          <div className="p-4 border-b border-border">
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/50">
              <div className={`w-3 h-3 rounded-full ${
                botStatus?.is_running ? 'bg-success-500 animate-pulse' : 'bg-muted-foreground'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-card-foreground truncate">
                  {botStatus?.is_running ? 'Bot Running' : 'Bot Stopped'}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {botStatus?.session_name || 'No active session'}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive(item.href)
                      ? 'bg-primary text-primary-foreground shadow-md'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  <Icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${
                    isActive(item.href) ? 'text-primary-foreground' : 'text-muted-foreground group-hover:text-accent-foreground'
                  }`} />
                  <span className="truncate">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Theme Toggle */}
          <div className="p-4 border-t border-border">
            <button
              onClick={toggleTheme}
              className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all duration-200"
            >
              <Activity className="w-5 h-5" />
              <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        <main className="min-h-screen">
          <div className="p-4 lg:p-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
