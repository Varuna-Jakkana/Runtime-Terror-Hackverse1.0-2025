// src/components/TransportInput.js
import React, { useState } from 'react';

const API_URL = 'http://127.0.0.1:5000';
const USER_ID = 1; 

const TRANSPORT_MODES = [
    { name: 'Walk', co2: 0.0, type: 'Walk' },
    { name: 'Bike', co2: 0.0, type: 'Bike' },
    { name: 'Bus', co2: 0.063, type: 'Bus' },
    { name: 'Car', co2: 0.192, type: 'Car' },
    { name: 'EV', co2: 0.053, type: 'Car' }, // EV maps to 'Car' type for simpler backend logic
];

const TransportInput = ({ fetchData }) => {
    const [mode, setMode] = useState(TRANSPORT_MODES[0]);
    const [distance, setDistance] = useState(1.0);

    const handleLogTransport = async (e) => {
        e.preventDefault();

        const dataToSend = {
            category: 'Transport',
            type: mode.type, 
            value: parseFloat(distance)
        };

        try {
            const response = await fetch(`${API_URL}/api/track/${USER_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dataToSend)
            });

            if (!response.ok) {
                throw new Error('Failed to log transport activity.');
            }
            
            await fetchData();
            alert(`Logged ${distance} km by ${mode.name}. Check Summary!`);

        } catch (err) {
            alert(`Error logging activity: ${err.message}`);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <form onSubmit={handleLogTransport}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
                    {TRANSPORT_MODES.map((m) => (
                        <div 
                            key={m.name}
                            onClick={() => setMode(m)}
                            style={{
                                padding: '15px', 
                                backgroundColor: mode.name === m.name ? '#dcfce7' : '#f0f0f0',
                                border: '1px solid #ccc', 
                                borderRadius: '8px', 
                                cursor: 'pointer',
                                textAlign: 'center'
                            }}
                        >
                            <strong>{m.name}</strong>
                            <div style={{ fontSize: '0.8em', color: '#666' }}>{m.co2} kg CO2/km</div>
                        </div>
                    ))}
                </div>

                <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                        Distance (km) for {mode.name}:
                    </label>
                    <input 
                        type="number" 
                        value={distance} 
                        onChange={(e) => setDistance(e.target.value)}
                        placeholder="Enter distance"
                        required
                        style={{ padding: '10px', width: '150px', marginRight: '15px', borderRadius: '4px' }}
                    />
                    <button type="submit" style={{ padding: '10px 20px', backgroundColor: 'darkgreen', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                        Log Distance
                    </button>
                    <p style={{ color: 'red', marginTop: '10px' }}>
                        Estimated CO2: {(mode.co2 * distance).toFixed(3)} kg CO2
                    </p>
                </div>
            </form>
        </div>
    );
};

export default TransportInput;