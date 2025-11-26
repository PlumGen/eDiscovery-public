import React, { useEffect, useMemo, useState } from "react";
import { motion, useAnimation, AnimatePresence } from "framer-motion";
import { LineChart, Line, ResponsiveContainer, Tooltip as ReTooltip } from "recharts";
import {
  Box,
  Button,
  Container,
  Link,
  Paper,
  Typography,
  Divider,
  Chip,
  Stack,
} from "@mui/material";
import Grid from "@mui/material/Grid";




const DashboardPreview = () => {
  console.log("DashboardPreview render");
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      console.debug("DashboardPreview tick");
      setTick((t) => (t + 1) % 1000);
    }, 3000);
    return () => clearInterval(id);
  }, []);
  const totalPages = 120_000 + (tick % 7) * 11;
  const processed = 87_320 + (tick % 5) * 13;
  const confidence = 92 + (tick % 3);
  return (
    <Paper variant="outlined\" sx={{ p: 2, borderRadius: 3, minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Progress (mock data)</Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary">Total pages</Typography>
            <Typography variant="h5" fontWeight={700}>{totalPages.toLocaleString()}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary">Processed docs</Typography>
            <Typography variant="h5" fontWeight={700}>{processed.toLocaleString()}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary">Confidence band</Typography>
            <Typography variant="h5" fontWeight={700}>{confidence}%</Typography>
          </Paper>
        </Grid>
      </Grid>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
        Hover for details: Confidence is computed on held‑out spot‑checks; low‑band items are queued for review.
      </Typography>
    </Paper>
  );
};

export default DashboardPreview;