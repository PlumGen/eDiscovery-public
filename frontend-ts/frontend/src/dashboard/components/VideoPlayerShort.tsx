// add this import
import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import AutoAwesomeRoundedIcon from '@mui/icons-material/AutoAwesomeRounded';

import VideoPlayer from "./VideoPlayer.tsx";

// (optional) wrap it in your MUI Card so your current imports are used
export default function VideoPlayerShort() {
  return (
    <Card sx={{ maxWidth: 900, mx: "auto" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Intro Video
        </Typography>

        <VideoPlayer
          fallbackMp4="https://storage.googleapis.com/plumgenstaticsite-ebaf8.firebasestorage.app/video/orca_intro_web.mp4"
          poster="/thumb.jpg"
        />


      </CardContent>
    </Card>
  );
}
