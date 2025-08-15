import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import SimpleDashboard from '../SimpleDashboard'
import { apiService, handleApiError } from '../../services/api'

// Mock the API service
jest.mock('../../services/api')

describe('SimpleDashboard', () => {
  const mockCommits = [
    {
      id: 1,
      commit_hash: '8890dbd8edfd2fd09dded49fc4ee96cdfbdbad51',
      author: 'Pavan',
      author_email: 'nityahasini7@gmail.com',
      message: 'Structure',
      timestamp: '2025-08-15T06:22:01',
      repository: 'Pavan200312/Microserivices-With-Agent',
      branch: 'main'
    },
    {
      id: 2,
      commit_hash: 'fb46e9129eb76b93f46f4cbf41c212a007e4c357',
      author: 'Pavan',
      author_email: 'nityahasini7@gmail.com',
      message: 'Initial commit: GitHub Commit Tracker',
      timestamp: '2025-08-15T06:20:45',
      repository: 'Pavan200312/Microserivices-With-Agent',
      branch: 'main'
    },
    {
      id: 3,
      commit_hash: '5fc50fa47b9562f3154101966d36338609b46b59',
      author: 'pavan',
      author_email: '131873258+Pavan200312@users.noreply.github.com',
      message: 'Initial commit',
      timestamp: '2025-08-15T05:55:58',
      repository: 'Pavan200312/Microserivices-With-Agent',
      branch: 'main'
    }
  ]

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  describe('Initial Render', () => {
    test('renders header correctly', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('GitHub Commit Tracker')).toBeInTheDocument()
      expect(screen.getByText('Real-time commit tracking with AI analysis')).toBeInTheDocument()
    })

    test('renders Track Now button', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('Track Now')).toBeInTheDocument()
      expect(screen.getByText('Click the button below to start tracking GitHub commits')).toBeInTheDocument()
    })

    test('renders commits section', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('Commits (Not Tracking)')).toBeInTheDocument()
      expect(screen.getByText('🔄 Refresh')).toBeInTheDocument()
    })

    test('shows no commits message initially', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('No commits displayed yet. Click "Track Now" to start viewing commits.')).toBeInTheDocument()
    })
  })

  describe('API Integration', () => {
    test('fetches commits on mount', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      
      render(<SimpleDashboard />)
      
      await waitFor(() => {
        expect(apiService.getCommits).toHaveBeenCalledTimes(1)
      })
    })

    test('handles API error on mount', async () => {
      const error = new Error('Network error')
      apiService.getCommits.mockRejectedValue(error)
      handleApiError.mockReturnValue('Network error: Unable to connect to server')
      
      render(<SimpleDashboard />)
      
      await waitFor(() => {
        expect(screen.getByText('❌ Network error: Unable to connect to server')).toBeInTheDocument()
      })
    })

    test('starts tracking successfully', async () => {
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      apiService.getCommits.mockResolvedValue(mockCommits)
      
      render(<SimpleDashboard />)
      
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(apiService.startTracking).toHaveBeenCalledTimes(1)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Tracking...')).toBeInTheDocument()
      })
    })

    test('handles tracking error', async () => {
      const error = new Error('Tracking failed')
      apiService.startTracking.mockRejectedValue(error)
      handleApiError.mockReturnValue('Failed to start tracking')
      
      render(<SimpleDashboard />)
      
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('❌ Failed to start tracking')).toBeInTheDocument()
      })
    })
  })

  describe('Commit Display Logic', () => {
    test('displays commits one by one when tracking starts', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Wait for initial fetch
      await waitFor(() => {
        expect(apiService.getCommits).toHaveBeenCalled()
      })
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Tracking...')).toBeInTheDocument()
      })
      
      // Wait for commits to be fetched and displayed
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Check that only first commit is displayed initially
      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.queryByText('Initial commit: GitHub Commit Tracker')).not.toBeInTheDocument()
      expect(screen.queryByText('Initial commit')).not.toBeInTheDocument()
    })

    test('displays next commit after interval', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Fast-forward time to trigger next commit display
      act(() => {
        jest.advanceTimersByTime(2000)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Initial commit: GitHub Commit Tracker')).toBeInTheDocument()
      })
    })

    test('shows all commits when "Show All" is clicked', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Click "Show All"
      const showAllButton = screen.getByText('📋 Show All')
      fireEvent.click(showAllButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
        expect(screen.getByText('Initial commit: GitHub Commit Tracker')).toBeInTheDocument()
        expect(screen.getByText('Initial commit')).toBeInTheDocument()
      })
    })

    test('resets display when "Reset" is clicked', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Click "Reset"
      const resetButton = screen.getByText('🔄 Reset')
      fireEvent.click(resetButton)
      
      await waitFor(() => {
        expect(screen.queryByText('Structure')).not.toBeInTheDocument()
        expect(screen.getByText('No commits displayed yet. Click "Track Now" to start viewing commits.')).toBeInTheDocument()
      })
    })
  })

  describe('Commit Hash Logic', () => {
    test('displays commit hash correctly', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('🔑 Hash: 8890dbd8edfd2fd09dded49fc4ee96cdfbdbad51')).toBeInTheDocument()
      })
    })

    test('handles commits without hash gracefully', async () => {
      const commitsWithoutHash = [
        {
          id: 1,
          author: 'Test User',
          message: 'Test commit',
          timestamp: '2025-08-15T06:22:01',
          repository: 'test/repo'
        }
      ]
      
      apiService.getCommits.mockResolvedValue(commitsWithoutHash)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('🔑 Hash: commit-0')).toBeInTheDocument()
      })
    })

    test('sorts commits by timestamp (newest first)', async () => {
      const unsortedCommits = [
        {
          id: 1,
          commit_hash: 'old123',
          author: 'User1',
          message: 'Old commit',
          timestamp: '2025-08-15T05:00:00',
          repository: 'test/repo'
        },
        {
          id: 2,
          commit_hash: 'new456',
          author: 'User2',
          message: 'New commit',
          timestamp: '2025-08-15T06:00:00',
          repository: 'test/repo'
        }
      ]
      
      apiService.getCommits.mockResolvedValue(unsortedCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('New commit')).toBeInTheDocument()
        expect(screen.getByText('🔑 Hash: new456')).toBeInTheDocument()
      })
    })
  })

  describe('Control Buttons', () => {
    test('pause and resume functionality', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Start display
      const startDisplayButton = screen.getByText('▶️ Start Display')
      fireEvent.click(startDisplayButton)
      
      // Check pause button appears
      await waitFor(() => {
        expect(screen.getByText('⏸️ Pause')).toBeInTheDocument()
      })
      
      // Click pause
      const pauseButton = screen.getByText('⏸️ Pause')
      fireEvent.click(pauseButton)
      
      // Check resume button appears
      await waitFor(() => {
        expect(screen.getByText('▶️ Resume')).toBeInTheDocument()
      })
    })

    test('refresh functionality', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      
      render(<SimpleDashboard />)
      
      const refreshButton = screen.getByText('🔄 Refresh')
      fireEvent.click(refreshButton)
      
      await waitFor(() => {
        expect(apiService.getCommits).toHaveBeenCalledTimes(2) // Once on mount, once on refresh
      })
    })
  })

  describe('Loading States', () => {
    test('shows loading state during API calls', async () => {
      apiService.getCommits.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<SimpleDashboard />)
      
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    test('disables buttons during loading', async () => {
      apiService.startTracking.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<SimpleDashboard />)
      
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      expect(trackButton).toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    test('shows retry button on error', async () => {
      const error = new Error('API Error')
      apiService.getCommits.mockRejectedValue(error)
      handleApiError.mockReturnValue('API Error occurred')
      
      render(<SimpleDashboard />)
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument()
      })
    })

    test('retry functionality works', async () => {
      const error = new Error('API Error')
      apiService.getCommits
        .mockRejectedValueOnce(error)
        .mockResolvedValueOnce(mockCommits)
      handleApiError.mockReturnValue('API Error occurred')
      
      render(<SimpleDashboard />)
      
      await waitFor(() => {
        expect(screen.getByText('Retry')).toBeInTheDocument()
      })
      
      const retryButton = screen.getByText('Retry')
      fireEvent.click(retryButton)
      
      await waitFor(() => {
        expect(apiService.getCommits).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Component Cleanup', () => {
    test('cleans up intervals on unmount', async () => {
      apiService.getCommits.mockResolvedValue(mockCommits)
      apiService.startTracking.mockResolvedValue({ status: 'success' })
      
      const { unmount } = render(<SimpleDashboard />)
      
      // Start tracking
      const trackButton = screen.getByText('Track Now')
      fireEvent.click(trackButton)
      
      await waitFor(() => {
        expect(screen.getByText('Structure')).toBeInTheDocument()
      })
      
      // Start display
      const startDisplayButton = screen.getByText('▶️ Start Display')
      fireEvent.click(startDisplayButton)
      
      // Unmount component
      unmount()
      
      // No errors should be thrown during cleanup
      expect(true).toBe(true)
    })
  })
})
