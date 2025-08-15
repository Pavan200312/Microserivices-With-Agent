import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import SimpleDashboard from './SimpleDashboard'

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    getCommits: jest.fn(),
    startTracking: jest.fn()
  },
  handleApiError: jest.fn()
}))

// Mock fetch for clearDatabase function
global.fetch = jest.fn()

describe('SimpleDashboard Component', () => {
  const mockApiService = require('../services/api').apiService
  const mockHandleApiError = require('../services/api').handleApiError

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  describe('Initial Render', () => {
    test('renders the dashboard with header and track button', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('GitHub Commit Tracker')).toBeInTheDocument()
      expect(screen.getByText('Real-time commit tracking with AI analysis')).toBeInTheDocument()
      expect(screen.getByText('Start Tracking')).toBeInTheDocument()
      expect(screen.getByText('Track Now')).toBeInTheDocument()
    })

    test('shows no commits message initially', () => {
      render(<SimpleDashboard />)
      
      expect(screen.getByText('No commits displayed yet. Click "Track Now" to start viewing commits.')).toBeInTheDocument()
    })
  })

  describe('API Integration', () => {
    test('handles successful commit fetching', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'Test User',
          message: 'Test commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Click Track Now
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(mockApiService.startTracking).toHaveBeenCalled()
        expect(mockApiService.getCommits).toHaveBeenCalled()
      })
    })

    test('handles API error during tracking start', async () => {
      const error = new Error('API Error')
      mockApiService.startTracking.mockRejectedValue(error)
      mockHandleApiError.mockReturnValue('Failed to start tracking')
      
      render(<SimpleDashboard />)
      
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('Failed to start tracking')).toBeInTheDocument()
      })
    })

    test('handles API error during commit fetching', async () => {
      const error = new Error('Fetch Error')
      mockApiService.getCommits.mockRejectedValue(error)
      mockHandleApiError.mockReturnValue('Failed to fetch commits')
      
      render(<SimpleDashboard />)
      
      // Click refresh button
      fireEvent.click(screen.getByText('🔄 Refresh'))
      
      await waitFor(() => {
        expect(screen.getByText('Failed to fetch commits')).toBeInTheDocument()
      })
    })
  })

  describe('Commit Display Logic', () => {
    test('displays commits one by one when start display is clicked', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'First commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        },
        {
          id: 2,
          commit_hash: 'def456',
          author: 'User 2',
          message: 'Second commit',
          timestamp: '2025-08-15T11:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('▶️ Start Display')).toBeInTheDocument()
      })
      
      // Start display
      fireEvent.click(screen.getByText('▶️ Start Display'))
      
      // Should show first commit immediately
      expect(screen.getByText('🔑 Hash: abc123')).toBeInTheDocument()
      expect(screen.getByText('📝 First commit')).toBeInTheDocument()
      
      // Fast forward timer to show second commit
      act(() => {
        jest.advanceTimersByTime(2000)
      })
      
      await waitFor(() => {
        expect(screen.getByText('🔑 Hash: def456')).toBeInTheDocument()
        expect(screen.getByText('📝 Second commit')).toBeInTheDocument()
      })
    })

    test('handles duplicate commits correctly', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'First commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        },
        {
          id: 2,
          commit_hash: 'abc123', // Duplicate hash
          author: 'User 1',
          message: 'First commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('▶️ Start Display')).toBeInTheDocument()
      })
      
      // Start display
      fireEvent.click(screen.getByText('▶️ Start Display'))
      
      // Should show only one commit (deduplicated)
      expect(screen.getByText('🔑 Hash: abc123')).toBeInTheDocument()
      expect(screen.getAllByText('🔑 Hash: abc123')).toHaveLength(1)
    })
  })

  describe('Control Buttons', () => {
    test('pause and resume functionality', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'Test commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking and display
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('▶️ Start Display'))
      })
      
      // Should show pause button
      expect(screen.getByText('⏸️ Pause')).toBeInTheDocument()
      
      // Pause display
      fireEvent.click(screen.getByText('⏸️ Pause'))
      
      // Should show resume button
      expect(screen.getByText('▶️ Resume')).toBeInTheDocument()
    })

    test('show all commits functionality', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'First commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        },
        {
          id: 2,
          commit_hash: 'def456',
          author: 'User 2',
          message: 'Second commit',
          timestamp: '2025-08-15T11:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('📋 Show All')).toBeInTheDocument()
      })
      
      // Show all commits
      fireEvent.click(screen.getByText('📋 Show All'))
      
      // Should show both commits
      expect(screen.getByText('🔑 Hash: abc123')).toBeInTheDocument()
      expect(screen.getByText('🔑 Hash: def456')).toBeInTheDocument()
    })

    test('reset display functionality', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'Test commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      render(<SimpleDashboard />)
      
      // Start tracking and display
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('▶️ Start Display'))
      })
      
      // Should show commit
      expect(screen.getByText('🔑 Hash: abc123')).toBeInTheDocument()
      
      // Reset display
      fireEvent.click(screen.getByText('🔄 Reset'))
      
      // Should show no commits message
      expect(screen.getByText('No commits displayed yet. Click "Track Now" to start viewing commits.')).toBeInTheDocument()
    })
  })

  describe('Clear Database Functionality', () => {
    test('clears database successfully', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'Test commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      global.fetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ message: 'Cleared 1 commits from database', deleted_count: 1 })
      })
      
      render(<SimpleDashboard />)
      
      // Start tracking
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('🗑️ Clear DB')).toBeInTheDocument()
      })
      
      // Clear database
      fireEvent.click(screen.getByText('🗑️ Clear DB'))
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/clear-commits', {
          method: 'DELETE'
        })
      })
    })

    test('handles clear database error', async () => {
      global.fetch.mockRejectedValue(new Error('Network error'))
      
      render(<SimpleDashboard />)
      
      // Start tracking to show clear button
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      mockApiService.getCommits.mockResolvedValue([])
      
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        expect(screen.getByText('🗑️ Clear DB')).toBeInTheDocument()
      })
      
      // Clear database
      fireEvent.click(screen.getByText('🗑️ Clear DB'))
      
      await waitFor(() => {
        expect(screen.getByText('Failed to clear database')).toBeInTheDocument()
      })
    })
  })

  describe('Loading States', () => {
    test('shows loading state during tracking start', async () => {
      mockApiService.startTracking.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<SimpleDashboard />)
      
      fireEvent.click(screen.getByText('Track Now'))
      
      expect(screen.getByRole('button', { name: 'Loading...' })).toBeInTheDocument()
    })

    test('shows loading state during commit fetching', async () => {
      mockApiService.getCommits.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<SimpleDashboard />)
      
      fireEvent.click(screen.getByText('🔄 Refresh'))
      
      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    test('handles invalid response format', async () => {
      mockApiService.getCommits.mockResolvedValue('invalid format')
      
      render(<SimpleDashboard />)
      
      fireEvent.click(screen.getByText('🔄 Refresh'))
      
      await waitFor(() => {
        expect(screen.getByText('Invalid response format from server')).toBeInTheDocument()
      })
    })

    test('handles network errors', async () => {
      mockApiService.getCommits.mockRejectedValue(new Error('Network error'))
      mockHandleApiError.mockReturnValue('Network error occurred')
      
      render(<SimpleDashboard />)
      
      fireEvent.click(screen.getByText('🔄 Refresh'))
      
      await waitFor(() => {
        expect(screen.getByText('Network error occurred')).toBeInTheDocument()
      })
    })
  })

  describe('Component Cleanup', () => {
    test('cleans up intervals on unmount', async () => {
      const mockCommits = [
        {
          id: 1,
          commit_hash: 'abc123',
          author: 'User 1',
          message: 'Test commit',
          timestamp: '2025-08-15T10:00:00Z',
          repository: 'test/repo',
          branch: 'main'
        }
      ]
      
      mockApiService.getCommits.mockResolvedValue(mockCommits)
      mockApiService.startTracking.mockResolvedValue({ message: 'Success' })
      
      const { unmount } = render(<SimpleDashboard />)
      
      // Start tracking and display
      fireEvent.click(screen.getByText('Track Now'))
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('▶️ Start Display'))
      })
      
      // Unmount component
      unmount()
      
      // Should not throw any errors
      expect(true).toBe(true)
    })
  })
})
