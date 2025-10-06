import * as React from 'react';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import ChartUserByCountry from './ChartUserByCountry';
import CustomizedTreeView from './CustomizedTreeView';

import HighlightedCard from './HighlightedCard';
import PageViewsBarChart from './PageViewsBarChart';
import SessionsChart from './SessionsChart';
import StatCard, { StatCardProps } from './StatCard';

import DocumentLevelProgress from './DocumentLevelProgress';
import ChartValidationByIssue from './ChartValidationByIssue';
import ListOfDocumentsLabeled from './ListOfDocumentsLabeled';
import PropogationBreakdown from './PropogationBreakdown';


export default function MainGrid() {
  return (
  <Container 
      maxWidth="lg"   // scales with viewport, up to theme.breakpoints.lg (~1200px)
      sx={{ py: 4 }}  // vertical padding
    >
      {/* cards */}
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>
      <Grid
        container
        spacing={2}
        columns={1}
        rows={1}        
        sx={{ mb: (theme) => theme.spacing(2) }}
      >
          {/* {data.map((card, index) => (
            <Grid key={index} size={{ xs: 12, sm: 6, lg: 3 }}>
              <StatCard {...card} />
            </Grid>
          ))} */}
        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <DocumentLevelProgress />
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 3  }}>
          <ChartValidationByIssue /> 
        </Grid>
        <Grid size={{ xs: 12, md: 6, lg: 3  }}>
          <PropogationBreakdown />
        </Grid>        
        {/* <Grid size={{ xs: 12, md: 6 }}>
          <PageViewsBarChart />
        </Grid> */}
      </Grid>

      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Details
      </Typography>
      <Grid container spacing={2} columns={1}>
        <Grid size={{ xs: 12, lg: 9 }}>
          <ListOfDocumentsLabeled />
        </Grid>

      </Grid>
      
      {/* <Copyright sx={{ my: 4 }} /> */}
    </Container>
  );
}
