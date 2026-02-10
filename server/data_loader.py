"""
Data loader module for NDVI CSV data parsing and processing.
Handles CSV parsing, missing value handling, and NDVI range validation.
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import os


class NDVIDataLoader:
    """
    Loads and processes NDVI data from CSV file.
    
    Handles:
    - CSV parsing with date and NDVI columns
    - Missing value handling (interpolation or exclusion)
    - NDVI range validation (-1 to 1)
    - Data formatting for API responses and model input
    """
    
    def __init__(self, csv_path: str):
        """
        Initialize the NDVI data loader.
        
        Args:
            csv_path: Path to the CSV file containing NDVI data
        """
        self.csv_path = csv_path
        self.data: Optional[pd.DataFrame] = None
        self.load_data()
    
    def load_data(self) -> None:
        """
        Load and process NDVI data from CSV file.
        
        Performs:
        - CSV parsing with date column parsing
        - Missing value handling via linear interpolation
        - NDVI range validation (-1 to 1)
        - Sorting by date
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV has invalid structure or all values are invalid
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # Read CSV with date parsing
        # The CSV uses DD/MM/YYYY format based on the sample data
        df = pd.read_csv(
            self.csv_path,
            parse_dates=['start_date'],
            dayfirst=True  # Handle DD/MM/YYYY format
        )
        
        # Rename columns for consistency
        df = df.rename(columns={'start_date': 'date', 'mean_ndvi': 'ndvi'})
        
        # Validate NDVI range: mark values outside [-1, 1] as NaN
        df.loc[(df['ndvi'] < -1) | (df['ndvi'] > 1), 'ndvi'] = pd.NA
        
        # Handle missing values using linear interpolation
        # This fills gaps while preserving trends
        df['ndvi'] = df['ndvi'].interpolate(method='linear', limit_direction='both')
        
        # Drop any remaining rows with missing values (e.g., if all values were invalid)
        df = df.dropna(subset=['ndvi'])
        
        if df.empty:
            raise ValueError("No valid NDVI data after processing")
        
        # Sort by date to ensure chronological order
        df = df.sort_values('date').reset_index(drop=True)
        
        self.data = df
    
    def get_historical_data(self) -> List[Dict[str, any]]:
        """
        Get historical NDVI data formatted for API response.
        
        Returns:
            List of dictionaries with 'date' (ISO 8601 string) and 'ndvi' (float)
            
        Example:
            [
                {"date": "2017-01-01", "ndvi": 0.184},
                {"date": "2017-01-15", "ndvi": 0.183},
                ...
            ]
        """
        if self.data is None or self.data.empty:
            return []
        
        # Convert to list of dictionaries with ISO 8601 date format
        result = []
        for _, row in self.data.iterrows():
            result.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'ndvi': float(row['ndvi'])
            })
        
        return result
    
    def get_latest_ndvi(self) -> float:
        """
        Get the most recent NDVI value.
        
        Returns:
            Latest NDVI value as float
            
        Raises:
            ValueError: If no data is available
        """
        if self.data is None or self.data.empty:
            raise ValueError("No data available")
        
        return float(self.data.iloc[-1]['ndvi'])
    
    def get_data_for_model(self) -> pd.DataFrame:
        """
        Get NDVI data formatted for model input.
        
        Returns:
            DataFrame with 'date' and 'ndvi' columns, sorted chronologically
            
        Raises:
            ValueError: If no data is available
        """
        if self.data is None or self.data.empty:
            raise ValueError("No data available")
        
        # Return a copy to prevent external modifications
        return self.data[['date', 'ndvi']].copy()
