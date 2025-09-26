import { motion } from 'framer-motion';
import { CheckCircle, Clock, Search, XCircle } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { useAnalyticsStore } from '../stores/analyticsStore';

const Jobs: React.FC = () => {
  const { jobRecords, fetchJobRecords } = useAnalyticsStore();
  const [filter, setFilter] = useState<'all' | 'accepted' | 'rejected'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchJobRecords();
  }, [fetchJobRecords]);

  const filteredJobs = jobRecords.filter(job => {
    const matchesFilter = filter === 'all' || job.status === filter;
    const matchesSearch = job.job_ref.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.language.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'accepted':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-error-600" />;
      default:
        return <Clock className="w-5 h-5 text-warning-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'bg-success-100 text-success-800 dark:bg-success-900/30 dark:text-success-300';
      case 'rejected':
        return 'bg-error-100 text-error-800 dark:bg-error-900/30 dark:text-error-300';
      default:
        return 'bg-warning-100 text-warning-800 dark:bg-warning-900/30 dark:text-warning-300';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900 dark:text-white">
          Job Records
        </h1>
        <p className="text-secondary-600 dark:text-secondary-400 mt-1">
          View and manage all job records
        </p>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
              <input
                type="text"
                placeholder="Search jobs by reference or language..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-secondary-300 dark:border-secondary-600 rounded-lg bg-white dark:bg-secondary-800 text-secondary-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="flex space-x-2">
            <Button
              variant={filter === 'all' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All ({jobRecords.length})
            </Button>
            <Button
              variant={filter === 'accepted' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setFilter('accepted')}
            >
              Accepted ({jobRecords.filter(j => j.status === 'accepted').length})
            </Button>
            <Button
              variant={filter === 'rejected' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setFilter('rejected')}
            >
              Rejected ({jobRecords.filter(j => j.status === 'rejected').length})
            </Button>
          </div>
        </div>
      </Card>

      {/* Job List */}
      <Card className="p-6">
        <div className="space-y-4">
          {filteredJobs.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 dark:text-white mb-2">
                No jobs found
              </h3>
              <p className="text-secondary-600 dark:text-secondary-400">
                {searchTerm ? 'Try adjusting your search terms' : 'No jobs have been processed yet'}
              </p>
            </div>
          ) : (
            filteredJobs.map((job, index) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-4 bg-secondary-50 dark:bg-secondary-800 rounded-lg border border-secondary-200 dark:border-secondary-700 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(job.status)}
                    <div>
                      <h3 className="font-semibold text-secondary-900 dark:text-white">
                        {job.job_ref}
                      </h3>
                      <p className="text-sm text-secondary-600 dark:text-secondary-400">
                        {job.language} • {job.duration}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </div>
                    
                    <div className="text-right">
                      <p className="text-sm font-medium text-secondary-900 dark:text-white">
                        {new Date(job.appointment_date).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-secondary-600 dark:text-secondary-400">
                        {new Date(job.appointment_time).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
                
                {job.rejection_reason && (
                  <div className="mt-3 p-3 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-800">
                    <p className="text-sm text-error-800 dark:text-error-200">
                      <strong>Reason:</strong> {job.rejection_reason}
                    </p>
                  </div>
                )}
                
                <div className="mt-3 flex items-center justify-between text-xs text-secondary-500 dark:text-secondary-400">
                  <span>Job Type: {job.job_type || 'N/A'}</span>
                  <span>Scraped: {new Date(job.scraped_at).toLocaleString()}</span>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </Card>
    </motion.div>
  );
};

export default Jobs;
