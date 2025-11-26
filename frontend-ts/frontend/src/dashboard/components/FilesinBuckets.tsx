import * as React from 'react';
import { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Button, Stack, Box } from '@mui/material';
import TableChartIcon from '@mui/icons-material/TableChart';   // for tabulated data
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile'; // for document dump


const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";


const PASSWORD = "0000";
const askPassword = () => {
  const input = window.prompt("Enter password:");
  return input === PASSWORD;
};


export default function FilesinBuckets() {
  const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);



  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Name', width: 300 },
    { field: 'size', headerName: 'Size (bytes)', type: 'number', width: 130 },
    { field: 'updated', headerName: 'Last Updated', width: 200 },
    { field: 'content_type', headerName: 'Content Type', width: 200 },
  ];

  const fetchData = async (type?: string) => {
    if (!selectedCompany) return;
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/getitemsinbucket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: selectedCompany,
          userinjesttype: type
        }),
      });

      const result = await response.json();
      const formattedRows = (result.data || []).map((item: any, index: number) => ({
        id: index,
        ...item,
        updated: new Date(item.updated).toLocaleString(),
      }));

      setRows(formattedRows);
    } catch (error) {
      console.error('Failed to fetch items from bucket:', error);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    const handleCompanyUpdate = () => {
      setSelectedCompany(sessionStorage.getItem('selectedCompany'));
    };

    window.addEventListener('company-updated', handleCompanyUpdate);
    return () => window.removeEventListener('company-updated', handleCompanyUpdate);
  }, []);

  useEffect(() => {
    fetchData('');
  }, [selectedCompany]);


return (
  <Box
    sx={{
      height: '100vh', // fill full window height
      width: '50vw',  // fill full window width
      display: 'flex',
      flexDirection: 'column',
    }}
  >
    {/* Button section (fixed height) */}
    <Box sx={{ p: 2, flexShrink: 0 }}>

        <Button
          variant="contained"
          startIcon={<TableChartIcon />}
          onClick={() => {
            if (askPassword()) fetchData('table');
            else alert("Incorrect password");
          }}
        >
          Ingest Tabulated Data
        </Button>

        <Button
          variant="contained"
          startIcon={<InsertDriveFileIcon />}
          onClick={() => {
            if (askPassword()) fetchData('document');
            else alert("Incorrect password");
          }}
        >
          Ingest Document Dump
        </Button>

    </Box>

    {/* DataGrid (fills remaining space) */}
    <Box sx={{ flex: 1, minHeight: 0 }}>
      <DataGrid
        loading={loading}
        checkboxSelection
        rows={rows}
        columns={columns}
        getRowClassName={(params) =>
          params.indexRelativeToCurrentPage % 2 === 0 ? 'even' : 'odd'
        }
        initialState={{
          pagination: { paginationModel: { pageSize: 20 } },
        }}
        pageSizeOptions={[10, 20, 50]}
        disableColumnResize
        density="compact"
      />
    </Box>
  </Box>
);


}
