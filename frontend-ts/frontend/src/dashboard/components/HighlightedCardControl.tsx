import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import ChevronRightRoundedIcon from '@mui/icons-material/ChevronRightRounded';
import InsightsRoundedIcon from '@mui/icons-material/InsightsRounded';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

import SecurityRoundedIcon from '@mui/icons-material/SecurityRounded';
import CenterFocusStrongRoundedIcon from '@mui/icons-material/CenterFocusStrongRounded';
import VerifiedRoundedIcon from '@mui/icons-material/VerifiedRounded';


export default function HighlightedCard() {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <SecurityRoundedIcon />
        <Typography
          component="h2"
          variant="subtitle2"
          gutterBottom
          sx={{ fontWeight: '600' }}
        >
          Data Control
        </Typography>
        <Typography sx={{ color: 'text.secondary', mb: '8px' }}>
          Your data always remains within your control, zero data retention and no external data sharing, ensuring full confidentiality and compliance with client and regulatory requirements.
        </Typography>

      </CardContent>
    </Card>
  );
}
