import React, { useState, useEffect } from 'react';
import LinearProgress from '@mui/material/LinearProgress';

const LoadingBar = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((oldProgress) => {
        const newProgress = oldProgress + 3.33 * 4 * 1.25;
        if (newProgress >= 100) {
          clearInterval(timer);
        }
        return newProgress;
      });
    }, 1000);

    return () => {
      clearInterval(timer);
    };
  }, []);

  // Custom style to make the progress bar thicker
  const progressBarStyle = {
    height: '10px', // Adjust the height as needed to make the bar thicker
    borderRadius: '5px', // Optional: Adds rounded corners to the progress bar
  };

  return <LinearProgress variant="determinate" value={progress} style={progressBarStyle} />;
};

export default LoadingBar;
