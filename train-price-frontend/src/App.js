import React, { useState, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

// Register Chart.js components
Chart.register(...registerables);

const TrainPriceHistoryChart = () => {
  const [trainData, setTrainData] = useState([]);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTrainPriceHistory = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch unique trains first
        const trainsResponse = await axios.get('https://cd-price-tracker.onrender.com');
        
        // Fetch full price history
        const priceHistoryResponse = await axios.get('https://cd-price-tracker.onrender.com');
        
        // Group data by train
        const groupedData = priceHistoryResponse.data.reduce((acc, entry) => {
          const { train_code, price, scrape_timestamp } = entry;
          
          if (!acc[train_code]) {
            acc[train_code] = [];
          }
          
          acc[train_code].push({
            trainCode: train_code,
            price: parseFloat(price),
            timestamp: new Date(scrape_timestamp).toLocaleString()
          });
          
          return acc;
        }, {});

        // Convert grouped data to array
        const processedData = Object.entries(groupedData).map(([trainCode, entries]) => ({
          trainCode,
          entries: entries.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        }));

        setTrainData(processedData);
        
        // Auto-select first train if available
        if (processedData.length > 0) {
          setSelectedTrain(processedData[0].trainCode);
        }
      } catch (error) {
        console.error('Error fetching train price history:', error);
        setError(error.message || 'Failed to fetch train price history');
      } finally {
        setLoading(false);
      }
    };

    fetchTrainPriceHistory();
  }, []);

  // Render loading or error states
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  // Get selected train's data
  const selectedTrainData = trainData.find(train => train.trainCode === selectedTrain);

  // Prepare chart data
  const chartData = selectedTrainData ? {
    labels: selectedTrainData.entries.map(entry => entry.timestamp),
    datasets: [{
      label: `${selectedTrain} Price (CZK)`,
      data: selectedTrainData.entries.map(entry => entry.price),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Price (CZK)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Timestamp'
        }
      }
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Train Price History</h1>

      {/* Train Selection Dropdown */}
      <div className="mb-4">
        <label htmlFor="train-select" className="mr-2">Select Train:</label>
        <select 
          id="train-select"
          value={selectedTrain || ''}
          onChange={(e) => setSelectedTrain(e.target.value)}
          className="p-2 border rounded"
        >
          {trainData.map(train => (
            <option key={train.trainCode} value={train.trainCode}>
              {train.trainCode}
            </option>
          ))}
        </select>
      </div>

      {/* Price History Chart */}
      {chartData && (
        <div className="h-[500px] w-full mb-4">
          <Line data={chartData} options={chartOptions} />
        </div>
      )}

      {/* Detailed Price Table */}
      {selectedTrainData && (
        <div className="mt-4">
          <h2 className="text-xl font-bold mb-4">Price History Details</h2>
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2">Timestamp</th>
                <th className="border p-2">Price (CZK)</th>
              </tr>
            </thead>
            <tbody>
              {selectedTrainData.entries.map((entry, index) => (
                <tr 
                  key={index} 
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className="border p-2">{entry.timestamp}</td>
                  <td className="border p-2">{entry.price.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TrainPriceHistoryChart;