import React from 'react'

function TestComponent() {
  return (
    <div style={{ 
      padding: '20px', 
      margin: '20px', 
      backgroundColor: '#e0e0e0', 
      border: '2px solid #333',
      borderRadius: '8px'
    }}>
      <h2>Test Component</h2>
      <p>If you can see this, React is working!</p>
      <button 
        onClick={() => alert('Button clicked!')}
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Test Button
      </button>
    </div>
  )
}

export default TestComponent
