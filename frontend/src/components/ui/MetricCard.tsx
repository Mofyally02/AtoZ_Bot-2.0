import { motion } from 'framer-motion';
import { Minus, TrendingDown, TrendingUp } from 'lucide-react';
import React from 'react';
import { MetricCardProps } from '../../types';
import { cn } from '../../utils/cn';

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  className,
}) => {
  const getChangeIcon = () => {
    if (change === undefined) return null;
    
    switch (changeType) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-success-600" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-error-600" />;
      default:
        return <Minus className="w-4 h-4 text-secondary-500" />;
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-success-600';
      case 'negative':
        return 'text-error-600';
      default:
        return 'text-secondary-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'p-6 bg-white dark:bg-secondary-800 rounded-2xl shadow-lg border border-secondary-200 dark:border-secondary-700',
        'hover:shadow-xl transition-all duration-200',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-secondary-600 dark:text-secondary-400">
          {title}
        </h3>
        {icon && (
          <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
            {icon}
          </div>
        )}
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold text-secondary-900 dark:text-white">
            {value}
          </p>
          {change !== undefined && (
            <div className={cn('flex items-center mt-2 text-sm font-medium', getChangeColor())}>
              {getChangeIcon()}
              <span className="ml-1">
                {change > 0 ? '+' : ''}{change}%
              </span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MetricCard;
