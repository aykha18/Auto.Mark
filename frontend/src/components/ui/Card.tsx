import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
  id?: string;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  shadow = 'md',
  hover = false,
  onClick,
  id,
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  };

  const hoverClasses = hover ? 'hover:shadow-lg transition-shadow duration-200' : '';
  const clickableClasses = onClick ? 'cursor-pointer' : '';

  const classes = `
    bg-white rounded-lg border border-gray-200
    ${paddingClasses[padding]}
    ${shadowClasses[shadow]}
    ${hoverClasses}
    ${clickableClasses}
    ${className}
  `.trim();

  return (
    <div className={classes} onClick={onClick} id={id}>
      {children}
    </div>
  );
};

export default Card;