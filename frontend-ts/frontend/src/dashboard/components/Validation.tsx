// MUI-only rewrite of Sampleresults.jsx
import React, { useEffect, useState, useRef } from "react";
import {
  Box, Container, Grid, Paper, Typography, List, ListItem,
  ListItemText, IconButton, Tooltip, Dialog, DialogTitle,
  DialogContent, DialogActions, Button, FormControl, InputLabel,
  Select, MenuItem, TextField, Checkbox, FormControlLabel,
  CircularProgress
} from "@mui/material";
import { ChevronLeft, ChevronRight, Info as InfoIcon } from "@mui/icons-material";
import { ListItemButton } from "@mui/material";
import Chip from '@mui/material/Chip';
import OutlinedInput from '@mui/material/OutlinedInput';
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

import LinearProgress from '@mui/material/LinearProgress';
import { useTheme } from '@mui/material/styles';

function HorizontalRatioBar({ title, value }: { title: string; value: number }) {
  const theme = useTheme();

  const barColor = value > 0.1
    ? theme.palette.error.main
    : theme.palette.primary.main;

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="subtitle2" noWrap>
        {title}
      </Typography>
      <Box display="flex" alignItems="center" gap={1}>
        <Box sx={{ flexGrow: 1 }}>
          <LinearProgress
            variant="determinate"
            value={Math.min(value * 100, 100)}
            sx={{
              height: 8,
              borderRadius: 5,
              [`& .MuiLinearProgress-bar`]: {
                backgroundColor: barColor,
              },
            }}
          />
        </Box>
        <Typography variant="body2" sx={{ minWidth: 40 }} noWrap>
          {(value * 100).toFixed(1)}%
        </Typography>
      </Box>
    </Box>
  );
}


function CategoryList({ selectedItems, onSelect, data }) {
  console.log('CategoryList')
  
  console.log(data)

  return (
    <Paper sx={{ p: 1, height: '100%', overflowY: 'auto' }}>
      <Typography variant="h6" gutterBottom>Categories/Issues</Typography>
      <List dense>
{Object.entries(data.labelpropstatus).map(([key, item]) => (
  <ListItem key={key} disablePadding>
    <ListItemButton
      selected={selectedItems.includes(key)}
      onClick={() => onSelect(key)}
      sx={{ justifyContent: 'space-between' }}
    >
<ListItemText

primary={
  <Tooltip title={key} placement="top">
    <span>{key.slice(0, 20)}{key.length > 20 ? '…' : ''}</span>
  </Tooltip>
}
  secondary={
    <Box display="flex" gap={1} mt={0.5}>
      <Chip size="small" label={`User: ${item.userlabel}`} />
      <Chip size="small" color="primary" label={`Prop: ${item.propogation}`} />
    </Box>
  }
/>
<Box sx={{ flexShrink: 0 }}>
  <Tooltip title={key || ''} placement="left">
    <IconButton size="small">
      <InfoIcon fontSize="small" />
    </IconButton>
  </Tooltip>
</Box>

    </ListItemButton>
  </ListItem>
))}
      </List>
    </Paper>
  );
}

function EmailDisplay({ email, onOptionChangeMaster, onMultiLabelChange, allLabels }) {
  const topicMap = {
    [email.user_label_name]: email.user_label_name,
    ...(email.user_reassign && { [email.user_reassign]: email.user_reassign })
  };

  const [selectedEmail, setSelectedEmail] = useState(null);

  const handleOpenModal = () => setSelectedEmail(email);
  const handleCloseModal = () => setSelectedEmail(null);

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box mb={2} display="flex" flexDirection="column" gap={1}>
      <Typography variant="body1">
        <strong>Classification:</strong>{" "}
        {email.user_reassign && email.user_reassign !== email.label ? (
          <>
            <s style={{ color: 'red' }}>{topicMap[email.user_label_name]}</s> → {allLabels.labelmapping[topicMap[email.user_reassign]]}
          </>
        ) : (
          topicMap[email.user_label_name] || 'None'
        )}
      </Typography>
        {/* ✅ Multi-label dropdown here */}
        
        <Box sx={{ maxWidth: '100%' }}>
        <Box mb={2} display="flex" flexDirection="column" gap={1}>
          
            <FormControl fullWidth size="small">
              <InputLabel>Reject and Reassign or Accept</InputLabel>
              <Select
                multiple
                value={email.multiLabels || []}
                onChange={(e) => onMultiLabelChange(e, email)}
                input={<OutlinedInput label="Reject and Reassign or Accept" />}
                

renderValue={(selected) => (
  <Box
    title={selected.join(', ')}
    sx={{
      display: 'block',
      overflow: 'hidden',
      whiteSpace: 'nowrap',
      textOverflow: 'ellipsis',
      width: '100%',
    }}
  >

    {/* {selected.join(', ')} */}
  </Box>
)}


                MenuProps={{
                  PaperProps: {
                    sx: {
                      maxHeight: 300,
                      maxWidth: 300,
                    },
                  },
                }}

sx={{
  width: '100%',
  maxWidth: '100%',
  '& .MuiSelect-select': {
    display: 'block',
    width: '100%',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis',
  },
  '& .MuiSelect-multiple': {
    paddingTop: '8px',
    paddingBottom: '8px',
  },
  '& .MuiOutlinedInput-root': {
    height: 40,
    width: '100%',
    maxWidth: '100%',
    overflow: 'hidden',
  },
  '& .MuiOutlinedInput-input': {
    padding: '0 8px',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis',
    width: '100%',
  },
}}




              >

                {Object.entries(allLabels.labelpropstatus).map(([key]) => (
                  <MenuItem key={key} value={key}>
                    <Checkbox checked={(email.multiLabels || []).includes(key)} />
                    <ListItemText primary={key} />
                  </MenuItem>
                ))}
                
              </Select>

            </FormControl>




        </Box>
        </Box>

        {/*
        <Button variant="outlined" onClick={handleOpenModal}>
          View Training Texts
        </Button>
        */}
      </Box>

      <Typography variant="subtitle2"><strong>Message ID:</strong> {email.docid}</Typography>
      <Typography variant="body2"><strong>Confidence:</strong> {email.confidence.toFixed(2)}</Typography>
      <Typography variant="body1" mt={2}>{email.clean_text}</Typography>

      <Dialog open={!!selectedEmail} onClose={handleCloseModal} maxWidth="md" fullWidth>
        <DialogTitle>Training Texts</DialogTitle>
        <DialogContent dividers>
          {selectedEmail?.textsMasters?.length > 0 ? (
            selectedEmail.textsMasters.map((item, index) => (
              <Box key={index} mb={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Reassign</InputLabel>
                  <Select
                    value={item.selectedOptionMaster || ""}
                    onChange={(e) => onOptionChangeMaster(e, item)}
                  >
                    <MenuItem value="">Reassign</MenuItem>
                    <MenuItem value={email.label}>{email.label}</MenuItem>
                    {email.user_reassign && (
                      <MenuItem value={email.user_reassign}>{email.user_reassign}</MenuItem>
                    )}
                  </Select>
                </FormControl>
                <Typography variant="body2" mt={1}>{item.clean_text}</Typography>
              </Box>
            ))
          ) : (
            <Typography variant="body2">No training texts.</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModal}>Close</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}




export default function Validation() {
  const [selectedItems, setSelectedItems] = useState([]);
  const initialData = { labelpropstatus: {}, labelmapping: {} };
  const [data, setData] = useState(initialData);


  const [emails, setEmails] = useState([]);
  const [page, setPage] = useState(1); 
  const [searchText, setSearchText] = useState('');
  const [selectedReverse, setSelectedReverse] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedaction, setselectedaction] = useState('random_sample');

  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [reassignlabels, setreassignlabels] = useState([]);

  const [rejectionstats, setrejectionstats] = useState({});


  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };

    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);


  useEffect(() => {
        fetch(`${API_BASE_URL}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({company: selectedCompany})}).then(res => res.json()).then(setData).catch(console.error);
                  }, [selectedCompany]);

useEffect(() => {
  setLoading(true);
  setrejectionstats({});

  const formattedLabels = Object.entries(reassignlabels).map(([key, multilabels]) => {
    const [row_hash, row_hash_model] = key.split("__");
    return { row_hash, row_hash_model, multilabels };
  });

  fetch(`${API_BASE_URL}/action?page=${page}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      company: selectedCompany,
      selectedaction,
      page,
      text: searchText,
      selected_categories: selectedItems,
      selected_categories_reverse: selectedReverse,
      reassignlabels: formattedLabels
    })
  })
     .then(res => res.json())
    .then(res => {
      setEmails(res.data);
      setrejectionstats(res.rejectionStats);
    })
    .then(() => setreassignlabels({}))
    .catch(() => setEmails([]))
    .catch(() => setrejectionstats({}))    
    .finally(() => setLoading(false));
}, [selectedItems, page, searchText, selectedReverse, selectedCompany, selectedaction]);

const handleSelect = (label) => {
  setSelectedItems(prev =>
    prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label]
  );
};

const handleMultiLabelChange = (e, email) => {
  const newLabels = e.target.value;
  const rowHash = email.row_hash;
  const rowHash_model = email.row_hash_model;

  // Update email list with new labels
  setEmails(prev =>
    prev.map(item =>
      item.row_hash === rowHash
        ? { ...item, multiLabels: newLabels }
        : item
    )
  );

  // Fix object key: [rowHash, rowHash_model] is treated as a string like "rowHash,rowHash_model"
  // Use nested object or a joined key string instead
  setreassignlabels(prev => ({
    ...prev,
    [`${rowHash}__${rowHash_model}`]: newLabels
  }));
};






  return (
  <Box sx={{ p: 1, maxWidth: '1600px', margin: '0 auto' }}>
  <Box display="flex" gap={2} height="100vh">
   

    {/* Left Panel: Category List */}
    <Paper sx={{ flex: '0 0 25%', p: 2, overflowY: 'auto' }}>
      <CategoryList
        selectedItems={selectedItems}
        onSelect={handleSelect}
        data={data}
      />
    </Paper>

    {/* Right Panel: Controls + Results + Pagination */}
    
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
    


               <Box sx={{ flexShrink: 0, display: 'flex', flexDirection: 'column', py: 1 }}>


                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0}>
                        <HorizontalRatioBar
                          title={`Rejection Rate ${rejectionstats?.mismatched_reassigned ?? 0}/${rejectionstats?.total_reassigned ?? 0} Pages`}
                          value={
                            rejectionstats?.total_reassigned
                              ? rejectionstats.mismatched_reassigned / rejectionstats.total_reassigned
                              : 0
                          }
                          />
                        </Box>

                  {/* Search + Reverse */}
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1} >

                                    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                      <Button
                                        variant="contained"
                                        color="primary"
                                        size="small"
                                        onClick={() => setselectedaction('random_sample')}
                                        sx={{
                                          px: 0.5,
                                          py: 0.25,
                                          fontSize: '0.6rem',
                                          minHeight: '20px',
                                          lineHeight: 1,
                                        }}
                                      >
                                        Random Sample
                                      </Button>

                                      <Button
                                        variant="contained"
                                        color="primary"
                                        size="small"
                                        onClick={() => setselectedaction('least_confidence')}
                                        sx={{
                                          px: 0.5,
                                          py: 0.25,
                                          fontSize: '0.6rem',
                                          minHeight: '20px',
                                          lineHeight: 1,
                                        }}
                                      >
                                        Least Confidence
                                      </Button>
                                    </Box>



                    <TextField
                      size="small"
                      placeholder="Search..."
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          setselectedaction('search_text');
                        }
                      }}
                      sx={{ flexGrow: 1, mr: 2 }}
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedReverse}
                          onChange={(e) => setSelectedReverse(e.target.checked)}
                        />
                      }
                      label="Reverse"
                    />
                  </Box>


                  </Box>


        {/* Email Results  */}
        <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
        <Paper sx={{ flex: 1, p: 2, overflowY: 'auto', minHeight: 0 }}>
          {loading ? (
            <CircularProgress />
          ) : emails.length > 0 ? (
            emails.map(chunk => (
          <EmailDisplay
            key={chunk.row_hash}
            email={chunk}

            onMultiLabelChange={handleMultiLabelChange}
            allLabels={data}
          />


            ))
          ) : (
            <Typography>No results.</Typography>
          )}
        </Paper>
        </Box>


        {/* Pagination */}
           <Box sx={{ height: 40, flexShrink: 0, display: 'flex', alignItems: 'center' }}>

          <IconButton onClick={() => setPage((p) => Math.max(1, p - 1))}>
            <ChevronLeft />
          </IconButton>
          <Typography>Page {page}</Typography>
          <IconButton onClick={() => setPage((p) => p + 1)}>
            <ChevronRight />
          </IconButton>
        </Box>




    </Box>
  </Box>
</Box>

      );
}
