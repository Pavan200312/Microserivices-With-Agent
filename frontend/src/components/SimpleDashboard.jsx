import React, { useState, useEffect } from 'react'
import { apiService, handleApiError } from '../services/api'

function SimpleDashboard() {
  const [allCommits, setAllCommits] = useState([])
  const [displayedCommits, setDisplayedCommits] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isTracking, setIsTracking] = useState(false)
  const [currentCommitIndex, setCurrentCommitIndex] = useState(0)
  const [isDisplayingCommits, setIsDisplayingCommits] = useState(false)

  const fetchCommits = async () => {
    try {
      console.log('🔍 Fetching commits from database...')
      setLoading(true)
      setError(null)
      
      const commitsData = await apiService.getCommits()
      console.log('✅ Commits fetched from database:', commitsData)
      
      if (!Array.isArray(commitsData)) {
        console.error('❌ Invalid response format:', commitsData)
        setError('Invalid response format from server')
        return
      }
      
      // Create a Map to ensure truly unique commits by hash
      const commitMap = new Map()
      
      commitsData.forEach(commit => {
        const commitHash = commit.commit_hash || commit.hash
        if (commitHash && !commitMap.has(commitHash)) {
          commitMap.set(commitHash, commit)
        } else if (commitHash) {
          console.log(`⚠️ Duplicate commit hash found: ${commitHash}`)
        }
      })
      
      // Convert Map back to array and sort by timestamp (newest first)
      const uniqueCommits = Array.from(commitMap.values())
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .map((commit, index) => ({
          ...commit,
          uniqueId: commit.commit_hash || commit.hash || `commit-${index}`,
          displayOrder: index + 1
        }))
      
      console.log(`📊 Processed ${commitsData.length} commits from database, ${uniqueCommits.length} unique commits`)
      console.log('🔑 Unique commit hashes:', uniqueCommits.map(c => c.commit_hash || c.hash))
      setAllCommits(uniqueCommits)
      
    } catch (error) {
      console.error('❌ Failed to fetch commits:', error)
      const errorMessage = handleApiError(error)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const startTracking = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🚀 Starting tracking process...')
      
      // Start tracking (this will fetch and store commits in database)
      const result = await apiService.startTracking()
      console.log('✅ Tracking started:', result)
      setIsTracking(true)
      
      // Wait a moment for the backend to process
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Fetch commits from database (not from GitHub again)
      await fetchCommits()
      
    } catch (error) {
      console.error('❌ Failed to start tracking:', error)
      const errorMessage = handleApiError(error)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const showNextCommit = () => {
    if (allCommits.length === 0) {
      console.log('❌ No commits available')
      return
    }
    
    // If this is the first click, start displaying
    if (displayedCommits.length === 0) {
      setIsDisplayingCommits(true)
      setCurrentCommitIndex(0)
      
      // Show first commit
      const firstCommit = allCommits[0]
      setDisplayedCommits([firstCommit])
      console.log(`📝 Displaying commit 1/${allCommits.length}: ${firstCommit.commit_hash || firstCommit.hash} - ${firstCommit.message}`)
      return
    }
    
    // Check if we've displayed all commits
    if (displayedCommits.length >= allCommits.length) {
      console.log('✅ All commits already displayed')
      return
    }
    
    // Show next commit
    const nextIndex = displayedCommits.length
    const nextCommit = allCommits[nextIndex]
    
    setCurrentCommitIndex(nextIndex)
    setDisplayedCommits(prev => [...prev, nextCommit])
    console.log(`📝 Displaying commit ${nextIndex + 1}/${allCommits.length}: ${nextCommit.commit_hash || nextCommit.hash} - ${nextCommit.message}`)
  }





  const clearDatabase = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🗑️ Clearing database...')
      const response = await fetch('http://localhost:8000/api/clear-commits', {
        method: 'DELETE'
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Database cleared:', result)
                 setAllCommits([])
         setDisplayedCommits([])
         setIsTracking(false)
         setCurrentCommitIndex(0)
         setIsDisplayingCommits(false)
      } else {
        throw new Error(`Failed to clear database: ${response.status}`)
      }
    } catch (error) {
      console.error('❌ Failed to clear database:', error)
      setError('Failed to clear database')
    } finally {
      setLoading(false)
    }
  }



  // Don't auto-start display - let user control it manually
  // useEffect(() => {
  //   if (isTracking && allCommits.length > 0 && !isDisplayingCommits) {
  //     startDisplayingCommits()
  //   }
  // }, [isTracking, allCommits])



  useEffect(() => {
    console.log('🚀 SimpleDashboard mounted')
    // Don't fetch commits on mount - wait for user to click "Track Now"
    console.log('📋 Waiting for user to click "Track Now" to start tracking')
  }, [])

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '2rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2.5rem' }}>
          GitHub Commit Tracker
        </h1>
        <p style={{ margin: 0, fontSize: '1.1rem', opacity: 0.9 }}>
          Real-time commit tracking with AI analysis
        </p>
      </div>

      {/* Track Now Button */}
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <h2>Start Tracking</h2>
        <p>Click the button below to start tracking GitHub commits</p>
                 <button 
           onClick={isTracking ? showNextCommit : startTracking}
           disabled={loading}
           style={{
             background: isTracking 
               ? 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)'
               : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
             color: 'white',
             border: 'none',
             padding: '1rem 2rem',
             fontSize: '1.1rem',
             borderRadius: '8px',
             cursor: loading ? 'not-allowed' : 'pointer',
             opacity: loading ? 0.7 : 1,
             fontWeight: '600',
             marginRight: '1rem'
           }}
         >
           {loading ? 'Loading...' : isTracking ? `Show Next Commit (${displayedCommits.length + 1}/${allCommits.length})` : 'Track Now'}
         </button>
         
         {isTracking && allCommits.length > 0 && (
           <div style={{ marginTop: '1rem' }}>
             <button 
               onClick={clearDatabase}
               disabled={loading}
               style={{
                 background: '#dc3545',
                 color: 'white',
                 border: 'none',
                 padding: '0.5rem 1rem',
                 borderRadius: '4px',
                 cursor: loading ? 'not-allowed' : 'pointer',
                 opacity: loading ? 0.5 : 1
               }}
             >
               🗑️ Clear DB
             </button>
           </div>
         )}
      </div>

      {/* Commits List */}
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>
            Commits {isTracking ? '(Tracking Active)' : '(Not Tracking)'}
                         {isDisplayingCommits && (
               <span style={{ fontSize: '1rem', color: '#6c757d', marginLeft: '1rem' }}>
                 Showing {displayedCommits.length} of {allCommits.length}
               </span>
             )}
          </h2>
          <button 
            onClick={fetchCommits}
            disabled={loading}
            style={{
              background: '#007bff',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            🔄 Refresh
          </button>
        </div>
        
        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <h3>Loading...</h3>
            <div>⏳</div>
          </div>
        )}

        {error && (
          <div style={{ 
            background: '#f8d7da', 
            color: '#721c24', 
            padding: '1rem', 
            borderRadius: '4px',
            marginBottom: '1rem'
          }}>
            <p>❌ {error}</p>
            <button 
              onClick={fetchCommits}
              style={{
                background: '#dc3545',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && displayedCommits.length === 0 && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>No commits displayed yet. Click "Track Now" to start viewing commits.</p>
            <p>Make sure you have:</p>
            <ul style={{ textAlign: 'left', display: 'inline-block' }}>
              <li>✅ Started tracking</li>
              <li>✅ Valid GitHub token</li>
              <li>✅ Repository with commits</li>
            </ul>
          </div>
        )}

        {!loading && !error && displayedCommits.length > 0 && (
          <div>
            {displayedCommits.map((commit, index) => {
              // Get unique commit hash for key
              const commitHash = commit.commit_hash || commit.hash || `commit-${index}`
              return (
                <div 
                  key={commitHash}
                  style={{
                    border: '1px solid #dee2e6',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1rem',
                    background: '#f8f9fa',
                    animation: index === displayedCommits.length - 1 ? 'fadeIn 0.5s ease-in' : 'none',
                    position: 'relative'
                  }}
                >
                  <div style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    background: '#007bff',
                    color: 'white',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    fontWeight: 'bold'
                  }}>
                    #{commit.displayOrder}
                  </div>
                  
                  <div style={{ 
                    fontFamily: 'monospace', 
                    fontSize: '0.9rem', 
                    color: '#6c757d',
                    marginBottom: '0.5rem',
                    fontWeight: 'bold',
                    wordBreak: 'break-all'
                  }}>
                    🔑 Hash: {commit.commit_hash || commit.hash}
                  </div>
                  <div style={{ 
                    fontSize: '1.1rem', 
                    fontWeight: '600',
                    marginBottom: '0.5rem',
                    color: '#333'
                  }}>
                    📝 {commit.message}
                  </div>
                  <div style={{ color: '#6c757d' }}>
                    👤 {commit.author} • 📅 {new Date(commit.timestamp).toLocaleString()}
                  </div>
                  {commit.repository && (
                    <div style={{ color: '#6c757d', marginTop: '0.5rem' }}>
                      📁 {commit.repository}
                    </div>
                  )}
                  {commit.branch && (
                    <div style={{ color: '#6c757d', marginTop: '0.5rem' }}>
                      🌿 Branch: {commit.branch}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

export default SimpleDashboard
