import React, { useState, useEffect, useCallback  } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  TextField, CircularProgress, Divider
} from '@mui/material';

import { dataDisplayCustomizations } from '../../shared-theme/customizations/dataDisplay';
const API_BASE_URL     = import.meta.env.VITE_API_URL || "/api";
const possibleMisMatch = import.meta.env.ENABLELABELCHECK || "False";

import { ToggleButton, ToggleButtonGroup, Modal  } from '@mui/material';
import ModalTest from './ModalTest';

export default function ManualLabel() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingText, setIsLoadingText] = useState(false);

  const [categories, setCategories] = useState<string[]>([
  ]);
  const [possiblemisMatch, setpossiblemisMatch] = useState<string[]>([
  ]);

  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [newCategory, setNewCategory] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));



  const [idpagenumber, setidpagenumber] = useState(0);  
  const [countlabelCandidates, setcountlabelCandidates] = useState(0);    
  const [paginationDirection, setPaginationDirection] = useState<'next' | 'prev' | null>(null);


    
  const [chunkText, setChunkText] = useState("");
  const [documentText, setdocumenttext] = useState("");
  const [cleanText, setCleantext] = useState("");
  const [rowHashModel, setrowHashModel] = useState("");

  const [labelFilter, setLabelFilter] = useState<'labeled' | 'unlabeled' | null>(null);

  const [openModal, setOpenModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);

  const [trackProgress, settrackProgress] = useState({})

  const handleOpenModal = (entry) => {
    setSelectedEntry(entry);
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    setOpenModal(false);
    setSelectedEntry(null);
  };


 const cycleFilter = () => {
    setLabelFilter(prev =>
      prev === null ? 'labeled' :
      prev === 'labeled' ? 'unlabeled' :
      null
    );
  };

const getLabel = () => {
  if (labelFilter === 'labeled') return `Labeled Only: ${trackProgress.labeled}`;
  if (labelFilter === 'unlabeled') return `Unlabeled Only: ${trackProgress.unlabeled}`;
  return `All: ${trackProgress.All}`;
};



const getColorForSimilarity = (similarity: number) => {
  const ratio = Math.min(Math.max((similarity - 0.7) / 0.7, 0), 1); // normalize 0.5 → 0, 1 → 1
  const red = Math.round(255 * ratio);
  const green = Math.round(255 * (1 - ratio));
  return `rgb(${red},${green},0)`; // green→red gradient
};

// get texts to
const fetchTexts = useCallback(async (direction: 'next' | 'prev' | null = null, currentId: number | null = null, specific_row_hash_model: string | null = null, markstagecomplete: string | null = null) => {
  if (!selectedCompany) return;
  setIsLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/getnextcandidatelabel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company: selectedCompany,
        current_id: currentId,
        direction,
        onlyUnlabeled: labelFilter,
        specific_row_hash_model:specific_row_hash_model, 
        markstagecomplete:markstagecomplete
      }),
    });

    if (!response.ok) throw new Error('Failed to load texts');

    const result = await response.json();
    const candidate = result.data;

    // ✅ Update state from response
    setidpagenumber(candidate.id);
    setChunkText(candidate.chunk_text);
    setCleantext(candidate.clean_text);
    setdocumenttext(candidate.documenttext);
    setrowHashModel(candidate.row_hash_model);
    setcountlabelCandidates(candidate.countlabelCandidates);

    settrackProgress({labeled:candidate.countlabelCandidates-candidate.unlabeledCandidates,
                      unlabeled:candidate.unlabeledCandidates,
                      All:candidate.countlabelCandidates}
                      )
    setIsLoading(false);

    if (candidate.user_label) {
      try {
        const parsed = typeof candidate.user_label === 'string'
          ? JSON.parse(candidate.user_label)
          : candidate.user_label;

        const values = Array.isArray(parsed)
          ? parsed
          : Object.values(parsed);

        setSelectedCategories(new Set(values));
      } catch (err) {
        console.error("Failed to parse user_label", err);
        setSelectedCategories(new Set());
      }
    } else {
      setSelectedCategories(new Set());
    }

  } catch (err) {
    console.error('Error loading categories:', err);
    setidpagenumber(null);
    setChunkText("");
    setCleantext("");
    setdocumenttext("");
    setrowHashModel("");
  }
}, [selectedCompany, labelFilter]);


useEffect(() => {
  fetchTexts(null, idpagenumber, null, null);
}, [fetchTexts]);


useEffect(() => {
  if (!selectedCompany) return;

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/addcategory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: selectedCompany }),
      });

      if (!response.ok) throw new Error('Failed to load categories');

      const result = await response.json();
      const latestCategories = result.data.map((row: any) => row.issuedefinition);
      setCategories(latestCategories);
    } catch (err) {
      console.error('Error loading categories:', err);
      setCategories([]);
    }
  };

  fetchCategories();
}, [selectedCompany]);

  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };

    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);

  const sampleText = cleanText
  
  const handleToggle = (category: string) => {
    const newSet = new Set(selectedCategories);
    if (newSet.has(category)) {
      newSet.delete(category);
    } else {
      newSet.add(category);
    }
    setSelectedCategories(newSet);
  };

const handleAddCategory = async () => {
  if (!newCategory.trim()) return;

  try {
    const response = await fetch(`${API_BASE_URL}/addcategory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company: selectedCompany, category: newCategory }),
    });

    if (!response.ok) throw new Error('API Error');

    const result = await response.json();
    const updatedCategories = result.data.map((row: any) => row.issuedefinition); // assuming backend returns rows
    setCategories(updatedCategories);
    setNewCategory('');
    console.log('Category added:', result);
  } catch (err) {
    console.error('Failed to add category:', err);
  }
};


  const handleSubmit = async (delta = 'next') => {

    if (!selectedCategories) return;
    setIsLoading(true);

  setPaginationDirection(delta);  
  try {
    const response = await fetch(`${API_BASE_URL}/labelthiscandidate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company: selectedCompany, id: idpagenumber,  row_hash_model:rowHashModel, user_label:Array.from(selectedCategories)}),
    });

    if (!response.ok) throw new Error('API Error');

    const result = await response.json();
    if (result.status === 'ok') {


      setpossiblemisMatch(result.mismatch)

      setSelectedCategories(new Set());
      await fetchTexts(delta, idpagenumber, null, null);
      setIsLoading(false);
    };

    console.log('Category added:', `Selected categories:\n${Array.from(selectedCategories).join(', ')}`);
  } catch (err) {
    console.error('Failed to add category:', err);
  }




  };


  return (


  <Box sx={{ p: 4, maxWidth: '1200px', margin: '0 auto' }}>

    <Modal open={openModal} onClose={handleCloseModal}>
      <Box     sx={{
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      bgcolor: 'background.paper',
      boxShadow: 24,
      p: 4,
      minWidth: 400,
      maxHeight: '80vh',          // ⬅️ Limit height
      overflow: 'auto',           // ⬅️ Enable scrolling
      borderRadius: 2,
    }}>


        {selectedEntry ? (

                          <Box sx={{ p: 4, maxWidth: '1200px', margin: '0 auto' }}>
                            <Typography variant="h5" gutterBottom textAlign="center">
                             Label Sanity Check
                            </Typography>
                          
                            <Box sx={{ display: 'flex', gap: 2, mt: 2, height: '70vh' }}>
                              <Paper sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
                                <Typography variant="subtitle1" gutterBottom>
                                  Document A
                                </Typography>
                                <Typography variant="body2" whiteSpace="pre-wrap">
                                  {selectedEntry.source_clean_text}
                          
                                </Typography>
                              </Paper>
                          
                              <Paper sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
                                <Typography variant="subtitle1" gutterBottom>
                                  Document B
                                </Typography>
                                <Typography variant="body2" whiteSpace="pre-wrap">
                                  {selectedEntry.target_clean_text}
                          
                                </Typography>
                              </Paper>
                            </Box>
                          
                            <Box mt={3} display="flex" justifyContent="center" gap={2}>
                                    <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                                    <List dense>
                                      {Array.from(selectedEntry.source_user_label).map((category, index) => (
                                        <React.Fragment key={category}>
                                          <ListItem disablePadding>
                                            <ListItemIcon>
                                              <Checkbox
                                                edge="start"
                                                checked
                                                tabIndex={-1}
                                                disableRipple
                                                onChange={() => handleToggle(category)}
                                              />
                                            </ListItemIcon>
                                            <ListItemText primary={category} />
                                          </ListItem>
                                          {index < selectedCategories.size - 1 && (
                                            <Divider sx={{ mx: 1, borderBottomWidth: 2, borderColor: 'grey.700' }} />
                                          )}
                                        </React.Fragment>
                                      ))}
                                    </List>

                                        <Button
                                          variant="contained"
                                          color="secondary"
                                          onClick={() => {
                                            fetchTexts(null, null, selectedEntry.source_row_hash, null);
                                            handleCloseModal();

                                          }}
                                        >
                                          Relabel Document A
                                        </Button>

                                    </Box>

                                      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
                                    <List dense>
                                      {Array.from(selectedEntry.target_user_label).map((category, index) => (
                                        <React.Fragment key={category}>
                                          <ListItem disablePadding>
                                            <ListItemIcon>
                                              <Checkbox
                                                edge="start"
                                                checked
                                                tabIndex={-1}
                                                disableRipple
                                                onChange={() => handleToggle(category)}
                                              />
                                            </ListItemIcon>
                                            <ListItemText primary={category} />
                                          </ListItem>
                                          {index < selectedCategories.size - 1 && (
                                            <Divider sx={{ mx: 1, borderBottomWidth: 2, borderColor: 'grey.700' }} />
                                          )}
                                        </React.Fragment>
                                      ))}
                                    </List>

                                        <Button
                                          variant="contained"
                                          color="secondary"
                                          onClick={() => {
                                            fetchTexts(null, null, selectedEntry.target_row_hash, null);
                                            handleCloseModal();
                                          }}
                                        >
                                          Relabel Document B
                                        </Button>

                                    </Box>
                            </Box>
                          </Box>


        ) : (
          <Typography>No entry selected</Typography>
        )}
      </Box>
    </Modal>



  <Typography variant="h5" gutterBottom textAlign="center">
    Manual Document Classification
  </Typography>

    <Button variant="contained" onClick={cycleFilter}>
      {getLabel()}
    </Button>


  {/* Outer container with fixed height */}
  <Box sx={{ display: 'flex', gap: 2, mt: 2, height: '70vh' }}>

    {/* Category List */}
    <Paper sx={{ width: '30%', p: 2, display: 'flex', flexDirection: 'column' }}>
      <Typography variant="subtitle1" gutterBottom>
        Select Categories
      </Typography>

      <Box display="flex" gap={1} mb={2}>
        <TextField
          fullWidth
          size="small"
          variant="outlined"
          placeholder="New category"
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
        />
        <Button variant="contained" onClick={handleAddCategory}>
          Add
        </Button>
      </Box>

      {/* Scrollable category list */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        <List dense>
          {categories.map((category, index) => (
            <React.Fragment key={category}>
              <ListItem disablePadding>
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={selectedCategories.has(category)}
                    onChange={() => handleToggle(category)}
                    tabIndex={-1}
                    disableRipple
                  />
                </ListItemIcon>
                <ListItemText primary={category} />
              </ListItem>
              {index < categories.length - 1 && (
                <Divider sx={{ mx: 1, borderBottomWidth: 2, borderColor: 'grey.700' }} />
              )}
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Paper>

    {/* Document Viewer */}
          {isLoading ? (
        <CircularProgress />
      ) : ( 

    <Paper sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
      <Typography variant="subtitle1" gutterBottom>
        Document Text  ({idpagenumber}/{countlabelCandidates})
      </Typography>
      <Typography variant="body2" whiteSpace="pre-wrap">
        {sampleText}
      </Typography>
    </Paper>
      )}
    {/* Possible Mismatch */}
    {possibleMisMatch === true && (
        <Paper sx={{ width: '10%', p: 2, display: 'flex', flexDirection: 'column' }}>
          <Typography variant="subtitle1" gutterBottom>
            Label Check
          </Typography>

          <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
            <List dense>
              {Array.isArray(possiblemisMatch) &&
                possiblemisMatch.map((entries, index) => (
                  <React.Fragment key={entries.id}>


        <ListItem key={entries.id} disableGutters sx={{ pl: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'left', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                backgroundColor: getColorForSimilarity(entries.similarity),
                borderRadius: 1,
                flexShrink: 0,
                cursor: 'pointer',
              }}
          onClick={() => {
            console.log('Clicked', entries);
            handleOpenModal(entries);
          }}
            />
          </Box>
        </ListItem>


                  {index < possiblemisMatch.length - 1 && (
                    <Divider sx={{ mx: 1, borderBottomWidth: 2, borderColor: 'grey.700' }} />
                  )}
                </React.Fragment>
              ))}
            </List>
          </Box>
        </Paper>

)}

  </Box>


  {/* Pagination Buttons */}
  <Box mt={3} display="flex" justifyContent="center" gap={2}>
    <Button variant="contained" disabled={selectedCategories.size === 0} onClick={() => handleSubmit('prev')}>
      Previous Page
    </Button>
    <Button variant="contained" disabled={selectedCategories.size === 0} onClick={() => handleSubmit('next')}>
      Next Page
    </Button>
  </Box>

      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
      <List dense>
        {Array.from(selectedCategories).map((category, index) => (
          <React.Fragment key={category}>
            <ListItem disablePadding>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked
                  tabIndex={-1}
                  disableRipple
                  onChange={() => handleToggle(category)}
                />
              </ListItemIcon>
              <ListItemText primary={category} />
            </ListItem>
            {index < selectedCategories.size - 1 && (
              <Divider sx={{ mx: 1, borderBottomWidth: 2, borderColor: 'grey.700' }} />
            )}
          </React.Fragment>
        ))}
      </List>
      </Box>

  <Box mt={15} display="flex" justifyContent="center" gap={2}>
    <Button variant="contained" disabled={trackProgress.unlabeled > 0} onClick={() => fetchTexts(null, null, null, 'complete')}>
      Mark Stage as Complete
    </Button>
  </Box>

</Box>



  );
}
