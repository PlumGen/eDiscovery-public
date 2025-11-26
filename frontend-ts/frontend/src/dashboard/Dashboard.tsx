import * as React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import type {} from '@mui/x-date-pickers/themeAugmentation';
import type {} from '@mui/x-charts/themeAugmentation';
import type {} from '@mui/x-data-grid-pro/themeAugmentation';
import type {} from '@mui/x-tree-view/themeAugmentation';
import { alpha } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import AppNavbar from './components/AppNavbar';
import Header from './components/Header';

// import for main area
import Progress from './components/Progress';

import IntroPage from './components/IntroPage';
import Duplicates from './components/Duplicates';
import FilesinBuckets from './components/FilesinBuckets';
import ManualLabel from './components/ManualLabel';
import Validation from './components/Validation';
import ExportResults from './components/ExportResults';
import Privacy from './components/Privacy';
import Layout from './components/Layout';

import Analytics from './components/Analytics';

import SideMenu from './components/SideMenu';
import VideoPlayerShort from './components/VideoPlayerShort';



import AppTheme from '../shared-theme/AppTheme';
import {
  chartsCustomizations,
  dataGridCustomizations,
  datePickersCustomizations,
  treeViewCustomizations,
} from './theme/customizations';

const xThemeComponents = {
  ...chartsCustomizations,
  ...dataGridCustomizations,
  ...datePickersCustomizations,
  ...treeViewCustomizations,
};

export default function Dashboard(props: { disableCustomTheme?: boolean }) {
  return (
    <AppTheme {...props} themeComponents={xThemeComponents}>
      <CssBaseline enableColorScheme />
      <Box sx={{ display: 'flex' }}>
        <Layout />
        {/* Main content */}
        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            backgroundColor: theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
            overflow: 'auto',
          })}
        >
          <Stack
            spacing={2}
            sx={{
              alignItems: 'stretch',
              mx: 1,
              pb: 1,
              mt: { xs: 8, md: 0 },
            }}
          >
            <Header />

              <Routes>
                <Route path="/" element={<IntroPage />} />

                <Route path="/IntroPage" element={<IntroPage />} />
                <Route path="/IngestData" element={<FilesinBuckets />} />
                <Route path="/Duplicates" element={<Duplicates />} />
                <Route path="/ManualLabel" element={<ManualLabel />} />
                <Route path="/Validation" element={<Validation />} />
                <Route path="/WorkLoadProgress" element={<Progress />} />
                <Route path="/Analytics" element={<Analytics />} />
                <Route path="/ExportResults" element={<ExportResults />} />
                <Route path="/Privacy" element={<Privacy />} />
                <Route path="/ORCAINTROSHORT" element={<VideoPlayerShort />} />


              </Routes>



          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
}
