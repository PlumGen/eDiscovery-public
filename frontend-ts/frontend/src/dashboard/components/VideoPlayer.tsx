// VideoPlayer.tsx
import { useEffect, useRef } from "react";
import Hls from "hls.js";

type Props = {
  src?: string;            // optional HLS .m3u8
  fallbackMp4: string;     // your MP4 URL
  poster?: string;
  autoplay?: boolean;
  muted?: boolean;
};

export default function VideoPlayer({
  src,
  fallbackMp4,
  poster,
  autoplay = false,
  muted = false,
}: Props) {
  const ref = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const video = ref.current!;
    let hls: Hls | null = null;

    if (src) {
      if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = src;
      } else if (Hls.isSupported()) {
        hls = new Hls({ enableWorker: true, lowLatencyMode: true });
        hls.loadSource(src);
        hls.attachMedia(video);
      }
    } else {
      video.src = fallbackMp4;
    }

    return () => hls?.destroy();
  }, [src, fallbackMp4]);

  return (
    <video
      ref={ref}
      className="w-full"
      controls
      playsInline
      poster={poster}
      autoPlay={autoplay}
      muted={muted}
      preload="metadata"
    >
      {!src && (
        <source
          src={fallbackMp4}
          type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'
        />
      )}
    </video>
  );
}
