import React from 'react';
import { Box, Typography, Container, TextField } from '@mui/material';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { sendMessage } from '../services/api';
import { useSnackbar } from 'notistack';
import { styled } from '@mui/material/styles';

interface Message {
  role: 'user' | 'assistant';
  content: string; // The text content of the message (e.g., intro phrase)
  events?: any[]; // Optional array of event data received from the backend
}

interface ChatProps {
  videoFilename: string;
}

const Chat = ({ videoFilename }: ChatProps) => {
  const { enqueueSnackbar } = useSnackbar();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I have analyzed your video. Please write a request or any keyword to retrieve relevant highlighted moments. To see all highlights, write "All".' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputMessage(event.target.value);
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;
    if (isLoading) return;

    const newMessage: Message = { role: 'user', content: inputMessage };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    
    const messageToSend = inputMessage.trim().toLowerCase() === 'all' ? '__GET_ALL_EVENTS__' : inputMessage;
    const originalInput = inputMessage.trim().toLowerCase(); // Store original input
    setInputMessage('');
    
    setIsLoading(true);

    try {
      console.log('Preparing to send message. Filename:', videoFilename, 'Message:', messageToSend);
      const response = await sendMessage(videoFilename, messageToSend);
      console.log('Received response:', response);
      
      if (response && response.events) {
        console.log('Raw events received:', response.events);
        // Format the event descriptions into a single message
        const eventDescriptions = response.events.map((event: any) => {
          // Format timestamp from seconds to mm:ss.ms
          const formatTime = (seconds: number) => {
            try {
              // Calculate minutes and seconds from total seconds
              const minutes = Math.floor(seconds / 60);
              const remainingSeconds = Math.floor(seconds % 60);
              // const milliseconds = Math.round((seconds % 1) * 1000); // Optional milliseconds

              return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;//.${milliseconds.toString().padStart(3, '0')}`;
            } catch (e) {
              console.error('Error formatting timestamp:', seconds, e);
              return 'Invalid Time';
            }
          };

          // Format similarity score to 2 decimal places
          const similarityScore = event.similarity ? (event.similarity * 100).toFixed(2) : 'N/A';

          return `[${formatTime(event.timestamp)}] ${event.description || 'No description'} (Proximity: ${similarityScore}%)`;
        }).join('\n\n'); // Join multiple event descriptions with double newline

        let introPhrase = 'Here are some relevant moments:';
        if (originalInput === 'all') {
            introPhrase = 'These are all the moments extracted from the video:';
        } else if (response.events.length === 0) {
            introPhrase = `Sorry, I couldn't find any relevant moments for that query.`;
        }

        const finalAssistantMessage = response.events.length > 0
          ? `${introPhrase}\n\n${eventDescriptions}`
          : introPhrase;

        setMessages((prevMessages) => [
          ...prevMessages,
          { role: 'assistant', content: introPhrase, events: response.events },
        ]);
      } else {
        console.error('Invalid response format:', response);
        enqueueSnackbar('Received an unexpected response from the server.', { variant: 'error' });
      }
    } catch (error: any) {
      console.error('Caught error in Chat.tsx handleSendMessage:', error);
      enqueueSnackbar(error.message || 'Failed to send message.', { variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Container maxWidth="md" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Outer motion.div for the entire chat view */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%' }}
      >
        {/* Main Chat Container - This Box manages the vertical space distribution */}
        <Box
          sx={{
            flexGrow: 1, // Allows this box to take up available vertical space
            display: 'flex',
            flexDirection: 'column', // Stack title, message area, and input
            p: 2,
            border: '1px dashed grey',
            borderRadius: 2,
            bgcolor: 'background.paper',
            boxShadow: 1,
            mt: 2, // Margin top
            mx: 2, // Margin left and right
            mb: 2, // Margin bottom
            overflow: 'hidden', // Prevent internal content from causing overflow
            boxSizing: 'border-box', // Include padding and border in the element's total width and height
          }}
        >
          {/* Title and Video Filename */}
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom 
              sx={{ 
                fontWeight: 700,
                letterSpacing: '0.05em',
                color: 'success.dark',
                textTransform: 'uppercase',
                mb: 1,
                mt: 4
              }}
            >
              CHAT ABOUT THE VIDEO
            </Typography>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                color: 'text.secondary',
                mb: 0, // Adjusted margin bottom
                fontStyle: 'italic'
              }}
            >
              Video title: {videoFilename}
            </Typography>
          </Box>

          {/* Message Display Area - This Box will handle scrolling */}
          <Box 
            sx={{ 
              height: '0', // Crucial: base height for flex item that scrolls
              flexGrow: 1, // Crucial: allows message area to take available space
              overflowY: 'auto', // Enables vertical scrolling for messages
              pr: 1, // Add some padding to the right for the scrollbar
              pb: 2, // Add padding at the bottom of messages
              // Custom Scrollbar Styles
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                backgroundColor: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                backgroundColor: 'rgba(0, 0, 0, 0.2)', // Subtle grey/black
                borderRadius: '4px',
              },
              '&::-webkit-scrollbar-thumb:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.3)', // Darker on hover
              },
            }}
          >
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1.5,
                  wordBreak: 'break-word',
                }}
              >
                <Box
                  sx={{
                    bgcolor: msg.role === 'user' ? 'primary.light' : 'grey.300',
                    color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                    borderRadius: 2,
                    p: 1.5,
                    maxWidth: '80%',
                    textAlign: msg.role === 'user' ? 'right' : 'left',
                  }}
                >
                  {msg.role === 'assistant' && msg.events && msg.events.length > 0 ? (
                    <>
                      <Typography variant="body2" fontWeight="bold" mb={1}>{msg.content}</Typography>
                      {
                        msg.events.map((event: any, eventIndex) => {
                          // Format timestamp from seconds to mm:ss
                          const formatTime = (seconds: number) => {
                            try {
                              const minutes = Math.floor(seconds / 60);
                              const remainingSeconds = Math.floor(seconds % 60);
                              return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
                            } catch (e) {
                              console.error('Error formatting timestamp for event:', event, e);
                              return 'Invalid Time';
                            }
                          };

                          // Format similarity score to 2 decimal places (optional)
                          const similarityScore = event.similarity ? (event.similarity * 100).toFixed(2) : null;

                          return (
                            <Box key={eventIndex} sx={{ bgcolor: 'background.paper', p: 1, borderRadius: 1, mt: eventIndex > 0 ? 1 : 0, border: '1px solid grey.400' }}>
                              <Typography variant="body2" color="text.secondary">
                                {`[${formatTime(event.timestamp)}] ${event.description || 'No description'}`}
                                {similarityScore !== null && ` (Proximity: ${similarityScore}%)`}
                              </Typography>
                            </Box>
                          );
                        })
                      }
                    </>
                  ) : (
                    <Typography variant="body1">{msg.content}</Typography>
                  )}
                </Box>
              </Box>
            ))}
          </Box>
        
          {/* User Input Area */}
          <Box sx={{ mt: 2, width: '100%' }}> {/* Margin top for spacing, full width */}
            <TextField
              fullWidth
              variant="outlined"
              value={inputMessage}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              disabled={isLoading} // Disable input while loading
              placeholder="Ask a question about the video or write a keyword to retrieve relevant highlights."
            />
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default Chat; 