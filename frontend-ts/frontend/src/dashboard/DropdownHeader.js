import {
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    OutlinedInput,
    Checkbox,
    ListItemText
  } from '@mui/material';

export default function DropdownHeader({ options, selected, setSelected, textdisplay }) {
    // Determine the background color based on whether current selection differs from all options
    const backgroundColor = selected.length !== options.length ? '#f0f0f0' : 'white';
  
    return (
      <FormControl size="small" fullWidth>
        <InputLabel id="dropdown-header-label">{textdisplay}</InputLabel>
        <Select
          labelId="dropdown-header-label"
          id="dropdown-header-select"
          multiple
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          input={<OutlinedInput label={textdisplay} style={{ backgroundColor }} />}
          renderValue={(selected) => 
            selected.length === 0 ? <em>None selected</em> :
            selected.length > 1 ? `${selected.length} selected` : selected.join(', ')
          }
        >
          {options.map((option) => (
            <MenuItem key={option} value={option}>
              <Checkbox checked={selected.indexOf(option) > -1} />
              <ListItemText primary={option} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  }
  