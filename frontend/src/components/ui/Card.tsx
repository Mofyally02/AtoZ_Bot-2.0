import { motion } from 'framer-motion';
import React from 'react';
import { CardProps } from '../../types';
import { cn } from '../../utils/cn';

const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  ...props
}) => {
  const baseClasses = 'rounded-2xl transition-all duration-200';
  
  const variants = {
    default: 'bg-white dark:bg-secondary-800 shadow-lg border border-secondary-200 dark:border-secondary-700',
    glass: 'bg-white/10 dark:bg-secondary-800/10 backdrop-blur-md border border-white/20 dark:border-secondary-700/20 shadow-glass',
    outline: 'bg-transparent border-2 border-secondary-200 dark:border-secondary-700 hover:border-primary-300 dark:hover:border-primary-600',
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        baseClasses,
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default Card;
