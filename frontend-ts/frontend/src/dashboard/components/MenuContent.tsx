import * as React from 'react';
import { Link, useLocation } from "react-router-dom";
import {
  List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Stack, Divider, ListSubheader
} from '@mui/material';

import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import AnalyticsRoundedIcon from '@mui/icons-material/AnalyticsRounded';
import ContentCopy from '@mui/icons-material/ContentCopy';
import SwipeVertical from '@mui/icons-material/SwipeVertical';
import Rule from '@mui/icons-material/Rule';
import EventRepeat from '@mui/icons-material/EventRepeat';
import IosShare from '@mui/icons-material/IosShare';
import CloudUpload from '@mui/icons-material/CloudUpload'; // ✅ Import upload icon

import { Box, Typography } from "@mui/material";

const iconMap: Record<string, React.ReactNode> = {
  Home: <HomeRoundedIcon />,
  "Ingest Data": <CloudUpload />,
  "Duplicates / Near-Duplicates": <ContentCopy />,
  "Label Samples": <SwipeVertical />,
  Validation: <Rule />,
  "Workload Progress": <EventRepeat />,
  Analytics: <AnalyticsRoundedIcon />,
  "Export Results": <IosShare />,
};

const navigation = [
  { name: "Home", href: "/IntroPage" },
  { name: "Ingest Data", href: "/IngestData" },
  { name: "Duplicates / Near-Duplicates", href: "/Duplicates" },
  { name: "Label Samples", href: "/ManualLabel" },
  { name: "Validation", href: "/Validation" },
  { name: "Workload Progress", href: "/WorkLoadProgress" },
  { name: "Analytics", href: "/Analytics" },
  { name: "Export Results", href: "/ExportResults" },
  { name: "Privacy", href: "/Privacy" }, 

];

export default function MenuContent() {
  const location = useLocation();
  const pathname = location.pathname;

  const renderSection = (title: string, filter: (name: string) => boolean) => (
    <>
      <Divider sx={{ mx: -1 }} />
      <ListSubheader>{title}</ListSubheader>
      <List dense>
        {navigation.filter(nav => filter(nav.name)).map((item) => (
          <ListItem key={item.name} disablePadding sx={{ display: 'block' }}>
            <ListItemButton
              component={Link}
              to={item.href}
              selected={pathname === item.href}
            >
              <ListItemIcon>{iconMap[item.name]}</ListItemIcon>
              <ListItemText primary={item.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );

  return (
  <Stack
    sx={{
      p: 1,
      height: "100%",     // parent must provide a real height (e.g., Drawer/Box with 100%, or 100vh)
      minHeight: 0,       // allow flex children to shrink (critical!)
    }}
    direction="column"
    justifyContent="space-between"
  >
    {/* Top content (can scroll internally if needed) */}
    <Box sx={{ flex: 1, minHeight: 0, overflowY: "auto" }}>
      {renderSection('Home', name => name === 'Home')}
      {renderSection('Tasks', name =>
        ['Ingest Data', 'Duplicates / Near-Duplicates', 'Label Samples', 'Validation'].includes(name)
      )}
      {renderSection('Results', name =>
        ['Workload Progress', 'Analytics', 'Export Results'].includes(name)
      )}
     
    </Box>

    {/* Footer (always visible, never pushed off-screen) */}
    <Box sx={{ mt: 2, textAlign: "center", flexShrink: 0 }}>
      <Stack direction="column" justifyContent="center" spacing={0} sx={{ mt: 1 }}>
      <Typography
        variant="body2"
        color="text.secondary"
        component={Link}
        to="/privacy"
        sx={{ textDecoration: "none" }}
      >
        Privacy
      </Typography>

      <Typography variant="body2" color="text.secondary" component="a"
        href="mailto:products_ediscovery@plumgenai.com" sx={{ textDecoration: "none" }}>
        Contact
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
        component="a"
        target="_blank"
        href="https://github.com/PlumGen/eDiscovery-public"
        sx={{ textDecoration: "none" }}
      >
        Transparent Architecture
      </Typography>
      </Stack>

      <Stack direction="row" justifyContent="center" spacing={2} sx={{ mt: 1 }}>
        <Typography
          variant="body2"
          color="text.secondary"
          component="a"
          href="https://portal.azure.us/#create/plumgen.plumgen_ediscoverypreviewplan"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ textDecoration: "none", display: "flex", alignItems: "center" }}
        >
          <img
            src={`${import.meta.env.BASE_URL}/azure-govt-621.svg`}
            alt="GovMicrosoft"
            style={{ width: 100, height: 40, backgroundColor: "white" }}
          />
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          component="a"
          href="https://marketplace.microsoft.com/en-us/product/azure-application/plumgen.plumgen_ediscovery"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ textDecoration: "none", display: "flex", alignItems: "center" }}
        >
          <img
            src={`${import.meta.env.BASE_URL}/ms-marketplace.svg`}
            alt="Microsoft"
            style={{ width: 100, height: 40, backgroundColor: "white" }}
          />
        </Typography>
      </Stack>
 

    </Box>
  </Stack>
  );
}

