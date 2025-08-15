import React, { useState, useEffect } from 'react'
import './Dashboard.css'
import TrackNowButton from './TrackNowButton'
import CommitList from './CommitList'
import { apiService, handleApiError } from '../services/api'

function Dashboard() {
  const [isTracking, setIsTracking] = useState(false)
  const [commits, setCommits] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch commits when component mounts or when tracking starts
  const fetchCommits = async () => {
    try {
      console.log('🔍 Fetching commits...')
      console.log('🔧 API URL being used:', import.meta.env.VITE_API_URL || 'http://localhost:8000')
      setLoading(true)
      setError(null)
      
      const commitsData = await apiService.getCommits()
      console.log('✅ Commits fetched:', commitsData)
      console.log('📊 Number of commits:', commitsData.length)
      setCommits(commitsData)
      
    } catch (error) {
      console.error('❌ Failed to fetch commits:', error)
      console.error('❌ Error details:', error.response?.data || error.message)
      const errorMessage = handleApiError(error)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Fetch commits on component mount
  useEffect(() => {
    console.log('🚀 Dashboard mounted, fetching commits...')
    console.log('🔧 Current API URL:', import.meta.env.VITE_API_URL || 'http://localhost:8000')
    fetchCommits()
  }, [])

  // Auto-refresh commits every 30 seconds when tracking
  useEffect(() => {
    let interval
    if (isTracking) {
      interval = setInterval(fetchCommits, 30000) // 30 seconds
    }
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [isTracking])

  // Handle tracking state change
  const handleTrackingChange = (tracking) => {
    console.log('🔄 Tracking state changed:', tracking)
    setIsTracking(tracking)
    if (tracking) {
      // Fetch commits immediately when tracking starts
      fetchCommits()
    }
  }

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-content">
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#f0f0f0', 
            border: '2px solid #333',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <h3>Dashboard Status</h3>
            <p>Loading: {loading ? 'Yes' : 'No'}</p>
            <p>Tracking: {isTracking ? 'Yes' : 'No'}</p>
            <p>Commits: {commits.length}</p>
            <p>Error: {error || 'None'}</p>
          </div>
          
          <TrackNowButton 
            isTracking={isTracking} 
            setIsTracking={handleTrackingChange}
            setLoading={setLoading}
          />
          <CommitList 
            commits={commits} 
            loading={loading}
            isTracking={isTracking}
            error={error}
            onRefresh={fetchCommits}
          />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
