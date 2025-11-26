import * as React from 'react';
import { useEffect, useState } from 'react';
import { PieChart } from '@mui/x-charts/PieChart';
import { useDrawingArea } from '@mui/x-charts/hooks';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import LinearProgress, { linearProgressClasses } from '@mui/material/LinearProgress';
import LoadingBar from './/LoadingBar'

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

import {
  IndiaFlag, 
  UsaFlag,
  BrazilFlag,
  GlobeFlag,
} from '../internals/components/CustomIcons';

const data = [
  { label: 'India', value: 1000 },
  { label: 'USA', value: 10000 },
  { label: 'Brazil', value: 10000 },
  { label: 'Other', value: 5000 },
];

const countries = [
  {
    name: 'India',
    value: 50,
    flag: <IndiaFlag />,
    color: 'hsl(220, 25%, 65%)',
  },
  {
    name: 'USA',
    value: 50,
    flag: <UsaFlag />,
    color: 'hsl(220, 25%, 45%)',
  },
  {
    name: 'Brazil',
    value: 10,
    flag: <BrazilFlag />,
    color: 'hsl(220, 25%, 30%)',
  },
  {
    name: 'Other',
    value: 5,
    flag: <GlobeFlag />,
    color: 'hsl(220, 25%, 20%)',
  },
];

interface StyledTextProps {
  variant: 'primary' | 'secondary';
}

const StyledText = styled('text', {
  shouldForwardProp: (prop) => prop !== 'variant',
})<StyledTextProps>(({ theme }) => ({
  textAnchor: 'middle',
  dominantBaseline: 'central',
  fill: (theme.vars || theme).palette.text.secondary,
  variants: [
    {
      props: {
        variant: 'primary',
      },
      style: {
        fontSize: theme.typography.h5.fontSize,
      },
    },
    {
      props: ({ variant }) => variant !== 'primary',
      style: {
        fontSize: theme.typography.body2.fontSize,
      },
    },
    {
      props: {
        variant: 'primary',
      },
      style: {
        fontWeight: theme.typography.h5.fontWeight,
      },
    },
    {
      props: ({ variant }) => variant !== 'primary',
      style: {
        fontWeight: theme.typography.body2.fontWeight,
      },
    },
  ],
}));

interface PieCenterLabelProps {
  primaryText: string;
  secondaryText: string;
}

function PieCenterLabel({ primaryText, secondaryText }: PieCenterLabelProps) {
  const { width, height, left, top } = useDrawingArea();
  const primaryY = top + height / 2 - 10;
  const secondaryY = primaryY + 24;

  return (
    <React.Fragment>
      <StyledText variant="primary" x={left + width / 2} y={primaryY}>
        {primaryText}
      </StyledText>
      <StyledText variant="secondary" x={left + width / 2} y={secondaryY}>
        {secondaryText}
      </StyledText>
    </React.Fragment> 
  );
}

const colors = [
  'hsl(220, 20%, 65%)',
  'hsl(220, 20%, 42%)',
  'hsl(220, 20%, 35%)',
  'hsl(220, 20%, 25%)',
];

export default function ChartValidationByIssue() {
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [PieData, setPieData] = useState([]);
  const [totalReviewed, settotalReviewed] = useState(0);
  const [chartPercent, setchartPercent] = useState([]);


  const [dataloading, setdataloading] = useState(true);


  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };
  
    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);
  

    useEffect(() => {
      if (!selectedCompany) return;
      setdataloading(true)

      const fetchProgress = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/getcurrentprogress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company: selectedCompany, progresstype:'reviewedstats' }),
          });
          
          const data = await response.json();

          const raw = data?.data;
        
          if (!raw || typeof raw !== 'object' || Object.keys(raw).length < 1) {
            console.warn('Unexpected or empty tabledata:', raw);
            setPieData([]);
            setchartPercent([]);
            return;
          }


          const pieDataArray = Object.values(raw).map(item => ({
            label: item.displayname,
            value: item.totalreviewed
          }));

          setPieData(pieDataArray);
          const totalReviewed = pieDataArray.reduce((sum, item) => sum + item.value, 0);
          settotalReviewed(totalReviewed)

          const chartPercent = Object.values(raw).map(item => ({
            name: item.displayname,
            value: item.acceptedRatio,
            color: 'hsl(220, 25%, 65%)',

          }));
          setchartPercent(chartPercent);
          setdataloading(false);

        } catch (error) {
          console.error('Failed to fetch progress:', error);
          setchartPercent([]);
          setPieData([]);

        }
      };
  
      fetchProgress();
    }, [selectedCompany]);


  return (
    <Card
      variant="outlined"
      sx={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1 }}
    >
      <CardContent>
        <Typography component="h2" variant="subtitle2">
          Validation Statistics
        </Typography>

      {dataloading ? (
        <LoadingBar/>
      ) : (
        <>
     
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <PieChart
            colors={colors}
            margin={{
              left: 80,
              right: 80,
              top: 80,
              bottom: 80,
            }}
            series={[
              {
                data: PieData,
                innerRadius: 75,
                outerRadius: 100,
                paddingAngle: 0,
                highlightScope: { fade: 'global', highlight: 'item' },
              },
            ]}
            height={260}
            width={260}
            hideLegend
          >
              <PieCenterLabel
                primaryText={`${(totalReviewed / 1000).toFixed(1)}K`}
                secondaryText="Total Reviewed"
              />

          </PieChart>
        </Box>
        {chartPercent.map((country, index) => (
          <Stack
            key={index}
            direction="row"
            sx={{ alignItems: 'center', gap: 2, pb: 2 }}
          >
            {country.flag}
            <Stack sx={{ gap: 1, flexGrow: 1 }}>
              <Stack
                direction="row"
                sx={{
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: '500' }}>
                  {country.name}
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {country.value}%
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                aria-label="Number of users by country"
                value={country.value}
                sx={{
                  [`& .${linearProgressClasses.bar}`]: {
                    backgroundColor: country.color,
                  },
                }}
              />
            </Stack>
          </Stack>
                   

        ))}

                  </>
      )}

      </CardContent>
    </Card>
  );
}
