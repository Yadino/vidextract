import { ThemeProvider, createTheme, Container, Typography, Stack, Box, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import VideoUpload from './components/VideoUpload';
import Header from './components/Header';
import { useState } from 'react';
import Chat from './components/Chat';
import { AnimatePresence, motion } from 'framer-motion';

const theme = createTheme({
  palette: {
    background: {
      default: '#fff',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          height: '100%',
        },
        body: {
          height: '100%',
          backgroundColor: '#fff',
          margin: 0,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        },
        '#root': {
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          display: 'flex',
          flexDirection: 'column',
          flexGrow: 1,
          padding: 0,
        },
      },
    },
  },
});

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [videoFilename, setVideoFilename] = useState<string | null>(null);

  const handleAnalysisComplete = (filename: string) => {
    console.log('Analysis complete for:', filename);
    setVideoFilename(filename);
    console.log('videoFilename state set to:', filename);
    setCurrentView('chat');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
            flexGrow: 1,
          }}
        >
          <Header showResetButton={currentView === 'upload' || currentView === 'chat'} />
          <Container
            maxWidth="lg"
            sx={{
              flexGrow: 1,
              height: 0,
              paddingTop: 2.5,
              paddingBottom: 0,
              display: 'flex',
              flexDirection: 'column',
              width: '100%',
              position: 'relative',
            }}
          >
            <AnimatePresence mode="wait">
              {currentView === 'upload' && (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  style={{ 
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                  }}
                >
                  <Stack 
                    spacing={4} 
                    sx={{ 
                      width: '100%', 
                      maxWidth: 600,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="h4" component="h1" gutterBottom sx={{ textAlign: 'center', mt: 3 }}>
                      Video Analysis
                    </Typography>
                    <VideoUpload onAnalysisComplete={handleAnalysisComplete} />
                  </Stack>
                </motion.div>
              )}

              {currentView === 'chat' && videoFilename && (
                <motion.div
                  key="chat"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  style={{ 
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    height: 0,
                    flexGrow: 1,
                  }}
                >
                  <Chat videoFilename={videoFilename} />
                </motion.div>
              )}
            </AnimatePresence>
          </Container>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
