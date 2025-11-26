import React, { useEffect, useMemo, useState } from "react";
import { useTheme } from "@mui/material/styles";
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

const useCountUp = (to: number, ms = 1200) => {
  const [val, setVal] = useState(0);
  useEffect(() => {
    const start = performance.now();
    let raf = 0 as number | any;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / ms);
      console.debug("useCountUp tick", { to, ms, p });
      setVal(Math.round(p * to));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to, ms]);
  return val;
};

const Sparkline = ({ data }: { data: number[] }) => {
  const theme = useTheme();
  console.log("Sparkline render", { points: data.length, first: data[0], last: data[data.length-1] });
  const points = useMemo(() => data.map((y, i) => ({ x: i, y })), [data]);
  const chartData = points.map((p) => ({ name: p.x, value: p.y }));
  return (
    <Box sx={{ height: 40, width: "100%" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 6, right: 6, bottom: 0, left: 6 }}>
          <ReTooltip formatter={(v: any) => [v, ""] as any} contentStyle={{ fontSize: 12, background: theme.palette.background.paper, color: theme.palette.text.primary, border: `1px solid ${theme.palette.divider}` }} />
          <Line type="monotone" dataKey="value" dot={false} strokeWidth={2} stroke={theme.palette.primary.main} isAnimationActive />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

const Lock = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...props}>
    <rect x="3.5" y="10" width="17" height="10" rx="2" />
    <path d="M7.5 10V7a4.5 4.5 0 0 1 9 0v3" />
  </svg>
);

const FileIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...props}>
    <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9z" />
    <path d="M14 2v7h7" />
  </svg>
);

const Badge = ({ children }: { children: React.ReactNode }) => (
  <Chip variant="outlined" label={children} sx={{ fontSize: 12, borderRadius: 2 }} />
);

export default { useCountUp, Sparkline, Lock, FileIcon, Badge };


