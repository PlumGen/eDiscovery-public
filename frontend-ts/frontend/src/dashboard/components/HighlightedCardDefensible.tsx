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
        <VerifiedRoundedIcon />
        <Typography
          component="h2"
          variant="subtitle2"
          gutterBottom
          sx={{ fontWeight: '600' }}
        >
          Repeatable & Defensible Results
        </Typography>
        <Typography sx={{ color: 'text.secondary', mb: '8px' }}>
          Every workflow is auditable and reproducible, producing consistent outcomes that can stand up to scrutiny in court or arbitration.
        </Typography>

      </CardContent>
    </Card>
  );
}
