import axios, { type AxiosProgressEvent } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const uploadVideo = async (file: File, onUploadProgress?: (progressEvent: AxiosProgressEvent) => void) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE_URL}/api/video/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error uploading video:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to upload video');
    } else {
      console.error('Unexpected error uploading video:', error);
      throw new Error('An unexpected error occurred during upload');
    }
  }
};

export const sendMessage = async (videoFilename: string, message: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      query: message,
      video_filename: videoFilename,
    });
    return response.data; // Assuming backend returns { response: string }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Error sending message:', error.response?.data || error.message);
      console.error('Axios error details:', error.response);
      console.error('Axios error data:', error.response?.data);
      const errorDetail = error.response?.data?.detail 
                          ? (
                            Array.isArray(error.response.data.detail)
                            ? error.response.data.detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ')
                            : error.response.data.detail
                          )
                          : (typeof error.response?.data === 'object' 
                             ? JSON.stringify(error.response.data) 
                             : error.message || 'Failed to send message');
      console.error('Constructed error detail:', errorDetail);
      throw new Error(errorDetail);
    } else {
      console.error('Unexpected error sending message:', error);
      console.error('Non-Axios error details:', error);
      throw new Error('An unexpected error occurred while sending message');
    }
  }
}; 