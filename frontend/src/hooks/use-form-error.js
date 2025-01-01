import { useState } from 'react';

export function useFormError() {
  const [serverError, setServerError] = useState('');

  const handleError = (error, form) => {
    setServerError('');
    if (error.message.includes('detail')) {
      try {
        const errorData = JSON.parse(error.message);
        if (Array.isArray(errorData.detail)) {
          // Handle validation errors from backend
          errorData.detail.forEach((err) => {
            if (err.loc[1]) {
              form.setError(err.loc[1], {
                type: 'server',
                message: err.msg,
              });
            } else {
              setServerError(err.msg);
            }
          });
        } else {
          setServerError(errorData.detail);
        }
      } catch {
        setServerError(error.message);
      }
    } else {
      setServerError(error.message);
    }
  };

  return {
    serverError,
    setServerError,
    handleError,
  };
} 