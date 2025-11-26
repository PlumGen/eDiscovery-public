import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Dashbord from "./dashboard/Dashboard";

// VideoIntro
const VideoIntro = ({ onEnd, size }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    video.addEventListener("ended", onEnd);
    const playPromise = video.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {});
    }

    return () => video.removeEventListener("ended", onEnd);
  }, [onEnd]);

  const style =
    size.width && size.height
      ? {
          maxWidth: size.width,
          maxHeight: size.height,
        }
      : {};

  return (
    <div className="flex items-center justify-center w-full h-full overflow-hidden">
    Introduction Video
    <motion.video
      ref={videoRef}
      id="intro-video"
      autoPlay
      playsInline
      controls
      style={style}
      className="object-contain bg-black rounded-lg"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.1 } }}
    >
        <source
          src="https://storage.googleapis.com/plumgenstaticsite-ebaf8.firebasestorage.app/video/orca_intro_web.mp4"
          type="video/mp4"
        />
      </motion.video>
    </div>
  );
};

// IntroAnimation
const IntroAnimation = () => {
  const [showVideo, setShowVideo] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.has("shortvideo");
  });

  const containerRef = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const ro = new ResizeObserver((entries) => {
      const rect = entries[0].contentRect;
      setSize({ width: rect.width, height: rect.height });
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full h-full flex items-center justify-center bg-black overflow-hidden"
    >
      <AnimatePresence>
        {showVideo ? (
          <VideoIntro key="video" onEnd={() => setShowVideo(false)} size={size} />
        ) : (
          <motion.div
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, transition: { duration: 0 } }}
            className="w-full h-full flex items-center justify-center"
          >
            <Dashbord />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default IntroAnimation;
