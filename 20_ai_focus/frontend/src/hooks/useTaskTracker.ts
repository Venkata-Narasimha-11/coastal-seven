import { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '../services/apiClient';

export interface TaskStatusResponse {
  task_id: string;
  state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}

export const useTaskTracker = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [state, setState] = useState<'IDLE' | 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'>('IDLE');
  const [progress, setProgress] = useState<number>(0);
  const [message, setMessage] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const pollTask = useCallback(async (id: string) => {
    try {
      const data = await apiClient.get<TaskStatusResponse>(`/tasks/${id}`);
      setState(data.state);
      setProgress(data.progress || 0);
      if (data.message) setMessage(data.message);

      if (data.state === 'SUCCESS') {
        setResult(data.result);
        stopPolling();
      } else if (data.state === 'FAILURE') {
        setError(data.error || 'Task failed during execution');
        stopPolling();
      }
    } catch (err: any) {
      setError(err?.message || 'Error checking task status');
      stopPolling();
    }
  }, [stopPolling]);

  const startTracking = useCallback((newTaskId: string) => {
    stopPolling();
    setTaskId(newTaskId);
    setState('PENDING');
    setProgress(5);
    setMessage('Queued in background...');
    setResult(null);
    setError(null);

    // Initial check
    pollTask(newTaskId);

    // Poll every 1 second
    pollIntervalRef.current = setInterval(() => {
      pollTask(newTaskId);
    }, 1000);
  }, [pollTask, stopPolling]);

  const reset = useCallback(() => {
    stopPolling();
    setTaskId(null);
    setState('IDLE');
    setProgress(0);
    setMessage('');
    setResult(null);
    setError(null);
  }, [stopPolling]);

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  return {
    taskId,
    state,
    progress,
    message,
    result,
    error,
    startTracking,
    reset,
    isProcessing: state === 'PENDING' || state === 'PROGRESS',
  };
};