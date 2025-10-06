import * as React from 'react';
import { useEffect } from 'react';
import MuiAvatar from '@mui/material/Avatar';
import MuiListItemAvatar from '@mui/material/ListItemAvatar';
import MenuItem from '@mui/material/MenuItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListSubheader from '@mui/material/ListSubheader';
import Select, { SelectChangeEvent, selectClasses } from '@mui/material/Select';
import Divider from '@mui/material/Divider';
import { styled } from '@mui/material/styles';
import AddRoundedIcon from '@mui/icons-material/AddRounded';
import CheckCircleOutline from '@mui/icons-material/CheckCircleOutline';
import IncompleteCircle from '@mui/icons-material/IncompleteCircle';
import ConstructionRoundedIcon from '@mui/icons-material/ConstructionRounded';
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const Avatar = styled(MuiAvatar)(({ theme }) => ({
  width: 28,
  height: 28,
  backgroundColor: (theme.vars || theme).palette.background.paper,
  color: (theme.vars || theme).palette.text.secondary,
  border: `1px solid ${(theme.vars || theme).palette.divider}`,
}));

const ListItemAvatar = styled(MuiListItemAvatar)({
  minWidth: 0,
  marginRight: 12,
});

export default function DataBaseSelection() {
  const [company, setCompany] = React.useState(() => {
    return sessionStorage.getItem('selectedCompany') || '';
  });

const [menucontent, setmenucontent] = React.useState<Record<string, any[]>>(() => {
  const stored = sessionStorage.getItem('MenuContentsDBList');
  return stored ? JSON.parse(stored) : {};
});


useEffect(() => {
  sessionStorage.removeItem('selectedCompany');
  setCompany('');
}, []);


  useEffect(() => {
    // Run once on mount
    const fetchInitialData = async () => {
      

      try {
        const response = await fetch(`${API_BASE_URL}/dbselection`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ company: '' }),
        });

        if (!response.ok) throw new Error(`API error: ${response.status}`);
        const result = await response.json();
        sessionStorage.setItem('MenuContentsDBList', JSON.stringify(result.menueContent));
        setmenucontent(result.menueContent);


      } catch (error) {
        console.error('Initial API call failed:', error);
      }
    };

    fetchInitialData();

  }, []); // run only once
  
  

  const handleChange = async (event: SelectChangeEvent) => {
    console.log('handleChange fired:', event.target.value);

    const selectedValue = event.target.value as string;
    setCompany(selectedValue);
    sessionStorage.setItem('selectedCompany', selectedValue); // <-- save to sessionStorage
    window.dispatchEvent(new Event('company-updated'));
    
    if (!selectedValue) return;

    try {
      const response = await fetch(`${API_BASE_URL}/dbselection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: selectedValue }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const result = await response.json();
      console.log('Selection saved:', result);
    } catch (error) {
      console.error('Failed to save selection:', error);
    }
  };

const getIcon = (value: string) => {
  switch (value) {
    case 'demo-completed':
      return <CheckCircleOutline sx={{ fontSize: '1rem' }} />;
    case 'demo-live':
      return <IncompleteCircle sx={{ fontSize: '1rem' }} />;
    case 'current-project':
      return <ConstructionRoundedIcon sx={{ fontSize: '1rem' }} />;
    default:
      return null;
  }
};

const getColor = (value: string) => {
  switch (value) {
    case 'demo-completed':
      return '#C5900050';
    case 'demo-live':
      return '#C5900050';
    case 'current-project':
      return 'transparent';
    default:
      return null;
  }
};


return (
<Select
  labelId="company-select"
  id="company-simple-select"
  value={company}
  onChange={handleChange}
  displayEmpty
  fullWidth
  renderValue={(selected) => {
    if (!selected) return <em>Select Project</em>;
    const flatItems = Object.values(menucontent).flat();
    const selectedItem = flatItems.find(item => item.menu_value === selected);
    if (!selectedItem) return selected;
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Avatar sx={{ width: 24, height: 24 }}>
          {getIcon(selectedItem.menu_value)}
        </Avatar>
        <span>{selectedItem.primaryText}</span>
      </div>
    );
  }}
>
  <MenuItem disabled value="">
    <em>Select Project</em>
  </MenuItem>

  {Object.values(menucontent)
    .flat()
    .map((item) => (
      <MenuItem key={item.menu_value} value={item.menu_value} sx={{ bgcolor: getColor(item.menu_value) }}>
        <ListItemIcon>
          <Avatar sx={{ width: 24, height: 24 }}>
            {getIcon(item.menu_value)}
          </Avatar>
        </ListItemIcon>
        <ListItemText
          primary={item.primaryText}
          secondary={item.secondaryText}
        />
      </MenuItem>
    ))}
</Select>

);

}
