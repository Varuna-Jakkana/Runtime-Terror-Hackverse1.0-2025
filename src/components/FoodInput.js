// src/components/FoodInput.js
import React, { useState } from 'react';

const API_URL = 'http://127.0.0.1:5000';
const USER_ID = 1; 

const FOOD_ITEMS = [
    { name: 'Rice', co2: 0.3, type: 'Rice' },
    { name: 'Sambar', co2: 0.4, type: 'Sambar' },
    { name: 'Curry', co2: 0.8, type: 'Curry' },
    { name: 'Roti', co2: 0.3, type: 'Roti' },
    { name: 'Dosa', co2: 0.5, type: 'Dosa' },
    { name: 'Briyani', co2: 1.2, type: 'Briyani' },
    { name: 'Salad', co2: 0.2, type: 'Salad' },
    { name: 'Yogurt', co2: 0.3, type: 'Yogurt' },
];

const FoodInput = ({ fetchData }) => {
    const [selectedItem, setSelectedItem] = useState(null);

    const handleLogFood = async (item) => {
        const dataToSend = {
            category: 'Food',
            type: item.type,
            value: 1.0 // Assuming 1 serving per click
        };

        try {
            const response = await fetch(`${API_URL}/api/track/${USER_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dataToSend)
            });

            if (!response.ok) {
                throw new Error('Failed to log food activity.');
            }
            
            await fetchData(); // Refresh dashboard data
            alert(`${item.name} logged! Check your Summary for points.`);
            setSelectedItem(item);

        } catch (err) {
            alert(`Error logging activity: ${err.message}`);
        }
    };

    return (
        <div style={{ padding: '20px', display: 'flex', gap: '20px' }}>
            <div style={{ flex: 2, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
                {FOOD_ITEMS.map((item) => (
                    <div 
                        key={item.name}
                        onClick={() => handleLogFood(item)}
                        style={{
                            padding: '15px', 
                            backgroundColor: selectedItem && selectedItem.name === item.name ? '#dcfce7' : '#f0f0f0',
                            border: '1px solid #ccc', 
                            borderRadius: '8px', 
                            cursor: 'pointer',
                            textAlign: 'center'
                        }}
                    >
                        <strong>{item.name}</strong>
                        <div style={{ fontSize: '0.8em', color: '#666' }}>{item.co2} kg CO2/serving</div>
                    </div>
                ))}
            </div>
            <div style={{ flex: 1, padding: '15px', border: '1px solid #ccc', borderRadius: '8px' }}>
                <strong>Selected / Last Logged:</strong>
                <p>{selectedItem ? selectedItem.name : 'Pick a food item'}</p>
                {selectedItem && (
                    <p style={{ fontSize: '0.9em', color: 'darkgreen' }}>Logged 1 serving.</p>
                )}
            </div>
        </div>
    );
};

export default FoodInput;