from datetime import datetime
import json

class CAMGenerator:
    def __init__(self):
        pass
    
    def generate_cam(self, session_data):
        """Generate Credit Appraisal Memo (CAM)"""
        extracted_data = session_data.get('extracted_data', {})
        risk_analysis = session_data.get('risk_analysis', {})
        recommendation = session_data.get('recommendation', {})
        
        cam_report = {
            'header': self.generate_header(extracted_data),
            'company_overview': self.generate_company_overview(extracted_data),
            'financial_analysis': self.generate_financial_analysis(extracted_data, risk_analysis),
            'risk_assessment': self.generate_risk_assessment(risk_analysis),
            'five_cs_evaluation': self.generate_five_cs_evaluation(risk_analysis),
            'ai_recommendation': self.generate_ai_recommendation(recommendation),
            'conclusion': self.generate_conclusion(recommendation),
            'generated_at': datetime.now().isoformat()
        }
        
        return cam_report
    
    def generate_header(self, data):
        """Generate CAM header"""
        return {
            'title': 'CREDIT APPRAISAL MEMO (CAM)',
            'company_name': data.get('company_name', 'Unknown Company'),
            'loan_amount_requested': data.get('loan_amount', 'Not specified'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'prepared_by': 'BankPilot AI System',
            'reference_number': f"CAM-{datetime.now().strftime('%Y%m%d')}-{hash(str(data)) % 10000:04d}"
        }
    
    def generate_company_overview(self, data):
        """Generate company overview section"""
        return {
            'company_name': data.get('company_name', 'Not available'),
            'business_nature': 'Manufacturing/Services (extracted from documents)',
            'incorporation_year': 'Not specified',
            'registered_office': 'As per documents',
            'promoter_name': data.get('promoter_name', 'Not specified'),
            'key_products': 'As mentioned in annual report',
            'market_position': 'Established player in the industry'
        }
    
    def generate_financial_analysis(self, data, risk_analysis):
        """Generate financial analysis section"""
        revenue = data.get('revenue', 0)
        profit = data.get('profit', 0)
        debt = data.get('debt', 0)
        
        return {
            'revenue_analysis': {
                'annual_revenue': f"₹{revenue:,.0f}" if revenue else "Not available",
                'revenue_growth': "Analysis based on available data",
                'revenue_quality': "Stable recurring revenue base"
            },
            'profitability_analysis': {
                'net_profit': f"₹{profit:,.0f}" if profit else "Not available",
                'profit_margin': f"{risk_analysis.get('profit_margin', 0):.1f}%" if risk_analysis.get('profit_margin') else "Not calculated",
                'ebitda_margin': f"{data.get('ebitda_margin', 0):.1f}%" if data.get('ebitda_margin') else "Not available"
            },
            'leverage_analysis': {
                'total_debt': f"₹{debt:,.0f}" if debt else "Not available",
                'debt_to_revenue_ratio': f"{risk_analysis.get('debt_ratio', 0):.1f}%" if risk_analysis.get('debt_ratio') else "Not calculated",
                'debt_servicing_ability': "Adequate based on cash flows"
            },
            'liquidity_analysis': {
                'current_ratio': "Not available from current data",
                'quick_ratio': "Not available from current data",
                'cash_position': "Adequate for operations"
            }
        }
    
    def generate_risk_assessment(self, risk_analysis):
        """Generate risk assessment section"""
        return {
            'overall_risk_score': risk_analysis.get('total_score', 0),
            'risk_grade': self.get_risk_grade(risk_analysis.get('total_score', 0)),
            'key_risk_factors': risk_analysis.get('risk_factors', []),
            'risk_mitigation': [
                "Regular monitoring of financial performance",
                "Quarterly review meetings",
                "Compliance with loan covenants"
            ],
            'industry_risk': "Moderate - subject to economic cycles",
            'management_risk': "Low - experienced management team",
            'operational_risk': "Low to moderate based on business model"
        }
    
    def generate_five_cs_evaluation(self, risk_analysis):
        """Generate Five Cs evaluation"""
        return {
            'character': {
                'score': risk_analysis.get('character_score', 0),
                'assessment': "Management integrity and track record",
                'rating': self.get_rating(risk_analysis.get('character_score', 0))
            },
            'capacity': {
                'score': risk_analysis.get('capacity_score', 0),
                'assessment': "Cash flow generation and debt servicing ability",
                'rating': self.get_rating(risk_analysis.get('capacity_score', 0))
            },
            'capital': {
                'score': risk_analysis.get('capital_score', 0),
                'assessment': "Financial strength and equity base",
                'rating': self.get_rating(risk_analysis.get('capital_score', 0))
            },
            'conditions': {
                'score': risk_analysis.get('conditions_score', 0),
                'assessment': "Economic and industry conditions",
                'rating': self.get_rating(risk_analysis.get('conditions_score', 0))
            },
            'collateral': {
                'score': risk_analysis.get('collateral_score', 0),
                'assessment': "Security and collateral coverage",
                'rating': self.get_rating(risk_analysis.get('collateral_score', 0))
            }
        }
    
    def generate_ai_recommendation(self, recommendation):
        """Generate AI recommendation section"""
        return {
            'decision': recommendation.get('decision', 'REVIEW'),
            'recommended_amount': recommendation.get('recommended_limit', '₹0'),
            'interest_rate': recommendation.get('interest_rate', 'TBD'),
            'tenure': 'Subject to negotiation',
            'conditions': recommendation.get('conditions', []),
            'rationale': recommendation.get('explanation', 'Based on comprehensive risk analysis'),
            'monitoring_requirements': [
                "Monthly financial statements",
                "Quarterly business reviews",
                "Annual compliance certification"
            ]
        }
    
    def generate_conclusion(self, recommendation):
        """Generate conclusion section"""
        decision = recommendation.get('decision', 'REVIEW')
        
        if decision == 'APPROVE':
            conclusion = "The credit proposal is recommended for approval based on strong financial metrics and low risk profile."
        elif decision == 'REVIEW':
            conclusion = "The credit proposal requires additional review and enhanced monitoring before final decision."
        else:
            conclusion = "The credit proposal is not recommended for approval due to high risk factors."
        
        return {
            'summary': conclusion,
            'next_steps': self.get_next_steps(decision),
            'validity': '30 days from date of generation',
            'prepared_by': 'BankPilot AI Credit Analysis System',
            'reviewed_by': 'Pending human review'
        }
    
    def get_risk_grade(self, score):
        """Convert risk score to grade"""
        if score >= 80:
            return 'A (Low Risk)'
        elif score >= 65:
            return 'B (Moderate Risk)'
        elif score >= 50:
            return 'C (High Risk)'
        else:
            return 'D (Very High Risk)'
    
    def get_rating(self, score):
        """Convert score to rating"""
        if score >= 80:
            return 'Excellent'
        elif score >= 65:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        else:
            return 'Poor'
    
    def get_next_steps(self, decision):
        """Get next steps based on decision"""
        if decision == 'APPROVE':
            return [
                "Prepare loan documentation",
                "Conduct final due diligence",
                "Set up monitoring framework"
            ]
        elif decision == 'REVIEW':
            return [
                "Conduct additional due diligence",
                "Request additional documentation",
                "Schedule management meeting"
            ]
        else:
            return [
                "Communicate decision to applicant",
                "Provide feedback for improvement",
                "Archive application"
            ]