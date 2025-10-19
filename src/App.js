// src/App.js
import React, { useState, useEffect } from 'react';
// Import Components
import FoodInput from './components/FoodInput';
import TransportInput from './components/TransportInput';

// --- API Constants ---
const API_URL = 'http://127.0.0.1:5000';
const USER_ID = 1; 

// Simple Leaderboard Component (for display)
const Leaderboard = ({ data }) => (
    <div style={{ padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h3 style={{marginTop: 0}}>Rankings</h3>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
            {data.map((user) => (
                <li key={user.rank} style={{ padding: '5px 0', borderBottom: '1px dotted #eee', display: 'flex', justifyContent: 'space-between' }}>
                    <strong>#{user.rank} {user.username}</strong>
                    <span style={{ color: 'darkgreen' }}>{user.points} Pts</span>
                </li>
            ))}
        </ul>
    </div>
);

// Main App Component
function App() {
    const [activeTab, setActiveTab] = useState('Summary'); // Start on Summary tab
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [leaderboard, setLeaderboard] = useState([]);

    // Combined Fetch Function
    const fetchData = async () => {
        try {
            // 1. Fetch Summary Data
            const summaryResponse = await fetch(`${API_URL}/api/summary/${USER_ID}`);
            const summaryData = await summaryResponse.json();
            setSummary(summaryData);

            // 2. Fetch Leaderboard Data
            const leaderboardResponse = await fetch(`${API_URL}/api/leaderboard`);
            const leaderboardData = await leaderboardResponse.json();
            setLeaderboard(leaderboardData);

            setError(null);
        } catch (err) {
            console.error("Connection failed:", err);
            setError("Error: Backend API not reachable. Is the Flask server running in Terminal 1?");
        } finally {
            setLoading(false);
        }
    };

    // Run fetch on load
    useEffect(() => {
        fetchData();
    }, []); 

    // Tab Data (Matching your screenshot tabs)
    const tabs = ['Food', 'Transport', 'Activities', 'Summary', 'Eco Store', 'Leaderboard'];

    // Conditional rendering based on active tab
    const renderContent = () => {
        switch (activeTab) {
            case 'Food':
                return <FoodInput fetchData={fetchData} />;
            case 'Transport':
                return <TransportInput fetchData={fetchData} />;
            case 'Summary':
                if (!summary) return <div>No data available.</div>;
                return (
                    <div style={{ padding: '20px' }}>
                        <h3 style={{ borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>Evening Summary</h3>
                        
                        {/* CO2 Display */}
                        <div style={{ fontSize: '2em', fontWeight: 'bold', color: 'darkred' }}>
                            {summary.total_co2_kg} kg CO2
                        </div>
                        <div style={{ color: 'darkgreen', marginBottom: '20px' }}>EcoPoints: +{summary.eco_points}</div>

                        {/* AI Insights (Bridge to Motivation) */}
                        <div style={{ padding: '15px', backgroundColor: '#e0f7fa', borderLeft: '3px solid #00bcd4', marginBottom: '20px' }}>
                             <strong>AI Insights & Tips:</strong> {summary.insight_suggestion}
                        </div>
                        
                        {/* Static Placeholder elements from screenshot */}
                        <div style={{ border: '1px solid #ccc', padding: '15px', height: '150px', marginBottom: '20px' }}>
                            Last 7 Days (Chart Placeholder)
                        </div>
                        
                        <button style={{ padding: '10px 15px', backgroundColor: 'green', color: 'white', border: 'none' }}>Save Day & Earn Points</button>
                    </div>
                );
            case 'Leaderboard':
                return (
                    <div style={{ padding: '20px' }}>
                        <h3>Top Ecopulse Users</h3>
                        <Leaderboard data={leaderboard} />
                    </div>
                );
            case 'Activities':
            case 'Electricity':
            case 'Eco Store':
                return <div style={{ padding: '20px' }}>{activeTab} Content (Placeholder)</div>;
            default:
                return <div style={{ padding: '20px' }}>Select a tab to begin.</div>;
        }
    };

    // --- Render Logic ---
    if (loading) return <div style={{textAlign: 'center', marginTop: '50px'}}><h1>Loading EcoTrack Data...</h1></div>;
    if (error) return <div style={{textAlign: 'center', marginTop: '50px', color: 'red'}}><h2>{error}</h2></div>;

    return (
        <div style={{ maxWidth: '900px', margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
            <header style={{ background: '#333', color: 'white', padding: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '1.5em' }}>Ecopulse</div>
                <div style={{ fontSize: '0.9em' }}>
                    EcoPoints: {summary.eco_points} | Streak: {summary.current_streak} | Badges: {summary.title}
                </div>
            </header>
            
            {/* Tabs Navigation */}
            <div style={{ display: 'flex', background: '#444' }}>
                {tabs.map(tab => (
                    <button 
                        key={tab} 
                        onClick={() => setActiveTab(tab)}
                        style={{ 
                            padding: '10px 15px', 
                            border: 'none', 
                            backgroundColor: activeTab === tab ? 'darkgreen' : 'transparent',
                            color: 'white',
                            cursor: 'pointer',
                            transition: 'background-color 0.3s'
                        }}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            <div style={{ background: '#fff', minHeight: '500px', border: '1px solid #ccc' }}>
                {renderContent()}
            </div>
        </div>
    );
}

export default App;