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
    default: 'bg-card text-card-foreground shadow-soft border border-border',
    glass: 'bg-card/10 backdrop-blur-md border border-border/20 shadow-glass',
    outline: 'bg-transparent border-2 border-border hover:border-primary/50',
    elevated: 'bg-card text-card-foreground shadow-soft-lg border border-border hover:shadow-xl transition-shadow duration-200',
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
