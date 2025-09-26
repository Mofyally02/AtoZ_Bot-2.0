import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import React from 'react';
import { ButtonProps } from '../../types';
import { cn } from '../../utils/cn';

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className,
  ...props
}) => {
  const baseClasses = 'relative inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 focus:ring-ring shadow-soft hover:shadow-soft-lg',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 focus:ring-ring',
    success: 'bg-success-600 hover:bg-success-700 text-white focus:ring-success-500 shadow-soft hover:shadow-soft-lg',
    warning: 'bg-warning-600 hover:bg-warning-700 text-white focus:ring-warning-500 shadow-soft hover:shadow-soft-lg',
    error: 'bg-error-600 hover:bg-error-700 text-white focus:ring-error-500 shadow-soft hover:shadow-soft-lg',
    ghost: 'bg-transparent hover:bg-accent hover:text-accent-foreground focus:ring-ring',
    outline: 'border border-input bg-transparent hover:bg-accent hover:text-accent-foreground focus:ring-ring',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        className
      )}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      )}
      {children}
    </motion.button>
  );
};

export default Button;
