import { motion } from 'framer-motion';
import {
    Activity,
    CheckCircle,
    Clock,
    Globe,
    TrendingUp,
    XCircle,
    Zap
} from 'lucide-react';
import React from 'react';
import BotControlPanel from '../components/dashboard/BotControlPanel';
import Card from '../components/ui/Card';
import MetricCard from '../components/ui/MetricCard';
import { useAnalyticsStore } from '../stores/analyticsStore';
import { useBotStore } from '../stores/botStore';

const Dashboard: React.FC = () => {
  const { botStatus, theme } = useBotStore();
  const { dashboardMetrics } = useAnalyticsStore();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
            AtoZ Bot Dashboard
          </h1>
          <p className="text-secondary-600 dark:text-secondary-400 mt-1">
            Monitor and control your translation bot in real-time
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            botStatus?.is_running 
              ? 'bg-success-100 text-success-800 dark:bg-success-900/30 dark:text-success-300'
              : 'bg-secondary-100 text-secondary-800 dark:bg-secondary-800 dark:text-secondary-300'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 inline-block ${
              botStatus?.is_running ? 'bg-success-500 animate-pulse' : 'bg-secondary-400'
            }`} />
            {botStatus?.is_running ? 'Running' : 'Stopped'}
          </div>
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <motion.div 
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <MetricCard
          title="Total Jobs Today"
          value={dashboardMetrics?.total_jobs_today || 0}
          icon={<Activity className="w-6 h-6 text-primary-600" />}
          change={12}
          changeType="positive"
        />
        <MetricCard
          title="Acceptance Rate"
          value={`${dashboardMetrics?.acceptance_rate_today || 0}%`}
          icon={<TrendingUp className="w-6 h-6 text-success-600" />}
          change={5.2}
          changeType="positive"
        />
        <MetricCard
          title="Active Sessions"
          value={dashboardMetrics?.active_sessions || 0}
          icon={<Zap className="w-6 h-6 text-warning-600" />}
        />
        <MetricCard
          title="Bot Uptime"
          value={`${dashboardMetrics?.bot_uptime_hours || 0}h`}
          icon={<Clock className="w-6 h-6 text-secondary-600" />}
        />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Control Panel */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <BotControlPanel />
        </motion.div>

        {/* Recent Activity */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-xl font-bold text-secondary-900 dark:text-white mb-4">
              Recent Activity
            </h2>
            
            {botStatus?.is_running ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-success-600" />
                    <div>
                      <p className="font-medium text-success-900 dark:text-success-100">
                        Bot is running successfully
                      </p>
                      <p className="text-sm text-success-700 dark:text-success-300">
                        Session: {botStatus.session_name || 'Unnamed'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-success-900 dark:text-success-100">
                      {botStatus.total_accepted} accepted
                    </p>
                    <p className="text-xs text-success-700 dark:text-success-300">
                      {botStatus.total_checks} checks
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="w-4 h-4 text-primary-600" />
                      <span className="text-sm font-medium text-primary-900 dark:text-primary-100">
                        Jobs Accepted
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-primary-900 dark:text-primary-100">
                      {botStatus.total_accepted}
                    </p>
                  </div>

                  <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-800">
                    <div className="flex items-center space-x-2 mb-2">
                      <XCircle className="w-4 h-4 text-error-600" />
                      <span className="text-sm font-medium text-error-900 dark:text-error-100">
                        Jobs Rejected
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-error-900 dark:text-error-100">
                      {botStatus.total_rejected}
                    </p>
                  </div>
                </div>

                <div className="p-4 bg-secondary-50 dark:bg-secondary-800 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Globe className="w-4 h-4 text-secondary-600" />
                    <span className="text-sm font-medium text-secondary-700 dark:text-secondary-300">
                      Most Active Language
                    </span>
                  </div>
                  <p className="text-lg font-semibold text-secondary-900 dark:text-white">
                    {dashboardMetrics?.most_active_language || 'N/A'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Activity className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-secondary-900 dark:text-white mb-2">
                  Bot is not running
                </h3>
                <p className="text-secondary-600 dark:text-secondary-400">
                  Start the bot to see real-time activity and metrics
                </p>
              </div>
            )}
          </Card>
        </motion.div>
      </div>

      {/* Quick Stats */}
      <motion.div variants={itemVariants}>
        <Card className="p-6">
          <h2 className="text-xl font-bold text-secondary-900 dark:text-white mb-4">
            Quick Stats
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {botStatus?.total_checks || 0}
              </div>
              <div className="text-sm text-secondary-600 dark:text-secondary-400">
                Total Checks
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-success-600 mb-2">
                {botStatus?.total_accepted || 0}
              </div>
              <div className="text-sm text-secondary-600 dark:text-secondary-400">
                Jobs Accepted
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-error-600 mb-2">
                {botStatus?.total_rejected || 0}
              </div>
              <div className="text-sm text-secondary-600 dark:text-secondary-400">
                Jobs Rejected
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
