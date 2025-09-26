import { motion } from 'framer-motion';
import React, { useEffect } from 'react';
import Card from '../components/ui/Card';
import { useAnalyticsStore } from '../stores/analyticsStore';

const Analytics: React.FC = () => {
  const { analytics, fetchAnalytics } = useAnalyticsStore();

  useEffect(() => {
    fetchAnalytics(24); // Fetch last 24 hours
  }, [fetchAnalytics]);

  if (!analytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600 dark:text-secondary-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
          Analytics
        </h1>
        <p className="text-secondary-600 dark:text-secondary-400 mt-1">
          Detailed insights and performance metrics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">
              {analytics.total_jobs_processed}
            </div>
            <div className="text-sm text-secondary-600 dark:text-secondary-400">
              Total Jobs Processed
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-success-600 mb-2">
              {analytics.acceptance_rate}%
            </div>
            <div className="text-sm text-secondary-600 dark:text-secondary-400">
              Acceptance Rate
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-warning-600 mb-2">
              {analytics.most_common_language || 'N/A'}
            </div>
            <div className="text-sm text-secondary-600 dark:text-secondary-400">
              Most Common Language
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-error-600 mb-2">
              {analytics.peak_hour || 'N/A'}
            </div>
            <div className="text-sm text-secondary-600 dark:text-secondary-400">
              Peak Hour
            </div>
          </div>
        </Card>
      </div>

      {/* Placeholder for Charts */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-secondary-900 dark:text-white mb-4">
          Analytics Charts
        </h3>
        <div className="h-64 flex items-center justify-center bg-secondary-50 dark:bg-secondary-800 rounded-lg">
          <p className="text-secondary-500 dark:text-secondary-400">
            Charts will be implemented here
          </p>
        </div>
      </Card>
    </motion.div>
  );
};

export default Analytics;
