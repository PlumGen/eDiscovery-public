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


type Color = 'blue' | 'green';

type ExtendedTreeItemProps = {
  color?: Color;
  id: string;
  label: string;
};



function mapApiDataToTreeItems(apiData: any): TreeViewBaseItem<ExtendedTreeItemProps>[] {
  return Object.entries(apiData).map(([key, stageObj]: [string, any]) => {

    const [color, colorlab] = Object.entries(stageObj)[0] as [any, any];
    const [finalstage, stagename] = Object.entries(stageObj)[1] as [any, any];


    return {
      id: key,
      label: stagename,
      color:colorlab
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
const colors = {
  blue: (theme.vars || theme).palette.primary.main,
  green: (theme.vars || theme).palette.success.main,
  red: (theme.vars || theme).palette.error.main,
  yellow: (theme.vars || theme).palette.warning.main,
  gray: (theme.vars || theme).palette.text.disabled,
  default: (theme.vars || theme).palette.text.primary,
};


const iconColor = color && colors[color] ? colors[color] : colors.default;

  return (
    <TreeItemLabel {...other} sx={{ display: 'flex', alignItems: 'center' }}>
      {iconColor && <DotIcon color={iconColor} />}
      <Typography
        className="labelText"
        variant="body2"
        sx={{ color: 'text.primary' }}
      >
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
        const items = mapApiDataToTreeItems([]);
        setTreeItems(items);
      }
    };

    fetchProgress();
  }, [selectedCompany]);



  return (
<Card
  variant="outlined"
  sx={{ display: 'flex', flexDirection: 'column', width: '600px', flexGrow: 0 }}
>
  <CardContent>
    <Typography component="h2" variant="subtitle2"></Typography>
    {treeItems.length === 0 ? (
      <Typography>Loading progress...</Typography>
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
    marginRight: index !== treeItems.length - 1 ? '-10px' : 0, // optional
  }}
>

      <Box
        title={item.label}
        sx={{
          width: '100%',
          minWidth: 0,
          px: 2,
          py: 1,
          bgcolor: item.color,
          color: 'black',
          textAlign: 'center',
          clipPath:
            'polygon(0% 0%, calc(100% - 10px) 0%, 100% 50%, calc(100% - 10px) 100%, 0% 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
<Typography
  sx={{
    width: '100%',
    fontSize: 'min(1.0vw, 0.85rem)',
    lineHeight: 1.1,
    textAlign: 'center',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'normal', // ❗ allows wrapping if needed
    display: 'block',
  }}
>
  {item.label}
</Typography>

      </Box>
    </Box>
  ))}
</Box>



    )}
  </CardContent>
</Card>
  );
}
