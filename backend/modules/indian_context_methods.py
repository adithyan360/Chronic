import re
from datetime import datetime

# Indian document patterns
indian_patterns = {
    'gstr_2a': r'gstr[\s-]*2a|input tax credit|itc',
    'gstr_3b': r'gstr[\s-]*3b|monthly return|tax liability',
    'cibil_commercial': r'cibil|commercial credit report|credit information bureau',
    'pan': r'[A-Z]{5}[0-9]{4}[A-Z]{1}',
    'gstin': r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}',
    'cin': r'[UL][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}'
}

def classify_indian_document(text):
    """Classify Indian financial documents"""
    text_lower = text.lower()
    
    if re.search(indian_patterns['gstr_2a'], text):
        return 'GSTR-2A (Input Tax Credit)'
    elif re.search(indian_patterns['gstr_3b'], text):
        return 'GSTR-3B (Monthly Return)'
    elif re.search(indian_patterns['cibil_commercial'], text):
        return 'CIBIL Commercial Credit Report'
    elif 'annual report' in text_lower:
        return 'Annual Report'
    elif 'financial statement' in text_lower:
        return 'Financial Statement'
    else:
        return 'Unknown Document Type'

def extract_indian_identifiers(text):
    """Extract Indian regulatory identifiers"""
    extracted = {}
    
    # Extract PAN
    pan_match = re.search(indian_patterns['pan'], text)
    if pan_match:
        extracted['pan'] = pan_match.group(0)
    
    # Extract GSTIN
    gstin_match = re.search(indian_patterns['gstin'], text)
    if gstin_match:
        extracted['gstin'] = gstin_match.group(0)
    
    # Extract CIN
    cin_match = re.search(indian_patterns['cin'], text)
    if cin_match:
        extracted['cin'] = cin_match.group(0)
    
    return extracted

def extract_indian_financial_figures(text):
    """Extract financial figures with Indian number formats (lakhs/crores)"""
    extracted = {}
    
    # Indian number patterns with lakhs/crores
    patterns = {
        'revenue': r'(?:revenue|total income|sales|turnover|कुल आय|बिक्री)[\s\w]*?[\s:₹$]+([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|lac|करोड़|लाख)?',
        'profit': r'(?:net profit|pat|profit after tax|शुद्ध लाभ)[\s\w]*?[\s:₹$]+([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|lac|करोड़|लाख)?',
        'debt': r'(?:total debt|borrowings|loans|कुल ऋण|उधार)[\s\w]*?[\s:₹$]+([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|lac|करोड़|लाख)?',
        'ebitda_margin': r'(?:ebitda margin|operating margin|परिचालन मार्जिन)[\s\w]*?[\s:]+([\d.]+)%?'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text.lower())
        if match:
            value_str = match.group(1).replace(',', '')
            try:
                if key == 'ebitda_margin':
                    extracted[key] = float(value_str)
                else:
                    value = float(value_str)
                    # Convert based on Indian number system
                    if 'crore' in text.lower() or 'करोड़' in text.lower():
                        value *= 10000000  # 1 crore = 10 million
                    elif 'lakh' in text.lower() or 'लाख' in text.lower():
                        value *= 100000    # 1 lakh = 100 thousand
                    extracted[key] = int(value)
            except ValueError:
                pass
    
    return extracted

def simulate_ocr_extraction(filepath):
    """Simulate OCR extraction for scanned PDFs"""
    # In production, would use Tesseract OCR or AWS Textract
    # For prototype, return simulated extracted text
    return """
    ABC Manufacturing Pvt Ltd
    Annual Report 2023-24
    Revenue: ₹50 Crore
    Net Profit: ₹8 Crore
    Total Debt: ₹15 Crore
    GSTIN: 27AABCU9603R1ZM
    PAN: AABCU9603R
    Credit Rating: BBB+ (CRISIL)
    """

def extract_kyc_data(text):
    """Extract KYC data with Indian context"""
    extracted = {}
    
    # Extract director information
    director_match = re.search(r'director[s]?[:\s]+([a-zA-Z\s]+)', text.lower())
    if director_match:
        extracted['director_name'] = director_match.group(1).strip().title()
    
    # Check for negative flags in KYC
    kyc_flags = ['criminal', 'fraud', 'default', 'bankruptcy', 'wilful defaulter', 'suit filed']
    extracted['kyc_negative_flags'] = [flag for flag in kyc_flags if flag in text.lower()]
    
    # Extract DIN (Director Identification Number)
    din_match = re.search(r'DIN[:\s]*([0-9]{8})', text)
    if din_match:
        extracted['din'] = din_match.group(1)
    
    return extracted

def extract_collateral_data(text):
    """Extract collateral data with Indian context"""
    extracted = {}
    
    # Extract collateral information
    collateral_keywords = ['property', 'land', 'building', 'machinery', 'equipment', 'vehicle', 'plot', 'flat']
    extracted['collateral_types'] = [keyword for keyword in collateral_keywords if keyword in text.lower()]
    
    # Extract collateral value with Indian currency
    value_match = re.search(r'value[:\s]+[₹$]?([\d,]+(?:\.\d+)?)\s*(?:crore|cr|lakh|lac)?', text.lower())
    if value_match:
        try:
            value = float(value_match.group(1).replace(',', ''))
            if 'crore' in text.lower():
                value *= 10000000
            elif 'lakh' in text.lower():
                value *= 100000
            extracted['collateral_value'] = value
        except ValueError:
            pass
    
    return extracted

def perform_external_research(company_name):
    """Simulate external research for Indian companies"""
    # In production, would integrate with:
    # - MCA (Ministry of Corporate Affairs) API
    # - News APIs for Indian business news
    # - RBI databases
    # - Stock exchange data
    
    research_data = {
        'mca_status': 'Active',
        'recent_news': [
            f'{company_name} reports strong Q4 results',
            f'Regulatory compliance update for {company_name}',
            f'{company_name} expands operations in South India'
        ],
        'regulatory_filings': [
            'Annual Return filed on time',
            'Board Resolution for loan approval',
            'Compliance certificate submitted'
        ],
        'market_sentiment': 'Positive',
        'industry_outlook': 'Stable growth expected',
        'research_timestamp': datetime.now().isoformat()
    }
    
    return research_data