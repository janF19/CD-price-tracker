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
        const trainsResponse = await axios.get('https://cd-price-tracker.onrender.com/unique-trains');
        
        // Fetch full price history
        const priceHistoryResponse = await axios.get('https://cd-price-tracker.onrender.com/full-price-history');
        console.log('Raw API Response:', priceHistoryResponse.data);
        // Example output:
        // [
        //   { train_code: "123", price: "199.00", scrape_timestamp: "2024-03-20T14:30:00Z" },
        //   { train_code: "123", price: "220.00", scrape_timestamp: "2024-03-21T14:30:00Z" },
        //   { train_code: "456", price: "150.00", scrape_timestamp: "2024-03-20T14:30:00Z" }
        // ]
        
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

        console.log('Processed Data:', processedData);
        // Example output:
        // [
        //   {
        //     trainCode: "123",
        //     entries: [
        //       { trainCode: "123", price: 199.00, timestamp: "3/20/2024, 2:30:00 PM" },
        //       { trainCode: "123", price: 220.00, timestamp: "3/21/2024, 2:30:00 PM" }
        //     ]
        //   },
        //   {
        //     trainCode: "456",
        //     entries: [
        //       { trainCode: "456", price: 150.00, timestamp: "3/20/2024, 2:30:00 PM" }
        //     ]
        //   }
        // ]

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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-12 text-center tracking-tight">
          Train Price History
        </h1>

        <div className="mb-8 bg-white p-8 rounded-lg shadow-sm">
          <label htmlFor="train-select" className="block text-lg font-medium text-gray-700 mb-3">
            Select Train:
          </label>
          <select 
            id="train-select"
            value={selectedTrain || ''}
            onChange={(e) => setSelectedTrain(e.target.value)}
            className="w-full md:w-auto px-6 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
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
          <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
            <div className="h-[500px] w-full">
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>
        )}

        {/* Detailed Price Table */}
        {selectedTrainData && (
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 border-b pb-4">
              Price History Details
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white rounded-lg overflow-hidden">
                <thead>
                  <tr className="bg-gray-100 border-b border-gray-200">
                    <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider w-1/2">
                      Timestamp
                    </th>
                    <th className="px-8 py-4 text-left text-sm font-bold text-gray-700 uppercase tracking-wider w-1/2">
                      Price (CZK)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {selectedTrainData.entries.map((entry, index) => (
                    <tr 
                      key={index}
                      className="border-b border-gray-100 hover:bg-blue-50 transition-colors duration-150"
                    >
                      <td className="px-8 py-4">
                        <div className="text-base font-medium text-gray-800">
                          {entry.timestamp}
                        </div>
                      </td>
                      <td className="px-8 py-4">
                        <div className="text-base font-semibold text-blue-600">
                          {entry.price.toFixed(2)} CZK
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Total Records Card */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex justify-between items-center px-4">
                <span className="text-base font-medium text-gray-600">Total Records:</span>
                <span className="text-base font-bold text-gray-900">
                  {selectedTrainData.entries.length}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainPriceHistoryChart;