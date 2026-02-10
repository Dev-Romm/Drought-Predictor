"""
Insight generation module for pastoralist-friendly drought interpretation.

This module generates clear, actionable messages about drought conditions
in language appropriate for pastoralist communities in Turkana County.
"""

from typing import List
from drought_classifier import DroughtLevel


class InsightGenerator:
    """
    Generator for pastoralist-friendly drought insights.
    
    Provides clear, non-technical interpretation messages based on drought
    levels and prediction data, following Requirements 6.1-6.6.
    """
    
    @staticmethod
    def generate_insights(
        level: DroughtLevel,
        change_rate: float,
        predicted_ndvi: float,
        horizon_weeks: int
    ) -> List[str]:
        """
        Generate pastoralist-friendly insight messages based on drought conditions.
        
        Creates 2-3 actionable messages that:
        - Use clear, non-technical language
        - Include specific numerical information
        - Provide guidance appropriate to the drought level
        - Are relevant to pastoralist decision-making
        
        Args:
            level: Classified drought severity level
            change_rate: Percentage change in NDVI (negative indicates decline)
            predicted_ndvi: Predicted NDVI value at forecast horizon
            horizon_weeks: Forecast time horizon in weeks
            
        Returns:
            List of insight message strings
            
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 12.5
        """
        insights = []
        
        if level == DroughtLevel.NORMAL:
            # Normal: Good pasture conditions (Requirement 6.1)
            insights.append("Vegetation conditions are healthy. Pasture quality is good for grazing.")
            
            if change_rate > 0:
                insights.append(
                    f"Greenness is expected to improve by {abs(change_rate):.1f}% over the next {horizon_weeks} weeks."
                )
            else:
                insights.append(
                    f"Vegetation is stable with minimal change ({change_rate:.1f}%) expected over {horizon_weeks} weeks."
                )
            
            insights.append("Continue normal grazing patterns. No immediate action needed.")
        
        elif level == DroughtLevel.ALERT:
            # Alert: Potential decline, suggest monitoring (Requirement 6.2)
            insights.append(
                f"Vegetation shows signs of decline ({change_rate:.1f}% change over {horizon_weeks} weeks)."
            )
            
            insights.append(
                f"Predicted greenness level is {predicted_ndvi:.3f}, indicating reduced pasture quality."
            )
            
            insights.append(
                "Monitor conditions closely. Begin planning for possible water and grazing adjustments."
            )
        
        elif level == DroughtLevel.ALARM:
            # Alarm: Worsening conditions, early migration planning (Requirement 6.3)
            insights.append(
                f"Significant greenness decline expected ({change_rate:.1f}% over {horizon_weeks} weeks)."
            )
            
            insights.append(
                f"Vegetation health will drop to {predicted_ndvi:.3f}, meaning poor pasture conditions ahead."
            )
            
            insights.append(
                "Consider early migration planning. Identify alternative grazing areas and water sources now."
            )
        
        elif level == DroughtLevel.EMERGENCY:
            # Emergency: Severe drought, immediate action (Requirement 6.4)
            insights.append(
                f"Severe drought conditions predicted. Greenness will be critically low (NDVI: {predicted_ndvi:.3f})."
            )
            
            if change_rate < -15:
                insights.append(
                    f"Rapid vegetation decline of {abs(change_rate):.1f}% expected within {horizon_weeks} weeks."
                )
            else:
                insights.append(
                    f"Vegetation is already severely degraded with further decline ({change_rate:.1f}%) expected."
                )
            
            insights.append(
                "Immediate action recommended: Move livestock to better grazing areas, secure emergency water supplies, and consider destocking if necessary."
            )
        
        return insights

