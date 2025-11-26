import React, { useEffect, useMemo, useState } from "react";
import { motion, useAnimation, AnimatePresence } from "framer-motion";
import {
  Box,
  Paper,
  Typography,
  Divider,
} from "@mui/material";
import Grid from "@mui/material/Grid";


import Items from "./Items";
const { useCountUp, Sparkline} = Items;


const StatCard = ({ title, valueTo, hint, spark, tooltip }: { title: string; valueTo: number; hint?: string; spark: number[]; tooltip: string }) => {
  const v = useCountUp(valueTo, 1200);
  return (
    <Paper variant="outlined\" sx={{ p: 2, borderRadius: 3, minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Typography variant="body2" color="text.secondary">{title}</Typography>
        {/* <Typography variant="caption" color="primary.main" sx={{ textDecoration: "underline" }} title={tooltip}>Methodology</Typography> */}
      </Box>
      <Box mt={0.5}>
        <Typography variant="h4" component="div" fontWeight={700}>
          {v}{title.includes("accuracy") && "%"}
          {hint && (
            <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>{hint}</Typography>
          )}
        </Typography>
      </Box>
      <Box mt={1.5}>
        <Sparkline data={spark} />
      </Box>
    </Paper>
  );
};

const Comparison = () => {
  const rows = [
    { k: "Data Control", other: "Vendor cloud", ORCA: "Your VPC/on‑prem", note: "Data remains within your network boundaries and keys." },
    { k: "Complex‑case Accuracy", other: "Generic", ORCA: "Case‑tuned propagation", note: "Small labeled set + threshold calibration → better F1 on edge cases." },
    { k: "Deployment", other: "Fixed SaaS", ORCA: "Azure/Azure Gov/on‑prem", note: "Fit to your compliance regime (FedRAMP‑aligned paths on Azure Gov)." },
  ];
  return (
    <Grid container spacing={4}>
      {rows.map((r, i) => (
        <Grid item xs={12} md={4} key={i}>
          <Paper variant="outlined\" sx={{ p: 2, borderRadius: 3, minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>{r.k}</Typography>
            <Grid container spacing={1}>
              <Grid item xs={6}><Typography variant="body2" color="text.secondary">❌ {r.other}</Typography></Grid>
              <Grid item xs={6}><Typography variant="body2" fontWeight={600}>✅ {r.ORCA}</Typography></Grid>
            </Grid>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>{r.note}</Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};



// Lightweight Accordion using MUI primitives + framer-motion
function Accordion({ items }: { items: { title: string; body: React.ReactNode }[] }) {
  console.log("Accordion render", { count: items.length });
  const [open, setOpen] = useState<number | null>(0);
  return (
    <Paper variant="outlined" sx={{ borderRadius: 3 }}>
      {items.map((it, i) => (
        <Box key={i}>
          <Box onClick={() => { console.log("Accordion toggle", { index: i, next: open === i ? null : i }); setOpen(open === i ? null : i); }} sx={{ p: 2, display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}>
            <Typography variant="body2" fontWeight={600}>{it.title}</Typography>
            <Typography variant="h6" component="span">{open === i ? "–" : "+"}</Typography>
          </Box>
          <AnimatePresence initial={false}>
            {open === i && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
                <Divider />
                <Box sx={{ p: 2 }}>{it.body}</Box>
              </motion.div>
            )}
          </AnimatePresence>
          {i < items.length - 1 && <Divider />}
        </Box>
      ))}
    </Paper>
  );
}

export default { StatCard, Comparison, Accordion };