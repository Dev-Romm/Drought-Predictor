"""
Drought classification module for NDVI-based drought severity assessment.

This module provides functionality to classify drought levels based on NDVI values
and change rates, following the thresholds defined in the requirements.
"""

from enum import Enum
from typing import Tuple


class DroughtLevel(Enum):
    """Enumeration of drought severity levels."""
    NORMAL = "Normal"
    ALERT = "Alert"
    ALARM = "Alarm"
    EMERGENCY = "Emergency"


class DroughtClassifier:
    """
    Classifier for drought severity based on NDVI values and change rates.
    
    Uses NDVI thresholds and change rate thresholds to determine drought levels
    according to Requirements 5.1-5.5.
    """
    
    # NDVI thresholds
    THRESHOLD_EMERGENCY = 0.2
    THRESHOLD_ALARM = 0.3
    THRESHOLD_ALERT = 0.4
    
    # Change rate thresholds (percentage)
    CHANGE_ALERT = -5.0
    CHANGE_ALARM = -10.0
    CHANGE_EMERGENCY = -20.0
    
    @staticmethod
    def classify(current_ndvi: float, predicted_ndvi: float) -> Tuple[DroughtLevel, float]:
        """
        Classify drought severity based on current and predicted NDVI values.
        
        Classification rules (Requirements 5.2-5.5):
        - Normal: NDVI > 0.4 AND change rate > -5%
        - Alert: NDVI between 0.3-0.4 OR change rate between -5% and -10%
        - Alarm: NDVI between 0.2-0.3 OR change rate between -10% and -20%
        - Emergency: NDVI < 0.2 OR change rate < -20%
        
        Args:
            current_ndvi: Current NDVI value
            predicted_ndvi: Predicted NDVI value
            
        Returns:
            Tuple of (DroughtLevel, change_rate_percentage)
        """
        # Calculate change rate: ((predicted - current) / current) × 100
        change_rate = ((predicted_ndvi - current_ndvi) / current_ndvi) * 100
        
        # Apply classification rules - check most severe conditions first
        # Emergency: NDVI < 0.2 OR change rate < -20%
        if predicted_ndvi < DroughtClassifier.THRESHOLD_EMERGENCY or \
           change_rate < DroughtClassifier.CHANGE_EMERGENCY:
            return (DroughtLevel.EMERGENCY, change_rate)
        
        # Alarm: NDVI between 0.2-0.3 OR change rate between -10% and -20%
        if predicted_ndvi < DroughtClassifier.THRESHOLD_ALARM or \
           change_rate < DroughtClassifier.CHANGE_ALARM:
            return (DroughtLevel.ALARM, change_rate)
        
        # Alert: NDVI between 0.3-0.4 OR change rate between -5% and -10%
        if predicted_ndvi < DroughtClassifier.THRESHOLD_ALERT or \
           change_rate < DroughtClassifier.CHANGE_ALERT:
            return (DroughtLevel.ALERT, change_rate)
        
        # Normal: NDVI > 0.4 AND change rate > -5%
        return (DroughtLevel.NORMAL, change_rate)
    
    @staticmethod
    def get_color_code(level: DroughtLevel) -> str:
        """
        Get the color code for a given drought level.
        
        Color mapping (Requirement 5.7):
        - Normal: green
        - Alert: yellow
        - Alarm: orange
        - Emergency: red
        
        Args:
            level: DroughtLevel enum value
            
        Returns:
            Hex color code string
        """
        color_map = {
            DroughtLevel.NORMAL: "#00FF00",      # green
            DroughtLevel.ALERT: "#FFFF00",       # yellow
            DroughtLevel.ALARM: "#FFA500",       # orange
            DroughtLevel.EMERGENCY: "#FF0000"    # red
        }
        return color_map[level]
