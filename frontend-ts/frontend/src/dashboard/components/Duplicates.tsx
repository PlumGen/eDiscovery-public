import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, Button, Paper, CircularProgress } from '@mui/material';
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";



export default function Duplicates() {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [duplicateDefinitionData, setDuplicateDefinitionData] = useState({
    lo: null,
    hi: null,
    similarity: null,
    sourceText: "",
    targetText: "",
    status: "init", // can be 'init', 'in_progress', 'complete', 'error'
  });
  const [buttonAnswer, setbuttonAnswer] = useState("");

  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };

    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);

useEffect(() => {
  const selected = sessionStorage.getItem("selectedCompany");
  if (selected !== selectedCompany) {
    setSelectedCompany(selected);
  }
}, []);

useEffect(() => {
  if (!selectedCompany) return;
  setIsLoading(true);
  const fetchInitial = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/getnextnearduplicate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: selectedCompany,
          lo: null,
          hi: null,
          last_answer: null,
        }),
      });

      if (!response.ok) throw new Error('Failed to load initial data');
      const result = await response.json();
      console.log("Initial response data:", result); // 🔍 Add this
      const {
        lo,
        hi,
        similarity,
        source_text,
        target_text,
        status
      } = result.data;

      setDuplicateDefinitionData({
        lo,
        hi,
        similarity,
        sourceText: source_text,
        targetText: target_text,
        status
      });
      setIsLoading(false);
    } catch (err) {
      console.error('Initial load failed:', err);
    }
  };

  fetchInitial();
}, [selectedCompany]);

useEffect(() => {
  if (!selectedCompany || !buttonAnswer) return;
  setIsLoading(true);
  const fetchTexts = async () => {
    try {

      const response = await fetch(`${API_BASE_URL}/getnextnearduplicate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: selectedCompany,
          lo: duplicateDefinitionData.lo,
          hi: duplicateDefinitionData.hi,
          last_answer: buttonAnswer,
        }),
      });

      if (!response.ok) throw new Error('Failed to load texts');
      const result = await response.json();
      const {
        lo,
        hi,
        similarity,
        source_text,
        target_text,
        status
      } = result.data;

      setDuplicateDefinitionData({
        lo:lo,
        hi:hi,
        similarity:similarity,
        sourceText: source_text,
        targetText: target_text,
        status:status
      });
      setIsLoading(false);
    } catch (err) {
      console.error('Error loading candidate:', err);
      setDuplicateDefinitionData({
        lo: null,
        hi: null,
        similarity: null,
        sourceText: '',
        targetText: '',
        status: 'init',
      });
    } finally {
      setbuttonAnswer("");
      setIsLoading(false);
    }
  };

  fetchTexts();
}, [selectedCompany, buttonAnswer]); 


  return (
<Box sx={{ p: 4, maxWidth: '1200px', margin: '0 auto' }}>
  <Typography variant="h5" gutterBottom textAlign="center">
    Near-Duplicate Definition
  </Typography>

      {isLoading ? (
    <CircularProgress />
  ) : ( 

  <Box sx={{ display: 'flex', gap: 2, mt: 2, height: '70vh' }}>



    <Paper sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
      <Typography variant="subtitle1" gutterBottom>
        Document A
      </Typography>
      <Typography variant="body2" whiteSpace="pre-wrap">
          {
            duplicateDefinitionData.status === 'complete'
              ? 'Stage Complete'
              : isLoading
                ? 'Loading...'
                : (duplicateDefinitionData.sourceText)
          }

      </Typography>
    </Paper>

    <Paper sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
      <Typography variant="subtitle1" gutterBottom>
        Document B
      </Typography>
      <Typography variant="body2" whiteSpace="pre-wrap">
        {
          duplicateDefinitionData.status === 'complete'
            ? 'Stage Complete'
            : isLoading
              ? 'Loading...'
              : (duplicateDefinitionData.targetText)
        }

      </Typography>
    </Paper>

  </Box>
    )}

  <Box mt={3} display="flex" justifyContent="center" gap={2}>
      <Button
        variant="contained"
        color="secondary"
        onClick={() => {
          setIsLoading(true);
          setbuttonAnswer("n");
        }}
      >
        No - Distinct Information
      </Button>
      <Button
        variant="contained"
        color="primary"
        onClick={() => {
          setIsLoading(true);
          setbuttonAnswer("y");
        }}
      >
        Yes - Near-Duplicates
      </Button>
  </Box>
</Box>


  );
}
