import * as React from 'react';
import { useEffect, useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Chip from '@mui/material/Chip';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import { BarChart } from '@mui/x-charts/BarChart';
import { useTheme } from '@mui/material/styles';
import LoadingBar from './/LoadingBar'

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

export default function DocumentLevelProgress() { 
  const theme = useTheme(); 
const colorPalette = [
  (theme.vars || theme).palette.primary.dark,
  (theme.vars || theme).palette.primary.main,
  (theme.vars || theme).palette.primary.light,
  (theme.vars || theme).palette.secondary.dark,
  (theme.vars || theme).palette.secondary.main,
  (theme.vars || theme).palette.secondary.light,
];


  const [treeItems, setTreeItems] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [categories, setCategories] = useState([]);
  const [OverAllPercent, setOverAllPercent] = useState(0);
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
            body: JSON.stringify({ company: selectedCompany, progresstype:'overall' }),
          });
          
          const data = await response.json();

          const raw = data?.data.tabledata;
          
          if (!Array.isArray(raw) || raw.length < 2) {
            console.warn('Unexpected or empty tabledata:', raw);
            setTreeItems([]);
            setOverAllPercent(0);
            return;
          }

          const headers = ['Ingested', 'Accepted', 'Rejected']
          const rows = [ [100, 0, 0], [0, 100, 0], [0, 0, 100]]
          const axisNames = ['Ingested', 'Processed', 'Labeled']; // adjust as needed


          // Build stacked bar series
          const series = headers.map((label, i) => ({
            id: label.toLowerCase(),
            label,
            data: rows[i],
            stack: 'A',
          }));

          const percentcomplete = data.data.percents.anylabeled/data.data.percents.totalprepared*100;
          setOverAllPercent(percentcomplete)
          setTreeItems(series);
          setCategories(axisNames);
          setdataloading(false)


        } catch (error) {
          console.error('Failed to fetch progress:', error);
         
          setTreeItems([]);
          setOverAllPercent(0);
        }
      };
  
      fetchProgress();
    }, [selectedCompany]);
  

  return (
    <Card variant="outlined" sx={{ width: '100%' }}>
      <CardContent>
        <Typography component="h2" variant="subtitle2" gutterBottom>
          Document Level Labeling Progress
        </Typography>

      {dataloading ? (
        <LoadingBar/>
      ) : (
        <>

        <Stack sx={{ justifyContent: 'space-between' }}>
          <Stack
            direction="row"
            sx={{
              alignContent: { xs: 'center', sm: 'flex-start' },
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Typography variant="h4" component="p">
              Overall
            </Typography>
            <Chip size="small" color="error" label={`${Math.round(OverAllPercent)}%`} />

          </Stack>

        </Stack>
        
<BarChart
  borderRadius={8}
  colors={colorPalette}
  xAxis={[
    {
      scaleType: 'band',
      categoryGapRatio: 0.5,
      data: categories, // now has 3 labels
      height: 24,
    },
  ]}
  yAxis={[{ width: 50 }]}
  series={treeItems} // now 6 series, each with 3 values
  height={250}
  margin={{ left: 0, right: 0, top: 20, bottom: 0 }}
  grid={{ horizontal: true }}
  hideLegend
/>
        </>
      )}

      </CardContent>
    </Card>
  );
}
