import google.generativeai as genai
import json

def get_ai_insights(disease, patient_data, prediction_results):
    """Generate AI-powered insights using Gemini"""
    try:
        # Prepare context for Gemini
        context = f"""
        Patient Profile:
        - Disease: {disease}
        - Age: {patient_data.get('age', 'N/A')}
        - Gender: {patient_data.get('gender', 'N/A')}
        - Disease Duration: {patient_data.get('duration_years', 'N/A')} years
        - Medication Compliance: {patient_data.get('compliance', 0)*100:.0f}%
        
        Current Predictions:
        - Disease Stage: {prediction_results.get('current_stage', 'N/A')}
        - Risk Score: {prediction_results.get('risk_score', 0):.1f}/10
        - Progression Risk: {prediction_results.get('progression_forecast', {}).get('to_next_stage', 0)*100:.0f}%
        
        Generate personalized health insights including:
        1. Key risk factors to address immediately
        2. Lifestyle modifications with specific targets
        3. Medication optimization suggestions
        4. Monitoring schedule recommendations
        5. Emergency warning signs to watch for
        
        Keep response concise, actionable, and medically appropriate.
        """
        
        response = genai.GenerativeModel('gemini-pro').generate_content(context)
        return response.text
    except Exception as e:
        return f"AI insights temporarily unavailable. Error: {str(e)}"

def get_medication_reminders(disease, medications):
    """Generate smart medication reminders"""
    try:
        context = f"""
        For {disease} patient taking medications: {', '.join(medications)}
        
        Generate a smart medication reminder system with:
        1. Optimal timing for each medication
        2. Food interaction warnings
        3. Side effects to monitor
        4. Missed dose instructions
        
        Format as JSON with medication name as key.
        """
        
        response = genai.GenerativeModel('gemini-pro').generate_content(context)
        return response.text
    except Exception as e:
        return "Medication reminders unavailable"

def analyze_health_trends(historical_data):
    """Analyze health trends from historical data"""
    try:
        context = f"""
        Historical health data: {json.dumps(historical_data, indent=2)}
        
        Analyze trends and provide:
        1. Disease progression patterns
        2. Compliance correlation with outcomes
        3. Seasonal variations if any
        4. Predictive insights for next 6 months
        
        Focus on actionable insights.
        """
        
        response = genai.GenerativeModel('gemini-pro').generate_content(context)
        return response.text
    except Exception as e:
        return "Trend analysis unavailable"

def generate_prescription_scan_insights(prescription_text):
    """Analyze prescription using OCR + AI"""
    try:
        context = f"""
        Prescription text: {prescription_text}
        
        Extract and analyze:
        1. Medication names and dosages
        2. Drug interactions warnings
        3. Compliance schedule optimization
        4. Cost-effective alternatives if appropriate
        5. Potential side effects to monitor
        
        Provide structured medical insights.
        """
        
        response = genai.GenerativeModel('gemini-pro').generate_content(context)
        return response.text
    except Exception as e:
        return "Prescription analysis unavailable"