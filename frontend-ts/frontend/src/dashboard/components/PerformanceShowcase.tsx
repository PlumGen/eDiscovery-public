import React from "react";
import { Card, CardContent, Typography, Box, Grid } from "@mui/material";
import { RadialBarChart, RadialBar, Legend, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { TooltipProps } from "recharts";
import { Paper } from "@mui/material";

const CustomTooltip: React.FC<TooltipProps<number, string>> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    let description = "";

    if (label === "Clear Cases") {
      description = "e.g. general HR topics versus technical details of an engineering project.";
    } else if (label === "Complex Cases") {
      description = "e.g. financial discussions relating to a specific project versus overall company financials.";
    }

return (
  <Box
    sx={{
      backgroundColor: "rgba(255,255,255,0.9)",
      border: "1px solid #ccc",
      borderRadius: 1,
      px: 1,
      py: 0.5,
      fontSize: "0.75rem",
      lineHeight: 1.2,
      maxWidth: 180
    }}
  >
    <Typography variant="caption" fontWeight="bold" display="block" color="text.secondary">
      {label}
    </Typography>
    <Typography variant="caption" display="block" color="text.secondary">
      Accuracy: {payload[0].value}%
    </Typography>
    <Typography variant="caption" color="text.secondary" display="block">
      {description}
    </Typography>
  </Box>
);
  }
  return null;
};


const precisionData = [
  { name: "", value: 92, fill: "#F7F7F7" }, // green
  { name: "", value: 8, fill: "#C59000" },  // yellow
];

const comparisonData = [
  { caseType: "Clear Cases", Accuracy: 98 },
  { caseType: "Complex Cases", Accuracy: 85 },
];

const PerformanceShowcase: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Grid container spacing={4}>
        
        {/* Precision Gauge */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: "16px", boxShadow: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Proven Performance
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <RadialBarChart 
                  cx="50%" cy="50%" innerRadius="10%" outerRadius="100%" 
                  barSize={100} data={precisionData} startAngle={90} endAngle={-270}
                >
                  <RadialBar minAngle={15} background clockWise dataKey="value" />
                  

                </RadialBarChart>
              </ResponsiveContainer>
              <Typography variant="body1" align="center" sx={{ mt: 2 }}>
                Overall Precision: <strong>92%</strong> | False Negatives: <strong>5%</strong>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Comparison Bar Chart */}
<Grid item xs={12} md={6}>
  <Card sx={{ borderRadius: "16px", boxShadow: 3 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Reliable Insights, Even in Complex Cases
      </Typography>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={comparisonData}>
          <XAxis dataKey="caseType" />
          <YAxis domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="Accuracy" fill="#2196f3" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <Typography variant="body1" align="center" sx={{ mt: 2 }}>
        Clear Cases: ~98% | Complex Cases: ~85%
      </Typography>
    </CardContent>
  </Card>
</Grid>

      </Grid>
    </Box>
  );
};

export default PerformanceShowcase;
