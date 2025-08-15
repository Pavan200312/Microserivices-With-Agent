import React from 'react'
import './TrackNowButton.css'

function TrackNowButton({ isTracking, setIsTracking, setLoading }) {
  const handleTrackNow = async () => {
    setLoading(true)
    // API call will be implemented here
    setIsTracking(true)
    setLoading(false)
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
