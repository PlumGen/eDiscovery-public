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
import { useTheme } from "@mui/material/styles";
import Grid from "@mui/material/Grid";

import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import AnalyticsRoundedIcon from '@mui/icons-material/AnalyticsRounded';
import ContentCopy from '@mui/icons-material/ContentCopy';
import SwipeVertical from '@mui/icons-material/SwipeVertical';
import Rule from '@mui/icons-material/Rule';
import EventRepeat from '@mui/icons-material/EventRepeat';
import IosShare from '@mui/icons-material/IosShare';
import CloudUpload from '@mui/icons-material/CloudUpload'; // ✅ Import upload icon

import { cloneElement } from "react";


const HowItWorks = () => {
  console.log("HowItWorks render");
  const steps = [ 
    { title: "Ingest", desc: "Securely load docs via VPN/gateway; unify pages.", icon: <CloudUpload /> },
    { title: "Define near‑duplicates", desc: "Review 10–12 pairs to set similarity threshold.", icon: <ContentCopy /> },
    { title: "Label sample", desc: "Tag a small representative set.", icon: <SwipeVertical /> },
    { title: "Propagate & validate", desc: "ORCA auto‑labels; you spot‑check random and low‑confidence.", icon: <Rule /> },
    { title: "Export to Workflow", desc: "Export structured data into your workflow ", icon: <IosShare /> },

  ];
  
const explanations = [
  "Ingest documents securely through your VPN or gateway. From any source, including Relativity, DISCO, ORCA normalizes formats (PDF, Word, email) and segments them into structured pages so later steps can compare and label consistently.",
  "We quickly calibrate what counts as 'near-duplicate.' Reviewing ~10–12 representative pairs lets you set a similarity threshold that prevents both over-merging and missed merges.",
  "Label a small, representative sample once. These gold labels ground the system so propagation can scale without sacrificing precision.",
  "ORCA propagates labels across the corpus. You then spot-check a random slice and low-confidence edges to keep quality high and measurable.",
  "Push clean, structured outputs to your workflow (review platform, DB, or queue) with provenance so everything remains auditable."
];
  
  const [idx, setIdx] = useState(0);
// 50/50 columns, no overflow
return (
  <Grid container spacing={3} alignItems="flex-start">
    <Stack direction="row" spacing={3}>
    <Grid item xs={12} md={6}>
      <Stack spacing={2}>
        {steps.map((s, i) => (
          <Paper
            key={i}
            onClick={() => setIdx(i)}
            variant="outlined"
            sx={{
              p: 2,
              borderRadius: 3,
              cursor: "pointer",
              borderColor: idx === i ? "primary.main" : "divider",
            }}
          >
            <Typography variant="subtitle2" fontWeight={700}>
              {i + 1}. {s.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {s.desc}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </Grid>

    <Grid item xs={12} md={6}>
      <Paper
        variant="outlined"
        sx={{
          width: "100%",
          borderRadius: 3,
          p: 3,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          alignItems: "center",
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={`icon-${idx}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.25 }}
            style={{ fontSize: 56, lineHeight: 1 }}
          >
            {cloneElement(steps[idx].icon, { sx: { fontSize: 96 } })}

          </motion.div>
        </AnimatePresence>

        <AnimatePresence mode="wait">
          <motion.div
            key={`text-${idx}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
            style={{ width: "100%" }}
          >
            <Typography variant="h6" fontWeight={800} gutterBottom>
              {steps[idx].title}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ wordBreak: "break-word" }}
            >
              {explanations[idx]}
            </Typography>
          </motion.div>
        </AnimatePresence>
      </Paper>
    </Grid>
    </Stack>
  </Grid>

);

};

export default HowItWorks;