import * as React from 'react';
import { useEffect, useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';

import LoadingBar from './/LoadingBar'
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

 
export default function ListOfDocumentsLabeled() {

  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [dataloading, setdataloading] = useState(true);

  const [rowsZ, setRows] = useState([]);
  const [columnsZ, setColumns] = useState([]);

  const [DocumentAccuracy, setDocumentAccuracy] = useState(0);
  const [FalseNegative, setFalseNegative] = useState(0);


  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };
  
    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);


   useEffect(() => {
      if (!selectedCompany) return;
      setdataloading(true)

      const fetchProgress = async () => {
          setColumns([]);
          setRows([]);
          setDocumentAccuracy(0);
          setFalseNegative(0);
                  
        try {
          const response = await fetch(`${API_BASE_URL}/getcurrentprogress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company: selectedCompany, progresstype:'listofpropogateddocuments' }),
          });
          
          const data = await response.json();

          const raw = data?.data;
          console.log(raw);
          if (!raw || typeof raw !== 'object' || Object.keys(raw).length < 1) {
            console.warn('Unexpected or empty tabledata:', raw);
          setColumns([]);
          setRows([]);
          setDocumentAccuracy(0);
          setFalseNegative(0);

            return;
          }

          const columns = data.data.columns.map((col) => ({
            field: col,
            headerName: col,
            flex: 1,
          }));
          console.log(columns);

          const rows = data.data.rows.map((row, index) => ({
            id: row.docid, // or use row.docid if unique
            ...row,
          }));


          setDocumentAccuracy(data.data.accuracyDocuments.documentLevelAccuracy);
          setFalseNegative(data.data.accuracyDocuments.FalseNegative);          

          setColumns(columns);
          setRows(rows);

          setdataloading(false);

        } catch (error) {
          console.error('Failed to fetch progress:', error);
          setColumns([]);
          setRows([]);
        }
      };
  
      fetchProgress();
    }, [selectedCompany]);




  return (
<Box sx={{ width: '100%', overflowX: 'auto' }}>
  <Chip size="small" color="success" label={`${DocumentAccuracy}% Document Level Accuracy`} />
  <Chip size="small" color="error" label={`${FalseNegative}% False Negatives`} />

  <DataGrid
    autoHeight
    rows={rowsZ}
    columns={columnsZ.map((col) => ({ ...col, minWidth: 150 }))}
    getRowClassName={(params) =>
      params.indexRelativeToCurrentPage % 2 === 0 ? 'even' : 'odd'
    }
    initialState={{
      pagination: { paginationModel: { pageSize: 20 } },
    }}
    pageSizeOptions={[10, 20, 50]}
    disableColumnResize
    density="compact"
    checkboxSelection
    sx={{ minWidth: 'max-content' }}
    slotProps={{
      filterPanel: {
        filterFormProps: {
          logicOperatorInputProps: { variant: 'outlined', size: 'small' },
          columnInputProps: { variant: 'outlined', size: 'small', sx: { mt: 'auto' } },
          operatorInputProps: { variant: 'outlined', size: 'small', sx: { mt: 'auto' } },
          valueInputProps: {
            InputComponentProps: { variant: 'outlined', size: 'small' },
          },
        },
      },
    }}
      sx={{
    '& .MuiDataGrid-footerContainer': {
      justifyContent: 'flex-start',
    },
  }}
  />
</Box>

  );
}
