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
import pdfFile from '../../assets/ORCA One Pager.pdf?url';
import OutputRoundedIcon from '@mui/icons-material/OutputRounded';
import CloudUploadRoundedIcon from '@mui/icons-material/CloudUploadRounded';
import BiotechRoundedIcon from '@mui/icons-material/BiotechRounded';
import LabelRoundedIcon from '@mui/icons-material/LabelRounded';
import AutoAwesomeMotionRoundedIcon from '@mui/icons-material/AutoAwesomeMotionRounded';
import IosShareIcon from '@mui/icons-material/IosShare';
// --- helpers ---
import {HeroDiagram} from "./IntroPage/HeroDiagram";
import HowItWorks from "./IntroPage/HowItWorks";
import DashboardPreview from "./IntroPage/DashboardPreview";

import Items from "./IntroPage/Items";
const { useCountUp, Sparkline, Lock, FileIcon, Badge  } = Items;

import Others from "./IntroPage/Others";
const { StatCard, Comparison, Accordion  } = Others;



export default function ORCALandingPage() {
  console.log("IntroPage mount");
  const perfData1 = [72, 75, 78, 80, 83, 87, 90, 94, 96, 98];
  const perfData2 = [52, 58, 62, 67, 71, 76, 80, 83, 84, 85];
  const perfData3 = [3, 6, 8, 12, 15, 20, 25, 32, 38, 45];
  const testimonialCount = useCountUp(100, 1200);

  return (
    <Box sx={{ bgcolor: 'background.paper', minHeight: "100vh" }}>
      {/* Nav */}
      <Container maxWidth="lg" sx={{ py: 2, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Typography variant="h6" fontWeight={800}>ORCA for eDiscovery</Typography>
        <Box sx={{ display: { xs: "none", md: "flex" }, gap: 3 }}>
          <Link href="#how" underline="hover" variant="body2">How it works</Link>
          <Link href="#security" underline="hover" variant="body2">Security</Link>
          <Link href="#demo" underline="hover" variant="body2">Demo</Link>
          <Button href="#demo" variant="outlined" size="small">Contact</Button>
        </Box>
      </Container>

      {/* Hero */}
      <Container maxWidth="lg" sx={{ py: 6, width: '100%' }}>
        <Grid container spacing={4} alignItems="stretch">
          <Grid item xs={12} md={6}>
            <Typography variant="h3\" sx={{ typography: { xs: 'h4', md: 'h3' } }} fontWeight={900} lineHeight={1.2}>
              Own your data. High‑accuracy eDiscovery in your cloud.
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mt: 2, maxWidth: 600 }}>
              Deploy on Azure or on‑prem. Audit‑ready results on complex cases.
            </Typography>
            <Box sx={{ mt: 3, display: "flex", gap: 1.5, flexWrap: "wrap" }}>
              <Button href="#demo" variant="contained" size="large">See a quick demo</Button>
              <Button href="#demo" variant="outlined" size="large">Deploy on Azure</Button>
            </Box>

          <Grid item xs={12} md={6}>
            <Box sx={{ alignSelf: 'stretch' }}>
              <HeroDiagram />
            </Box>
          </Grid>

          </Grid>

        </Grid>
      </Container>

      {/* Social proof */}
      <Box sx={{ borderTop: 1, borderBottom: 1, borderColor: "divider", bgcolor: 'background.paper', py: 2 }}>
        <Container maxWidth="lg">
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1.5, justifyContent: { xs: 'center', md: 'flex-start' } }}>
        <Typography
          variant="body2"
          color="text.secondary"
          component="a"
          href="https://cloud.google.com/find-a-partner/partner/plumgen"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ textDecoration: "none", display: "flex", alignItems: "center" }}
        >
          <img
            src={`${import.meta.env.BASE_URL}/Google_Cloud_Partner_no_outline_horizontal.svg`}
            alt="Microsoft"
            style={{ width: 200, height: 80, backgroundColor: "white" }}
          />
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          component="a"
          href="https://appsource.microsoft.com/en-us/marketplace/partner-dir/e48bfc20-c6fb-464f-9747-0035e502dec6/overview"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ textDecoration: "none", display: "flex", alignItems: "center" }}
        >
          <img
            src={`${import.meta.env.BASE_URL}/msCSP.svg`}
            alt="Microsoft"
            style={{ width: 200, height: 80, backgroundColor: "white" }}
          />
        </Typography>

              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, justifyContent: { xs: 'center', md: 'flex-end' }, textAlign: { xs: 'center', md: 'right' } }}>
                <Box component="img" alt="avatar" width={32} height={32} sx={{ borderRadius: 999, border: 1, borderColor: 'divider' }} src={`data:image/svg+xml;utf8,${encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="#e5e7eb"/></svg>')}`} />
                <Typography variant="body2"><b>{testimonialCount}%</b> "No data leaves your environment. Your IAM, your keys."</Typography>
              </Box>
            </Grid>
          </Grid>




        </Container>
      </Box>

      <Box sx={{ borderTop: 1, borderBottom: 1, borderColor: "divider", bgcolor: 'background.paper', py: 2 }}>
        <Container maxWidth="lg">
<Grid container spacing={2} alignItems="stretch" sx={{ mt: 2 }}>
  {[
    { k: 'Traceable', desc: 'Every decision logged and explainable', icon: '🔎' },
    { k: 'Repeatable', desc: 'Deterministic workflows you can rerun', icon: '🔁' },
    { k: 'Defensible', desc: 'Audit‑ready outputs for litigation', icon: '🛡' },
  ].map((r, i) => (
    <Grid item xs={12} sm={4} key={i}>
      <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3, height: '100%', display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
        <Box sx={{ fontSize: 28, lineHeight: 1 }}>{r.icon}</Box>
        <Box>
          <Typography variant="subtitle1" fontWeight={800}>{r.k}</Typography>
          <Typography variant="body2" color="text.secondary">{r.desc}</Typography>
        </Box>
      </Paper>
    </Grid>
  ))}
</Grid>
        </Container>
      </Box>

      {/* Performance */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Grid container spacing={4}  sx={{ flexWrap: { xs: 'wrap', md: 'nowrap' } }}>
          <Grid item xs={12} md={4}><StatCard title="98% accuracy on clear cases " valueTo={98} hint="" spark={perfData1} tooltip="Evaluated on straightforward document classes with deterministic ground truth; micro‑avg F1." /></Grid>
          <Grid item xs={12} md={4}><StatCard title="~85%+ complex matters " valueTo={85} hint="+" spark={perfData2} tooltip="Case‑tuned propagation with limited labels; evaluated against expert annotations on edge classes." /></Grid>
          <Grid item xs={12} md={4}><StatCard title="50–75% review time saved vs baseline " valueTo={75} hint="range" spark={perfData3} tooltip="Baseline = manual first‑pass review; measured across 3 internal studies on heterogeneous datasets." /></Grid>
        </Grid>
        {/* <Link href="#methodology" underline="always" sx={{ mt: 1, display: "inline-block" }} variant="caption"> Methodology and datasets</Link> */}
      </Container>

      {/* How it works */}
      <Container id="how" maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h5" fontWeight={800} sx={{ mb: 2 }}>How it works</Typography>
        <HowItWorks />
      </Container>

      {/* Why teams switch */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h5" fontWeight={800} sx={{ mb: 2 }}>Why Switch</Typography>
        <Comparison />
      </Container>

      {/* Security */}
      <Container id="security" maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h5" fontWeight={800} sx={{ mb: 2 }}>Security & Compliance</Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Paper variant="outlined\" sx={{ p: 2, borderRadius: 3, minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, color: "text.secondary", mb: 1 }}>
                <Lock style={{ width: 20, height: 20 }} />
                <Typography variant="body2">Tenant diagram: IAM, BYOK, logging, SIEM, network boundaries</Typography>
              </Box>
              <Grid container spacing={1}>
                <Grid item xs={6}><Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper' }}>Your IAM</Paper></Grid>
                <Grid item xs={6}><Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper' }}>BYOK</Paper></Grid>
                <Grid item xs={6}><Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper' }}>Logs → your telemetry</Paper></Grid>
                <Grid item xs={6}><Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.paper' }}>Code & infra reviewable on GitHub</Paper></Grid>
              </Grid>
              <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                <Badge>Azure</Badge>
                <Badge>Google Cloud</Badge>
                <Badge>AWS</Badge>                
                <Badge>Private Cloud</Badge>
                <Badge>On/Prem</Badge>                                
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Accordion items={[
              { title: "BYOK", body: (<pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>{`keys:
  provider: azure-kms
  keyVault: your-kv-name
  keyIdentifier: https://your-kv-name.vault.azure.net/keys/edisc-key
`}</pre>) },
              { title: "Tenant isolation", body: (<Typography variant="body2">Dedicated VNet/subnets, private endpoints, no public egress; workloads run under your IAM roles.</Typography>) },
              { title: "Audit logs", body: (<pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>{`logging:
  sink: your-siem
  include:
    - decisions
    - labeling
    - access
`}</pre>) },
            ]} />
          </Grid>
        </Grid>
      </Container>

      {/* Dashboard */}
      <Container id="demo" maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h5" fontWeight={800} sx={{ mb: 2 }}>Live dashboard preview</Typography>
        <DashboardPreview />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Always know where you stand, what’s labeled, what’s pending, and what needs review.
        </Typography>
      </Container>

      {/* CTA */}
      <Box sx={{ bgcolor: "primary.main", py: 6, color: "primary.contrastText" }}>
        <Container maxWidth="lg" sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2, flexDirection: { xs: "column", md: "row" } }}>
          <Typography variant="h6" fontWeight={700}>Ready to try ORCA on your data?</Typography>
          <Box sx={{ display: "flex", gap: 1.5 }}>

              <Button
                component="a"
                href="https://storage.googleapis.com/plumgenstaticsite-ebaf8.firebasestorage.app/video/orca_intro_web.mp4"
                target="_blank"
                rel="noopener noreferrer"
                variant="contained"
              >
                Quick Demo Video
              </Button>

              <Button
                component="a"
                href="https://marketplace.microsoft.com/en-us/product/azure-application/plumgen.plumgen_ediscovery"
                target="_blank"
                rel="noopener noreferrer"
                variant="contained"
              >
                Run a pilot on your data
              </Button>

              <Button
                component="a"
                href="https://storage.googleapis.com/plumgenstaticsite-ebaf8.firebasestorage.app/video/ORCA%20for%20eDiscovery%20-%20Brochure.pdf"
                download
                variant="outlined"
                color="inherit"
              >
                Product Brochure
              </Button>

          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Container id="contact" maxWidth="lg" sx={{ py: 3 }}>
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
          <Box sx={{ display: "flex", gap: 2 }}>
            {/* <Link href="#security-brief" underline="hover" variant="body2">Security brief</Link>
            <Link href="#github" underline="hover" variant="body2">GitHub</Link>
            <Link href="#terms" underline="hover" variant="body2">Terms</Link>
            <Link href="#privacy" underline="hover" variant="body2">Privacy</Link> */}
          </Box>
          <Typography variant="body2"> <Link href="mailto:products_ediscovery@plumgenai.com" underline="hover">Contact</Link></Typography>
        </Box>
      </Container>
    </Box>
  );
}
