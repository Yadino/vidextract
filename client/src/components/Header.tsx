import { AppBar, Toolbar, Typography, Container, Box, Link, IconButton } from '@mui/material';
import ReplayRoundedIcon from '@mui/icons-material/ReplayRounded';

interface HeaderProps {
  showResetButton: boolean;
}

const Header = ({ showResetButton }: HeaderProps) => {
  const handleReset = () => {
    window.location.reload(); // Simple page reload to reset
  };

  return (
    <AppBar position="sticky" color="default" elevation={1}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              mr: 2,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              flexGrow: 1, // Allow title area to take available space
            }}
          >
            {/* Logo Link */}
            <Link
              href="#"
              onClick={handleReset}
              color="inherit"
              underline="none"
              sx={{
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer',
              }}
            >
              <Box component="span" sx={{ fontStyle: 'italic', letterSpacing: '.3rem', mr: 1 }}>
                VidExtract
              </Box>
              <Box component="span" sx={{
                letterSpacing: '.25rem',
                fontSize: '0.6em',
                color: 'grey.700'
              }}>
                &nbsp;&nbsp;for Linnovate
              </Box>
            </Link>

            {/* Reset Button (conditionally rendered) */}
            {showResetButton && (
              <IconButton
                color="inherit"
                onClick={handleReset}
                size="small"
                sx={{
                  ml: 'auto', // Push to the right
                  bgcolor: 'rgba(0, 0, 0, 0.05)',
                  '&:hover': { bgcolor: 'rgba(0, 0, 0, 0.1)' },
                  borderRadius: '50%',
                  p: 0.5,
                }}
              >
                <ReplayRoundedIcon fontSize="small" />
              </IconButton>
            )}
          </Typography>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 