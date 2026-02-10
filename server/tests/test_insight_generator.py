"""
Unit tests for InsightGenerator class.

Tests insight message generation for each drought level with specific
examples and validates message content.
"""

import sys
import os

# Add server directory to path (parent of tests directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from insight_generator import InsightGenerator
from drought_classifier import DroughtLevel


class TestInsightGenerator:
    """Test suite for InsightGenerator class."""
    
    def test_generate_insights_normal(self):
        """Test Normal level insight generation (Requirement 6.1)."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.NORMAL,
            change_rate=-2.5,
            predicted_ndvi=0.45,
            horizon_weeks=4
        )
        
        assert len(insights) >= 2
        assert any("healthy" in insight.lower() or "good" in insight.lower() 
                   for insight in insights)
        assert any("4 weeks" in insight for insight in insights)
    
    def test_generate_insights_alert(self):
        """Test Alert level insight generation (Requirement 6.2)."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.ALERT,
            change_rate=-7.2,
            predicted_ndvi=0.35,
            horizon_weeks=4
        )
        
        assert len(insights) >= 2
        assert any("decline" in insight.lower() for insight in insights)
        assert any("-7.2" in insight for insight in insights)
        assert any("0.35" in insight or "0.350" in insight for insight in insights)
        assert any("monitor" in insight.lower() for insight in insights)
    
    def test_generate_insights_alarm(self):
        """Test Alarm level insight generation (Requirement 6.3)."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.ALARM,
            change_rate=-15.3,
            predicted_ndvi=0.25,
            horizon_weeks=6
        )
        
        assert len(insights) >= 2
        assert any("significant" in insight.lower() or "decline" in insight.lower() 
                   for insight in insights)
        assert any("-15.3" in insight for insight in insights)
        assert any("0.25" in insight or "0.250" in insight for insight in insights)
        assert any("migration" in insight.lower() for insight in insights)
    
    def test_generate_insights_emergency(self):
        """Test Emergency level insight generation (Requirement 6.4)."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.EMERGENCY,
            change_rate=-22.5,
            predicted_ndvi=0.18,
            horizon_weeks=4
        )
        
        assert len(insights) >= 2
        assert any("severe" in insight.lower() or "emergency" in insight.lower() 
                   for insight in insights)
        assert any("0.18" in insight or "0.180" in insight for insight in insights)
        assert any("immediate" in insight.lower() for insight in insights)
    
    def test_insights_include_numerical_info(self):
        """Test that insights include specific numerical information (Requirement 6.6)."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.ALERT,
            change_rate=-8.5,
            predicted_ndvi=0.32,
            horizon_weeks=2
        )
        
        # Should include change rate or NDVI value
        has_numerical_info = any(
            "-8.5" in insight or "0.32" in insight or "0.320" in insight 
            for insight in insights
        )
        assert has_numerical_info, "Insights should include specific numerical information"
    
    def test_insights_non_technical_language(self):
        """Test that insights use clear, non-technical language."""
        insights = InsightGenerator.generate_insights(
            level=DroughtLevel.NORMAL,
            change_rate=1.5,
            predicted_ndvi=0.48,
            horizon_weeks=4
        )
        
        # Check for pastoralist-friendly terms
        combined_text = " ".join(insights).lower()
        assert any(term in combined_text for term in 
                   ["pasture", "grazing", "vegetation", "greenness"])
    
    def test_different_horizon_weeks(self):
        """Test that horizon weeks are correctly included in messages."""
        for weeks in [2, 4, 6]:
            insights = InsightGenerator.generate_insights(
                level=DroughtLevel.ALERT,
                change_rate=-6.0,
                predicted_ndvi=0.35,
                horizon_weeks=weeks
            )
            
            assert any(f"{weeks} weeks" in insight for insight in insights)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

