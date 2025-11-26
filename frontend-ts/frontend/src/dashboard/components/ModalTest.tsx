import React, { useState } from 'react';
import { Modal, Box, Typography, Button } from '@mui/material';

export default function ModalTest() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button variant="contained" onClick={() => setOpen(true)}>Open Modal</Button>

      <Modal open={open} onClose={() => setOpen(false)}>
        <Box sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          bgcolor: 'background.paper',
          boxShadow: 24,
          p: 4,
          minWidth: 300,
          borderRadius: 2,
        }}>
          <Typography variant="h6">Test Modal</Typography>
          <Typography>This is working</Typography>
        </Box>
      </Modal>
    </>
  );
}
