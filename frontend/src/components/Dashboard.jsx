import React, { useState, useEffect } from 'react'
import './Dashboard.css'
import TrackNowButton from './TrackNowButton'
import CommitList from './CommitList'

function Dashboard() {
  const [isTracking, setIsTracking] = useState(false)
  const [commits, setCommits] = useState([])
  const [loading, setLoading] = useState(false)

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-content">
          <TrackNowButton 
            isTracking={isTracking} 
            setIsTracking={setIsTracking}
            setLoading={setLoading}
          />
          <CommitList 
            commits={commits} 
            loading={loading}
            isTracking={isTracking}
          />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
