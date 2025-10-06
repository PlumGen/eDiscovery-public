import * as React from 'react';
import { useEffect, useState } from 'react';
import Stack from '@mui/material/Stack';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import CustomDatePicker from './CustomDatePicker';
import NavbarBreadcrumbs from './NavbarBreadcrumbs';
import MenuButton from './MenuButton';
import ColorModeIconDropdown from '../../shared-theme/ColorModeIconDropdown';
import ChevronProgress from './ChevronProgress'
import Typography from '@mui/material/Typography';


import Search from './Search';


export function useSelectedProject() {
  const [primaryText, setPrimaryText] = useState<string | null>(null);

  useEffect(() => {
    const loadSelection = () => {
      const selectedCompany = sessionStorage.getItem("selectedCompany");
      const menucontent = JSON.parse(sessionStorage.getItem("MenuContentsDBList") || "{}");
      if (selectedCompany) {
        const flatItems = Object.values(menucontent).flat();
        const selectedItem = flatItems.find((item: any) => item.menu_value === selectedCompany);
        setPrimaryText(selectedItem?.primaryText || null);
      } else {
        setPrimaryText(null);
      }
    };

    loadSelection();
    window.addEventListener("company-updated", loadSelection);
    return () => window.removeEventListener("company-updated", loadSelection);
  }, []);

  return primaryText;
}


export default function Header() {

  const primaryText = useSelectedProject();

  return (

  <Stack
    direction="column"
    sx={{
      display: { xs: 'none', md: 'flex' },
      maxWidth: '90vw',
      overflowX: 'hidden',
      pt: 1.0,
      px: 0.5,
      boxSizing: 'border-box',
    }}
    spacing={0.5}
  >
    {/* Top row: Selected project */}
  <Typography sx={{ color: primaryText ? 'inherit' : 'red' }}>
    Selected Project: {primaryText || "Please Select a Project"}
  </Typography>

    <Stack
      direction="row"
      sx={{
        display: { xs: 'none', md: 'flex' },

        maxWidth: '90vw',              // ✅ prevent horizontal overflow
        overflowX: 'hidden',            // ✅ hide accidental spillover
        alignItems: { xs: 'flex-start', md: 'left' },
        justifyContent: 'space-between',
        pt: 1.5,
        px: 1,                          // optional padding
        boxSizing: 'border-box',       // ensures padding doesn't overflow
      }}
      spacing={1}
    >

      <ChevronProgress />
      <Stack direction="row" sx={{ gap: 1 }}>
        <ColorModeIconDropdown />
      </Stack>
    </Stack>
    </Stack>    
  );
}

