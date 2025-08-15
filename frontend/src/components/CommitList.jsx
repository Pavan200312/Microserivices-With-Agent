import React from 'react'
import './CommitList.css'

function CommitList({ commits, loading, isTracking, error, onRefresh }) {
  console.log('📋 CommitList props:', { commits, loading, isTracking, error })
  if (loading) {
    return (
      <div className="dashboard-section">
        <h2>Loading...</h2>
        <div className="loading-spinner">⏳</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-section">
        <h2>Error</h2>
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={onRefresh} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Remove the isTracking check - show commits regardless of tracking state

  return (
    <div className="dashboard-section">
      <div className="commit-header">
        <h2>Recent Commits {isTracking ? '(Tracking Active)' : '(Not Tracking)'}</h2>
        <button onClick={onRefresh} className="refresh-button">
          🔄 Refresh
        </button>
      </div>
      
      {commits.length === 0 ? (
        <div className="no-commits">
          <p>No commits found yet. New commits will appear here.</p>
          <p>Make sure you have:</p>
          <ul>
            <li>✅ Started tracking</li>
            <li>✅ Valid GitHub token</li>
            <li>✅ Repository with commits</li>
          </ul>
        </div>
      ) : (
        <div className="commit-list">
          {commits.map((commit) => (
            <div key={commit.commit_hash || commit.hash} className="commit-item">
              <div className="commit-hash">
                {commit.commit_hash || commit.hash}
              </div>
              <div className="commit-message">
                {commit.message}
              </div>
              <div className="commit-author">
                👤 {commit.author}
              </div>
              <div className="commit-timestamp">
                📅 {new Date(commit.timestamp).toLocaleString()}
              </div>
              {commit.repository && (
                <div className="commit-repository">
                  📁 {commit.repository}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CommitList
