import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Paper,
  Typography,
  Stack,
  CircularProgress,
  Box
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useSnackbar } from 'notistack';
import { uploadVideo } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';

type ProcessingStage = 'idle' | 'uploading' | 'analyzing' | 'saving' | 'complete' | 'error';

interface VideoUploadProps {
  onAnalysisComplete: (filename: string) => void;
}

const VideoUpload = ({ onAnalysisComplete }: VideoUploadProps) => {
  const { enqueueSnackbar } = useSnackbar();
  const [processingStage, setProcessingStage] = useState<ProcessingStage>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showSuccessCheck, setShowSuccessCheck] = useState(false);

  useEffect(() => {
    if (processingStage === 'complete') {
      setShowSuccessCheck(true);
      const checkmarkTimer = setTimeout(() => {
        console.log('Checkmark shown, triggering analysis complete');
        setShowSuccessCheck(false);
      }, 2000);
      
      return () => clearTimeout(checkmarkTimer);
    } else if (processingStage === 'idle') {
      setShowSuccessCheck(false);
    }
  }, [processingStage]);

  const [completedFilename, setCompletedFilename] = useState<string | null>(null);

  useEffect(() => {
    if (showSuccessCheck === false && processingStage === 'complete' && completedFilename) {
      console.log('showSuccessCheck is false after complete, calling onAnalysisComplete');
      const transitionTimer = setTimeout(() => {
        onAnalysisComplete(completedFilename);
        setProcessingStage('idle'); 
        setCompletedFilename(null);
      }, 200);
      return () => clearTimeout(transitionTimer);
    }
  }, [showSuccessCheck, processingStage, completedFilename, onAnalysisComplete]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    console.log('onDrop called', acceptedFiles);
    const file = acceptedFiles[0];
    if (!file) {
      console.log('No file accepted');
      return;
    }

    console.log('File accepted:', file);
    setProcessingStage('idle');
    setShowSuccessCheck(false);
    setUploadProgress(0);
    setUploadError(null);
    setCompletedFilename(null);

    if (!file.type.startsWith('video/')) {
      console.log('Invalid file type');
      enqueueSnackbar('Please upload a video file', { variant: 'error' });
      return;
    }

    console.log('File is a video, starting upload');
    setProcessingStage('uploading');
    setUploadProgress(0);
    console.log('Processing stage set to uploading');

    try {
      const result = await uploadVideo(file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || file.size));
        setUploadProgress(progress);
        console.log(`Upload progress: ${progress}%`);
        if (progress === 100) {
          setProcessingStage('analyzing');
          console.log('Network upload complete, transitioning to analyzing');
        }
      });

      console.log('Backend processing successful:', result);
      if (result && result.filename) {
         setCompletedFilename(result.filename);
         console.log('Set completed filename', result.filename);
      } else {
        console.error('Upload result did not contain filename', result);
        setUploadError('Analysis complete, but filename not received.');
        setProcessingStage('error');
        enqueueSnackbar('Video analysis complete, but missing filename!', { variant: 'error' });
        return;
      }
      
      setProcessingStage('complete');
      enqueueSnackbar('Video analysis complete!', { variant: 'success' });

    } catch (error: any) {
      console.error('Upload or analysis failed:', error);
      setProcessingStage('error');
      setUploadError(error.message || 'An error occurred during processing');
      enqueueSnackbar(error.message || 'Failed to process video', { variant: 'error' });
    }

  }, [enqueueSnackbar, onAnalysisComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi']
    },
    maxFiles: 1,
    disabled: processingStage !== 'idle',
  });

  let content;
  let cursor;
  let bgColor;
  let paperBorderColor;

  if (showSuccessCheck) {
     content = (
       <motion.div
         key="success-check"
         initial={{ opacity: 0, scale: 0.5 }}
         animate={{ opacity: 1, scale: 1 }}
         exit={{ opacity: 0, scale: 0.5 }}
         transition={{ duration: 0.5 }}
         style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 150 }}
       >
         <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main' }} />
         <Typography mt={2} variant="h6" color="text.primary">Success!</Typography>
       </motion.div>
     );
     cursor = 'not-allowed';
     bgColor = 'rgba(76, 175, 80, 0.1)'; // Light green
     paperBorderColor = 'success.main';
  } else {
    if (processingStage === 'uploading') {
      content = (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 150 }}>
          <CircularProgress size={40} variant='determinate' value={uploadProgress} />
          <Typography mt={2}>Uploading: {uploadProgress}%</Typography>
        </Box>
      );
      cursor = 'progress';
      bgColor = 'rgba(255, 193, 7, 0.1)'; // Light yellow
      paperBorderColor = isDragActive ? 'primary.main' : 'grey.400';
    } else if (processingStage === 'analyzing') {
      content = (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 150 }}>
          <CircularProgress size={40} variant='indeterminate' />
          <Typography mt={2}>Analyzing Video...</Typography>
        </Box>
      );
      cursor = 'progress';
      bgColor = 'rgba(255, 193, 7, 0.1)'; // Light yellow
      paperBorderColor = isDragActive ? 'primary.main' : 'grey.400';
    } else if (processingStage === 'saving') {
      content = (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 150 }}>
          <CircularProgress size={40} variant='indeterminate' />
          <Typography mt={2}>Saving Events...</Typography>
        </Box>
      );
      cursor = 'progress';
      bgColor = 'rgba(76, 175, 80, 0.1)'; // Light green
      paperBorderColor = isDragActive ? 'primary.main' : 'grey.400';
    } else if (processingStage === 'error') {
      content = (
        <Stack spacing={2} alignItems="center">
          <Typography color="error.main">Error: {uploadError}</Typography>
          <CloudUploadIcon sx={{ fontSize: 40, color: 'grey.500' }} />
          <Typography variant="h6" color="text.secondary">
            Drag and drop a video file here, or click to select
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: MP4, MOV, AVI
          </Typography>
        </Stack>
      );
      cursor = 'pointer';
      bgColor = 'rgba(244, 67, 54, 0.1)'; // Light red
      paperBorderColor = 'error.main';
    } else {
      content = (
        <Stack spacing={2} alignItems="center">
          <CloudUploadIcon sx={{ fontSize: 40, color: 'grey.500' }} />
          <Typography variant="h6" color="text.secondary">
            {isDragActive
              ? 'Drop the video here'
              : 'Drag and drop a video file here, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supported formats: MP4, MOV, AVI
          </Typography>
        </Stack>
      );
      cursor = 'pointer';
      bgColor = 'background.paper';
      paperBorderColor = isDragActive ? 'primary.main' : 'grey.400';
    }
  }

  return (
    <Paper
      {...getRootProps()}
      elevation={processingStage === 'idle' ? 1 : 3}
      sx={{
        p: 5,
        border: '2px dashed',
        borderColor: paperBorderColor,
        borderRadius: 'borderRadius',
        bgcolor: bgColor,
        cursor: cursor,
        transition: 'all 0.2s',
        '&:hover': {
          ...(processingStage === 'idle' && {
            borderColor: 'primary.main',
            bgcolor: 'primary.light',
          }),
        },
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <input {...getInputProps()} />

      <AnimatePresence mode="wait">
        {content}
      </AnimatePresence>
    </Paper>
  );
};

export default VideoUpload; 