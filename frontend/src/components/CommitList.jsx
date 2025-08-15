import React from 'react'
import './CommitList.css'

function CommitList({ commits, loading, isTracking }) {
  if (loading) {
    return (
      <div className="dashboard-section">
        <h2>Loading...</h2>
      </div>
    )
  }

  if (!isTracking) {
    return (
      <div className="dashboard-section">
        <h2>Commits</h2>
        <p>Start tracking to see commits here</p>
      </div>
    )
  }

  return (
    <div className="dashboard-section">
      <h2>Recent Commits</h2>
      {commits.length === 0 ? (
        <p>No commits found yet. New commits will appear here.</p>
      ) : (
        <div className="commit-list">
          {commits.map((commit) => (
            <div key={commit.hash} className="commit-item">
              <div className="commit-hash">{commit.hash}</div>
              <div className="commit-message">{commit.message}</div>
              <div className="commit-author">{commit.author}</div>
              <div className="commit-timestamp">{commit.timestamp}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CommitList
