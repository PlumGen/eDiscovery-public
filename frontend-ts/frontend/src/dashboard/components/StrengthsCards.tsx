import React from "react";
import { Card, CardContent, Typography, Box, Grid } from "@mui/material";
import { RadialBarChart, RadialBar, Legend, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { TooltipProps } from "recharts";
import { Paper } from "@mui/material";

import HighlightedCardAccurate from "./HighlightedCardAccurate";
import HighlightedCardControl from "./HighlightedCardControl";
import HighlightedCardDefensible from "./HighlightedCardDefensible";





const StrengthsCards: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 0 }}>
      <Grid
        container
        spacing={0}
        sx={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          flexWrap: "nowrap", 
        }}
      >
        {[<HighlightedCardControl />, <HighlightedCardAccurate />, <HighlightedCardDefensible />].map(
          (Component, i) => (
            <Box
              key={i}
              sx={{
                flex: 1,                    // equal width
                mx: 1,                      // even horizontal spacing
                minWidth: 0,                // prevent overflow
              }}
            >
              <Card sx={{ borderRadius: "16px", boxShadow: 3, height: "100%" }}>
                <CardContent>
                  <Box
                    sx={{
                      height: 200,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {Component}
                  </Box>
                </CardContent>
              </Card>
            </Box>
          )
        )}
      </Grid>
    </Box>
  );
};


export default StrengthsCards;


