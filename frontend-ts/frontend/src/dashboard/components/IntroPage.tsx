import React, { useRef, useEffect, useState} from "react";
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';

import Typography from '@mui/material/Typography';
import Copyright from '../internals/components/Copyright';
import ProcessGraph from './ProcessGraph';
import MarketTools from "./MarketTools";

import PerformanceShowcase from "./PerformanceShowcase";

 

import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

import { Document, Page} from 'react-pdf';
import { Paper} from '@mui/material';

import { pdfjs } from 'react-pdf';
// @ts-ignore
import pdfWorker from 'pdfjs-dist/build/pdf.worker.mjs?url';
// @ts-ignore
import pdfFile from '../../assets/PlumGen_eDiscovery.pdf?url';

pdfjs.GlobalWorkerOptions.workerSrc = pdfWorker;

export default function IntroPage() {

const containerRef = useRef(null);
const [containerWidth, setContainerWidth] = useState(800);

useEffect(() => {
  const resizeObserver = new ResizeObserver((entries) => {
    for (let entry of entries) {
      setContainerWidth(entry.contentRect.width);
    }
  });
  if (containerRef.current) {
    resizeObserver.observe(containerRef.current);
  }
  return () => resizeObserver.disconnect();
}, []);

console.log("pdfFile URL:", pdfFile);

  return (
    <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>

      {/* cards */}
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
      PlumGen Delivers Enterprise-grade Accuracy and Reliability in Document Review. 
      

      </Typography>
      <Grid
        container
        spacing={2}
        columns={1}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <Paper elevation={3} sx={{ p: 2, bgcolor: "white", borderRadius: 2 }}>
          <PerformanceShowcase />
          </Paper>
        </Grid>


        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <Paper elevation={3} sx={{ p: 2, bgcolor: "white", borderRadius: 2 }}>
          <ProcessGraph />
          </Paper>
        </Grid>

      </Grid>

      {/* cards */}
      <Typography component="h2" variant="h6" sx={{ mb: 2 }}>
        Current Market Tools
      </Typography>
      <Grid
        container
        spacing={2}
        columns={1}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>
          <Paper elevation={3} sx={{ p: 2, bgcolor: "white", borderRadius: 2 }}>
          <MarketTools />
          </Paper>
        </Grid>

      </Grid>



      <Grid
        container
        spacing={2}
        columns={1}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >

        <Grid size={{ xs: 12, sm: 6, lg: 3 }}>

            <Paper elevation={3} sx={{ p: 2, bgcolor: "white", borderRadius: 2 }}> 
              <Document file={pdfFile}>
                
                {[1, 2, 3].map((pageNumber) => (
                  <Page
                    key={pageNumber}
                    pageNumber={pageNumber}

                    className="pdf-page"
                  />
                ))}
              </Document>
          
            </Paper>
        </Grid>

      </Grid>



   

    
      {/* <Copyright sx={{ my: 4 }} /> */}
    </Box>
  );
}
