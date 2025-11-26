
import React, { useEffect, useMemo, useState } from "react";
import { motion, useAnimation, AnimatePresence } from "framer-motion";

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


import Items from "./Items";
const { useCountUp, Sparkline, Lock, FileIcon, Badge  } = Items;

// --- helpers ---


export const HeroDiagram = () => {
  const controls = useAnimation();
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

    const loop = async () => {
      while (!cancelled) {
        if (!paused) {
          await controls.start("flow");
          await sleep(4200);
          controls.set("initial");
        } else {
          await sleep(150);
        }
      }
    };

    loop();
    return () => { cancelled = true; };
  }, [controls, paused]);

  const parent = {
    initial: {},
    flow: {},
  } as const;

  const lanes = [-48, -16, 8, 28, 44];

  const filesV = {
    initial: (i: number) => ({
      opacity: 0,
      x: -80 - i * 10,
      y: lanes[i % lanes.length],
      rotate: 0,
      scale: 0.95,
    }),
    flow: (i: number) => ({
      opacity: [0, 1, 1, 0],
      x: [-80 - i * 10, 60 + i * 6, 60 + i * 6, 60 + i * 6],
      y: [lanes[i % lanes.length], lanes[i % lanes.length], lanes[i % lanes.length], lanes[i % lanes.length]],
      rotate: [0, [-10, 8, -4, 12, -7][i % 5], null, null],
      transition: { duration: 2.0, ease: "easeInOut", delay: 0.05 * i, times: [0, 0.7, 0.9, 1] },
    }),
  } as const;

  const sampleV = {
    initial: { scale: 0.95, opacity: 0 },
    flow: {
      scale: [0.95, 1],
      opacity: [0, 1],
      transition: { delay: 2.2, duration: 0.6, ease: "easeOut" },
    },
  } as const;


  const youV = {
    initial: { scale: 0.95, opacity: 0 },
    flow: {
      scale: [0.95, 1],
      opacity: [0, 1],
      transition: { delay: 2.2*2, duration: 0.6, ease: "easeOut" },
    },
  } as const;

  const orcaV = {
    initial: { scale: 0.95, opacity: 0 },
    flow: {
      scale: [0.95, 1],
      opacity: [0, 1],
      transition: { delay: 2.8+2*2.2, duration: 0.6, ease: "easeOut" },
    },
  } as const;



const returnLanes = [-20, -8, 0, 12, 24, 36];
const returnV = {
  initial: (i: number) => ({
    opacity: 0,
    x: 0, // centered
    y: returnLanes[i % returnLanes.length],
    scale: 0.95,
  }),
  flow: (i: number) => ({
    opacity: [0, 1, 1, 0],
    x: [0, -120 - i * 32, -220 - i * 32, -320 - i * 32], // slide back to the left
    y: [
      returnLanes[i % returnLanes.length],
      returnLanes[i % returnLanes.length],
      returnLanes[i % returnLanes.length],
      returnLanes[i % returnLanes.length],
    ],
    transition: {
      // kick in after the first set finishes; tweak to match your timeline
      delay: 3.2+2*2.2 + i * 0.26,
      duration: 1.1,
      ease: "easeInOut",
      times: [0, 0.25, 0.8, 1],
    },
  }),
} as const;  

const colors = ["#1E88E5", "#43A047", "#F4511E", "#8E24AA", "#FB8C00"];

  return (
    <Paper
      onMouseEnter={() => { setPaused(true); controls.set("initial"); }}
      onMouseLeave={() => { setPaused(false); }}
      variant="outlined"
      sx={{
        width: "100%",
        position: "relative",
        height: 288,
        p: 3,
        borderRadius: 3,
        overflow: "hidden",
        background: (t) =>
          `linear-gradient(135deg, ${t.palette.background.default}, ${t.palette.background.paper})`,
      }}
    >
      <Box sx={{ position: "absolute", inset: 8, border: (t) => `2px solid ${t.palette.primary.light}`, borderRadius: 2 }} />
      <Box sx={{ position: "absolute", right: 16, top: 16, display: "inline-flex", alignItems: "center", gap: 1, bgcolor: 'action.hover', color: "primary.main", px: 1.5, py: 0.5, borderRadius: 999 }}>
        <Lock style={{ width: 16, height: 16 }} />
        <Typography variant="caption" fontWeight={600}>Your Cloud </Typography> 
        <Typography variant="caption" fontWeight={600}>    </Typography> 

      </Box>

      <Box sx={{ position: "absolute", right: 650, top: +100, display: "inline-flex", alignItems: "center", gap: 1, bgcolor: 'action.hover', color: "primary.main", px: 1.5, py: 0.5, borderRadius: 999 }}>
        {/* <Lock style={{ width: 16, height: 16 }} /> */}
        <Typography variant="caption" fontWeight={600}>EDRM</Typography> 
        <Typography variant="caption" fontWeight={600}>    </Typography> 

      </Box>


      <motion.div variants={parent} initial="initial" animate={controls} style={{ position: 'relative', height: "100%" }}>
        {/* Files: each icon is its own motion.div, using custom index for distinct Y lanes */}
        {[0, 1, 2, 3, 4].map((i) => (
          <motion.div
            key={i}
            variants={filesV}
            custom={i}
            style={{
              position: "absolute",
              left: 12,
              top: "50%",
              transform: "translateY(-50%)",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, color: "text.secondary" }}>
              <FileIcon style={{ width: 24, height: 24 }} />
            </Box>
          </motion.div>
        ))}

        {/* Samples */}
        <motion.div variants={sampleV} style={{ position: "absolute", left: "25%", top: "10%", transform: "translate(-50%, -50%)" }}>
          <Paper variant="outlined" sx={{ backdropFilter: "blur(4px)", px: 1.5, py: 1, borderRadius: 2 }}>
            <Typography variant="body2" component="span" fontWeight={700} sx={{ mr: 1 }}>ORCA</Typography>
            <Chip label="selects an intelligent sample" size="small" color="success" variant="outlined" />
          </Paper>
        </motion.div>

        {/* You */}
        <motion.div variants={youV} style={{ position: "absolute", left: "25%", top: "20%", transform: "translate(-50%, -50%)" }}>
          <Paper variant="outlined" sx={{ backdropFilter: "blur(4px)", px: 1.5, py: 1, borderRadius: 2 }}>
            <Typography variant="body2" component="span" fontWeight={700} sx={{ mr: 1 }}>You</Typography>
            <Chip label="label a tiny sample" size="small" color="success" variant="outlined" />
          </Paper>
        </motion.div>

        {/* ORCA */}
        <motion.div variants={orcaV} style={{ position: "absolute", left: "25%", top: "30%", transform: "translate(-50%, -50%)" }}>
          <Paper variant="outlined" sx={{ backdropFilter: "blur(4px)", px: 1.5, py: 1, borderRadius: 2 }}>
            <Typography variant="body2" component="span" fontWeight={700} sx={{ mr: 1 }}>ORCA</Typography>
            <Chip label="labels the rest" size="small" color="success" variant="outlined" />
          </Paper>
        </motion.div>

{/* Centered "return" files: color each icon by index */}
{[0, 1, 2, 3, 4].map((i) => (
  <motion.div
    key={`return-${i}`}
    variants={returnV}
    custom={i}
    style={{
      position: "absolute",
      left: "50%",
      top: "50%",
      transform: "translate(-50%, -50%)",
    }}
  >
    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
      {/* If your icon respects currentColor (e.g., lucide): */}
      {/* <FileIcon style={{ width: 24, height: 24, color: colors[i] }} /> */}
      {/* If it's MUI SvgIcon-based, prefer: */}
      <FileIcon style={{ width: 24, height: 24, color:colors[i] }} />
    </Box>
  </motion.div>
))}


      </motion.div>


      <Typography variant="caption" color="text.secondary" sx={{ position: "absolute", right: 16, bottom: 16 }}>
        No data leaves your environment
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ position: "absolute", right: 16, bottom: 30 }}>
        We do not retain or train on your data
      </Typography>      
    </Paper>
  );
};