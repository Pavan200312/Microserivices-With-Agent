import React from 'react'
import './TrackNowButton.css'
import { apiService, handleApiError } from '../services/api'

function TrackNowButton({ isTracking, setIsTracking, setLoading }) {
  console.log('🔘 TrackNowButton rendered with props:', { isTracking, setIsTracking: !!setIsTracking, setLoading: !!setLoading })
  
  const handleTrackNow = async () => {
    try {
      setLoading(true)
      
      // Call the API to start tracking
      const result = await apiService.startTracking()
      
      console.log('Tracking started:', result)
      setIsTracking(true)
      
    } catch (error) {
      console.error('Failed to start tracking:', error)
      const errorMessage = handleApiError(error)
      alert(`Failed to start tracking: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-section">
      <h2>Start Tracking</h2>
      <p>Click the button below to start tracking GitHub commits</p>
      <button 
        className={`track-button ${isTracking ? 'tracking' : ''}`}
        onClick={handleTrackNow}
        disabled={isTracking}
      >
        {isTracking ? 'Tracking...' : 'Track Now'}
      </button>
    </div>
  )
}

export default TrackNowButton
