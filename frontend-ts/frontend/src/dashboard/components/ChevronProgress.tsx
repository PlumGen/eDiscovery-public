import * as React from 'react';
import { useEffect, useState } from 'react';
import clsx from 'clsx';
import { animated, useSpring } from '@react-spring/web';
import { TransitionProps } from '@mui/material/transitions';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Collapse from '@mui/material/Collapse';
import Typography from '@mui/material/Typography';
import { RichTreeView } from '@mui/x-tree-view/RichTreeView';
import { useTreeItem, UseTreeItemParameters } from '@mui/x-tree-view/useTreeItem';
import {
  TreeItemContent,
  TreeItemIconContainer,
  TreeItemLabel,
  TreeItemRoot,
} from '@mui/x-tree-view/TreeItem';
import { TreeItemIcon } from '@mui/x-tree-view/TreeItemIcon';
import { TreeItemProvider } from '@mui/x-tree-view/TreeItemProvider';
import { TreeViewBaseItem } from '@mui/x-tree-view/models';
import { useTheme } from '@mui/material/styles';

import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { Breadcrumbs, Link } from '@mui/material';

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";


type Color =
  | 'primary'
  | 'secondary'
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'textPrimary'
  | 'textSecondary'
  | 'disabled';


// Optional: map legacy names from your API to standard MUI names
// Map API colors -> MUI palette keys
const normalizeColor = (c?: string): Color | undefined => {
  if (!c) return undefined;
  const alias: Record<string, Color> = {
    green: 'success',
    red: 'error',
    yellow: 'warning',
  };
  return alias[c] ?? 'textPrimary';
};


type ExtendedTreeItemProps = {
  color?: Color;
  id: string;
  label: string;
};


const bgFrom = (theme: useTheme, c?: Color) => {
  switch (c) {
    case 'primary':   return theme.palette.primary.main;
    case 'secondary': return theme.palette.secondary.main;
    case 'success':   return theme.palette.success.main;
    case 'error':     return theme.palette.error.main;
    case 'warning':   return theme.palette.warning.main;
    case 'info':      return theme.palette.info.main;
    case 'textPrimary':   return theme.palette.text.primary;
    case 'textSecondary': return theme.palette.text.secondary;
    case 'disabled':      return theme.palette.text.disabled;
    default:              return theme.palette.text.primary;
  }
};

const fgFrom = (theme: useTheme, c?: Color) => {
  switch (c) {
    case 'primary':   return theme.palette.getContrastText(theme.palette.primary.main);
    case 'secondary': return theme.palette.getContrastText(theme.palette.secondary.main);
    case 'success':   return theme.palette.getContrastText(theme.palette.success.main);
    case 'error':     return theme.palette.getContrastText(theme.palette.error.main);
    case 'warning':   return theme.palette.getContrastText(theme.palette.warning.main);
    case 'info':      return theme.palette.getContrastText(theme.palette.info.main);
    // “text*” backgrounds are already text colors; use a neutral readable FG
    case 'textPrimary':
    case 'textSecondary':
    case 'disabled':
    default:
      return theme.palette.background.paper;
  }
};

// keep your mapper as-is, just rely on normalizeColor
function mapApiDataToTreeItems(apiData: any): TreeViewBaseItem<ExtendedTreeItemProps>[] {
  return Object.entries(apiData).map(([key, stageObj]: [string, any]) => {
    const [, colorlab] = Object.entries(stageObj)[0] as [any, any];
    const [, stagename] = Object.entries(stageObj)[1] as [any, any];

    return {
      id: key,
      label: stagename,
      color: normalizeColor(colorlab), // "green"|"red"|"yellow" -> success|error|warning
    };
  });
}




function DotIcon({ color }: { color: string }) {
  return (
    <Box sx={{ marginRight: 1, display: 'flex', alignItems: 'center' }}>
      <svg width={6} height={6}>
        <circle cx={3} cy={3} r={3} fill={color} />
      </svg>
    </Box>
  );
}

const AnimatedCollapse = animated(Collapse);

function TransitionComponent(props: TransitionProps) {
  const style = useSpring({
    to: {
      opacity: props.in ? 1 : 0,
      transform: `translate3d(0,${props.in ? 0 : 20}px,0)`,
    },
  });

  return <AnimatedCollapse style={style} {...props} />;
}

interface CustomLabelProps {
  children: React.ReactNode;
  color?: Color;
  expandable?: boolean;
}

function CustomLabel({ color, expandable, children, ...other }: CustomLabelProps) {
  const theme = useTheme();

  const iconColor =
    color === 'primary'        ? theme.palette.primary.main :
    color === 'secondary'      ? theme.palette.secondary.main :
    color === 'success'        ? theme.palette.success.main :
    color === 'error'          ? theme.palette.error.main :
    color === 'warning'        ? theme.palette.warning.main :
    color === 'info'           ? theme.palette.info.main :
    color === 'textSecondary'  ? theme.palette.text.secondary :
    color === 'disabled'       ? theme.palette.text.disabled :
                                 theme.palette.text.primary;

  return (
    <TreeItemLabel {...other} sx={{ display: 'flex', alignItems: 'center' }}>
      <DotIcon color={iconColor} />
      <Typography variant="body2" sx={{ color: 'text.primary' }}>
        {children}
      </Typography>
    </TreeItemLabel>
  );
}

interface CustomTreeItemProps
  extends Omit<UseTreeItemParameters, 'rootRef'>,
    Omit<React.HTMLAttributes<HTMLLIElement>, 'onFocus'> {}

const CustomTreeItem = React.forwardRef(function CustomTreeItem(
  props: CustomTreeItemProps,
  ref: React.Ref<HTMLLIElement>,
) {
  const { id, itemId, label, disabled, children, ...other } = props;

  const {
    getRootProps,
    getContentProps,
    getIconContainerProps,
    getLabelProps,
    getGroupTransitionProps,
    status,
    publicAPI,
  } = useTreeItem({ id, itemId, children, label, disabled, rootRef: ref });

  const item = publicAPI.getItem(itemId);
  const color = item?.color;
  return (
    <TreeItemProvider id={id} itemId={itemId}>
      <TreeItemRoot {...getRootProps(other)}>
        <TreeItemContent
          {...getContentProps({
            className: clsx('content', {
              expanded: status.expanded,
              selected: status.selected,
              focused: status.focused,
              disabled: status.disabled,
            }),
          })}
        >
          {status.expandable && (
            <TreeItemIconContainer {...getIconContainerProps()}>
              <TreeItemIcon status={status} />
            </TreeItemIconContainer>
          )}

          <CustomLabel {...getLabelProps({ color })} />
        </TreeItemContent>
        {children && (
          <TransitionComponent
            {...getGroupTransitionProps({ className: 'groupTransition' })}
          />
        )}
      </TreeItemRoot>
    </TreeItemProvider>
  );
});



export default function ChevronProgress() {
const [treeItems, setTreeItems] = useState<TreeViewBaseItem<ExtendedTreeItemProps>[]>([]);
const [selectedCompany, setSelectedCompany] = useState(() => sessionStorage.getItem('selectedCompany'));
const [loading, setLoading] = useState<boolean>(false);

useEffect(() => {
  const handleCompanyUpdate = () => {
    setSelectedCompany(sessionStorage.getItem('selectedCompany'));
  };

  window.addEventListener('company-updated', handleCompanyUpdate);
  return () => window.removeEventListener('company-updated', handleCompanyUpdate);
}, []);

useEffect(() => {
  if (!selectedCompany) return;

  const fetchProgress = async () => {
    setLoading(true); // start loading
    try {
      const response = await fetch(`${API_BASE_URL}/getcurrentprogress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: selectedCompany }),
      });

      const data = await response.json();
      const items = mapApiDataToTreeItems(data.data.chevron);
      setTreeItems(items);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
      setTreeItems([]);
    } finally {
      setTimeout(() => setLoading(false), 300); // small delay for smooth UX
    }
  };

  fetchProgress();
}, [selectedCompany]);



  return (
<Card variant="outlined" sx={{ display: 'flex', flexDirection: 'column', width: '600px', flexGrow: 0 }}>
  <CardContent>
    <Typography component="h2" variant="subtitle2"></Typography>

    {loading ? (
      <Typography color="text.secondary">Reloading progress...</Typography>
    ) : treeItems.length === 0 ? (
      <Typography color="text.secondary">No progress available</Typography>
    ) : (
      <Box sx={{ display: 'flex', width: '100%', overflow: 'hidden' }}>
        {treeItems.map((item, index) => (
          <Box
            key={item.id}
            sx={{
              flex: '1 1 0',
              minWidth: 0,
              display: 'flex',
              zIndex: treeItems.length - index,
              marginRight: index !== treeItems.length - 1 ? '-10px' : 0,
            }}
          >

<Box
  title={item.label}
  sx={{
    width: '100%',
    minWidth: 0,
    px: 2.5,
    py: 1.75,
    borderRadius: 1.5,
    textAlign: 'center',
    clipPath:
      'polygon(0% 0%, calc(100% - 10px) 0%, 100% 50%, calc(100% - 10px) 100%, 0% 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 500,
    letterSpacing: 0.3,
    color: (t) => fgFrom(t, item.color),
    background: (t) =>
      `linear-gradient(160deg, ${bgFrom(t, item.color)} 0%, ${t.palette.grey[900]} 100%)`,
    boxShadow: (t) =>
      `inset 0 1px 1px rgba(255,255,255,0.1),
       inset 0 -1px 2px rgba(0,0,0,0.25),
       0 4px 10px ${t.palette.grey[900]}55`,
    position: 'relative',
    overflow: 'hidden',
    transition: 'all 0.35s ease',

    // subtle gloss layer
    '&::before': {
      content: '""',
      position: 'absolute',
      inset: 0,
      background:
        'linear-gradient(180deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 35%)',
      pointerEvents: 'none',
    },

    // faint border glow
    '&::after': {
      content: '""',
      position: 'absolute',
      inset: 0,
      borderRadius: 'inherit',
      border: '1px solid rgba(255,255,255,0.08)',
      boxShadow: '0 0 10px rgba(255,255,255,0.05)',
      pointerEvents: 'none',
    },

    '&:hover': {
      transform: 'translateY(-3px) scale(1.02)',
      background: (t) =>
        `linear-gradient(160deg, ${t.palette.primary.light} 0%, ${t.palette.primary.dark} 100%)`,
      boxShadow: (t) =>
        `inset 0 1px 1px rgba(255,255,255,0.2),
         0 6px 18px ${t.palette.primary.main}44`,
      '&::before': {
        background:
          'linear-gradient(160deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 60%)',
      },
    },
  }}
>
  {item.label}
</Box>

          </Box>
        ))}
      </Box>
    )}
  </CardContent>
</Card>
  );
}
