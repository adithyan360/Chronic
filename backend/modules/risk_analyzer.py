class RiskAnalyzer:
    def __init__(self):
        self.base_score = 100
        self.risk_factors = []
    
    def analyze_risk(self, extracted_data):
        """Analyze risk based on Five Cs of Credit"""
        self.risk_factors = []
        risk_points = 0
        
        # Character Analysis
        character_risk = self.analyze_character(extracted_data)
        risk_points += character_risk
        
        # Capacity Analysis
        capacity_risk = self.analyze_capacity(extracted_data)
        risk_points += capacity_risk
        
        # Capital Analysis
        capital_risk = self.analyze_capital(extracted_data)
        risk_points += capital_risk
        
        # Conditions Analysis
        conditions_risk = self.analyze_conditions(extracted_data)
        risk_points += conditions_risk
        
        # Collateral Analysis (now adds risk points instead of reducing)
        collateral_risk = self.analyze_collateral(extracted_data)
        risk_points += collateral_risk
        
        # GST vs Bank Analysis
        gst_bank_risk = self.analyze_gst_bank_mismatch(extracted_data)
        risk_points += gst_bank_risk
        
        # Calculate final score (ensure it stays between 0-100)
        total_score = max(0, min(100, self.base_score - risk_points))
        
        # Calculate individual component scores (0-100 scale)
        character_score = max(0, min(100, self.base_score - character_risk))
        capacity_score = max(0, min(100, self.base_score - capacity_risk))
        capital_score = max(0, min(100, self.base_score - capital_risk))
        conditions_score = max(0, min(100, self.base_score - conditions_risk))
        collateral_score = max(0, min(100, self.base_score - collateral_risk))
        
        return {
            'total_score': total_score,
            'risk_points': risk_points,
            'risk_factors': self.risk_factors,
            'character_score': character_score,
            'capacity_score': capacity_score,
            'capital_score': capital_score,
            'conditions_score': conditions_score,
            'collateral_score': collateral_score,
            'gst_bank_risk_score': gst_bank_risk,
            'debt_ratio': self.calculate_debt_ratio(extracted_data),
            'profit_margin': self.calculate_profit_margin(extracted_data)
        }
    
    def analyze_character(self, data):
        """Character - Integrity and willingness to pay"""
        risk_points = 0
        
        # Check for KYC negative flags
        kyc_flags = data.get('kyc_negative_flags', [])
        if kyc_flags:
            risk_points += 25
            self.risk_factors.append(f"KYC red flags: {', '.join(kyc_flags)}")
        
        # Check for litigation/negative flags
        negative_flags = data.get('negative_flags', [])
        if negative_flags:
            risk_points += 20
            self.risk_factors.append(f"Character risk: {', '.join(negative_flags)} mentioned")
        
        return risk_points
    
    def analyze_capacity(self, data):
        """Capacity - Ability to repay based on cash flow"""
        risk_points = 0
        
        profit_margin = self.calculate_profit_margin(data)
        if profit_margin is not None:
            if profit_margin < 5:
                risk_points += 25
                self.risk_factors.append(f"Very low profit margin: {profit_margin:.1f}%")
            elif profit_margin < 10:
                risk_points += 15
                self.risk_factors.append(f"Low profit margin: {profit_margin:.1f}%")
            elif profit_margin < 15:
                risk_points += 5
                self.risk_factors.append(f"Moderate profit margin: {profit_margin:.1f}%")
        else:
            # If no profit data available, assume moderate risk
            risk_points += 10
            self.risk_factors.append("Profit margin data not available")
        
        return risk_points
    
    def analyze_capital(self, data):
        """Capital - Financial strength and equity"""
        risk_points = 0
        
        debt_ratio = self.calculate_debt_ratio(data)
        if debt_ratio is not None:
            if debt_ratio > 80:
                risk_points += 30
                self.risk_factors.append(f"Very high debt ratio: {debt_ratio:.1f}%")
            elif debt_ratio > 60:
                risk_points += 20
                self.risk_factors.append(f"High debt ratio: {debt_ratio:.1f}%")
            elif debt_ratio > 40:
                risk_points += 10
                self.risk_factors.append(f"Moderate debt ratio: {debt_ratio:.1f}%")
            elif debt_ratio > 20:
                risk_points += 5
                self.risk_factors.append(f"Acceptable debt ratio: {debt_ratio:.1f}%")
        else:
            # If no debt data, assume moderate risk
            risk_points += 8
            self.risk_factors.append("Debt ratio data not available")
        
        return risk_points
    
    def analyze_conditions(self, data):
        """Conditions - Economic and industry factors"""
        risk_points = 0
        
        # Check for negative industry conditions
        negative_flags = data.get('negative_flags', [])
        negative_conditions = ['loss', 'decline', 'lawsuit']
        
        for condition in negative_conditions:
            if condition in negative_flags:
                risk_points += 10
                self.risk_factors.append(f"Negative condition: {condition}")
        
        return risk_points
    
    def analyze_collateral(self, data):
        """Collateral - Security for the loan (now calculates risk points)"""
        risk_points = 0
        
        positive_flags = data.get('positive_flags', [])
        collateral_keywords = ['collateral', 'security', 'guarantee', 'asset']
        collateral_types = data.get('collateral_types', [])
        
        # Lack of collateral increases risk
        if not positive_flags and not collateral_types:
            risk_points += 15
            self.risk_factors.append("No collateral security identified")
        elif len(collateral_types) < 2:
            risk_points += 5
            self.risk_factors.append("Limited collateral coverage")
        
        # Good collateral reduces risk
        for collateral_type in collateral_types:
            if collateral_type in ['land', 'property', 'building']:
                risk_points -= 5  # Reduce risk for good collateral
                self.risk_factors.append(f"Good collateral: {collateral_type}")
        
        # Collateral value assessment
        collateral_value = data.get('collateral_value', 0)
        if collateral_value > 0:
            risk_points -= 3
            self.risk_factors.append(f"Collateral value: ₹{collateral_value:,.0f}")
        
        return max(0, risk_points)  # Ensure non-negative
    
    def analyze_gst_bank_mismatch(self, data):
        """Analyze GST vs Bank statement for inconsistencies"""
        risk_points = 0
        
        gst_sales = data.get('gst_sales', 0)
        bank_deposits = data.get('bank_deposits', 0)
        circular_transactions = data.get('circular_transactions', 0)
        
        # Revenue mismatch detection
        if gst_sales > 0 and bank_deposits > 0:
            mismatch_ratio = abs(bank_deposits - gst_sales) / gst_sales
            if mismatch_ratio > 0.3:  # 30% mismatch threshold
                risk_points += 15
                self.risk_factors.append(f"GST-Bank mismatch: {mismatch_ratio*100:.1f}%")
        
        # Circular transaction detection
        if circular_transactions > 5:
            risk_points += 20
            self.risk_factors.append(f"Possible circular transactions: {circular_transactions}")
        elif circular_transactions > 2:
            risk_points += 10
            self.risk_factors.append(f"Some circular transactions detected: {circular_transactions}")
        
        return risk_points
    
    def calculate_debt_ratio(self, data):
        """Calculate debt to revenue ratio"""
        debt = data.get('debt', 0)
        revenue = data.get('revenue', 0)
        
        if revenue > 0:
            return (debt / revenue) * 100
        return None
    
    def calculate_profit_margin(self, data):
        """Calculate profit margin"""
        profit = data.get('profit', 0)
        revenue = data.get('revenue', 0)
        
        if revenue > 0:
            return (profit / revenue) * 100
        return None
    
    def generate_recommendation(self, risk_analysis, extracted_data):
        """Generate loan recommendation based on risk score"""
        score = risk_analysis['total_score']
        revenue = extracted_data.get('revenue', 0)
        
        # More realistic decision logic
        if score >= 75:
            decision = "APPROVE"
            loan_limit = revenue * 0.20 if revenue > 0 else 2000000  # 20% of revenue or 20L default
            interest_rate = "9.5%" if score >= 85 else "10.2%"
            explanation = "Strong financial profile with low risk indicators"
        elif score >= 60:
            decision = "APPROVE"
            loan_limit = revenue * 0.15 if revenue > 0 else 1500000  # 15% of revenue or 15L default
            interest_rate = "11.5%"
            explanation = "Acceptable risk profile with some monitoring required"
        elif score >= 45:
            decision = "REVIEW"
            loan_limit = revenue * 0.10 if revenue > 0 else 1000000  # 10% of revenue or 10L default
            interest_rate = "13.0%"
            explanation = "Moderate risk - requires enhanced due diligence and conditions"
        else:
            decision = "REJECT"
            loan_limit = 0
            interest_rate = "N/A"
            explanation = f"High risk profile. Key concerns: {', '.join(risk_analysis['risk_factors'][:3])}"
        
        return {
            'decision': decision,
            'recommended_limit': f"₹{loan_limit:,.0f}",
            'interest_rate': interest_rate,
            'risk_score': score,
            'explanation': explanation,
            'conditions': self.generate_conditions(decision, risk_analysis)
        }
    
    def generate_conditions(self, decision, risk_analysis):
        """Generate loan conditions based on risk factors"""
        conditions = []
        
        if decision == "APPROVE":
            if risk_analysis['debt_ratio'] and risk_analysis['debt_ratio'] > 30:
                conditions.append("Monthly financial reporting required")
            if risk_analysis['profit_margin'] and risk_analysis['profit_margin'] < 15:
                conditions.append("Quarterly business review meetings")
        
        elif decision == "REVIEW":
            conditions.extend([
                "Additional collateral required",
                "Personal guarantee from promoters",
                "Monthly cash flow monitoring"
            ])
        
        return conditions