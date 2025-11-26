import * as React from 'react';
import { useEffect, useState } from 'react';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import {Box, 
        CircularProgress
} from '@mui/material';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import ChartUserByCountry from './ChartUserByCountry';
import CustomizedTreeView from './CustomizedTreeView';

import HighlightedCard from './HighlightedCard';
import PageViewsBarChart from './PageViewsBarChart';
import SessionsChart from './SessionsChart';
import StatCard, { StatCardProps } from './StatCard';
import {
  Button,
} from '@mui/material';

import DocumentLevelProgress from './DocumentLevelProgress';
import ChartValidationByIssue from './ChartValidationByIssue';
import ListOfDocumentsLabeled from './ListOfDocumentsLabeled';
import PropogationBreakdown from './PropogationBreakdown';
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

export default function MainGrid() {
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [loading, setLoading] = useState(false);
  
  const runUpdates = async (type?: string) => {
      if (!selectedCompany) return;
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/updateanalyticstables`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            company: selectedCompany,
            userinjesttype: type
          }),
        });

        const result = await response.json();
        const formattedRows = (result.data || false);
        if (formattedRows) {
          setLoading(false);
          alert("Analytics Updated");
        } else {
          setLoading(true);
          alert("Backend Error - Analytics Not Updated");          
        }


      } catch (error) {
        console.error('Failed to Run Updates:', error);
        setLoading(true);
      } finally {
        setLoading(false);
      }
    };
    
  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };

    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);



  return (
  <Container 
      maxWidth="lg"   // scales with viewport, up to theme.breakpoints.lg (~1200px)
      sx={{ py: 4 }}  // vertical padding
    >
      {/* cards */}

      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Overview
      </Typography>

        {loading ? (
          <CircularProgress />
          ) : ( 
      <>
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
      </>
          )}

        <Box mt={15} display="flex" justifyContent="center" gap={2}>
          <Button variant="contained" onClick={() => runUpdates('document')}>
            Update Analytics 
          </Button>
        </Box>
        
      {/* <Copyright sx={{ my: 4 }} /> */}
    </Container>
  );
}
