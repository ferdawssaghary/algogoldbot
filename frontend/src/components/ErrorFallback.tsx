import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { ErrorOutline } from '@mui/icons-material';

interface ErrorFallbackProps {
  error: Error;
  resetErrorBoundary: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetErrorBoundary }) => {
  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        textAlign="center"
        gap={3}
      >
        <ErrorOutline color="error" sx={{ fontSize: 64 }} />
        
        <Typography variant="h4" component="h1" color="error">
          Something went wrong
        </Typography>
        
        <Typography variant="body1" color="textSecondary">
          {error.message || 'An unexpected error occurred'}
        </Typography>
        
        <Button
          variant="contained"
          onClick={resetErrorBoundary}
          size="large"
        >
          Try Again
        </Button>
        
        {process.env.NODE_ENV === 'development' && (
          <Box mt={2} p={2} bgcolor="grey.100" borderRadius={1} maxWidth="100%">
            <Typography variant="caption" component="pre" style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
              {error.stack}
            </Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default ErrorFallback;