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
        'p-6 bg-card text-card-foreground rounded-2xl shadow-soft border border-border',
        'hover:shadow-soft-lg transition-all duration-200 group',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">
          {title}
        </h3>
        {icon && (
          <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors duration-200">
            {icon}
          </div>
        )}
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold text-card-foreground">
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
