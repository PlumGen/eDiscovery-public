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
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const loadSelection = () => {
      setLoading(true);
      setTimeout(() => {
        const selectedCompany = sessionStorage.getItem("selectedCompany");
        const menucontent = JSON.parse(sessionStorage.getItem("MenuContentsDBList") || "{}");
        if (selectedCompany) {
          const flatItems = Object.values(menucontent).flat();
          const selectedItem = flatItems.find((item: any) => item.db_name === selectedCompany);
          setPrimaryText(selectedItem?.primaryText || null);
        } else {
          setPrimaryText(null);
        }
        setLoading(false);
      }, 300); // small delay to show loading effect
    };

    loadSelection();
    window.addEventListener("company-updated", loadSelection);
    return () => window.removeEventListener("company-updated", loadSelection);
  }, []);

  return { primaryText, loading };
}


export default function Header() {
  const { primaryText, loading } = useSelectedProject();

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
      <Typography sx={{ color: loading ? 'gray' : primaryText ? 'inherit' : 'red' }}>
        {loading
          ? "Loading selected project..."
          : `Selected Project: ${primaryText || "Please Select a Project"}`}
      </Typography>

      <Stack
        direction="row"
        sx={{
          display: { xs: 'none', md: 'flex' },
          maxWidth: '90vw',
          overflowX: 'hidden',
          alignItems: { xs: 'flex-start', md: 'left' },
          justifyContent: 'space-between',
          pt: 1.5,
          px: 1,
          boxSizing: 'border-box',
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
