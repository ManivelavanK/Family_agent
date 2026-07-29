import React, { useEffect, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';

export const AnimatedNumber = ({ value = 0, formatAsCurrency = true, duration = 1.2 }) => {
  const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
  const spring = useSpring(0, { duration: duration * 1000, bounce: 0 });
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    spring.set(numericValue);
  }, [numericValue, spring]);

  useEffect(() => {
    return spring.on('change', (latest) => {
      setDisplayValue(latest);
    });
  }, [spring]);

  const formatNumber = (val) => {
    const rounded = Math.round(val);
    if (!formatAsCurrency) return rounded.toLocaleString('en-IN');
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(rounded);
  };

  return (
    <motion.span className="inline-block tracking-tight font-semibold">
      {formatNumber(displayValue)}
    </motion.span>
  );
};

export default AnimatedNumber;
