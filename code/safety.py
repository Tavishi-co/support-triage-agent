"""
safety.py - Risk detection and escalation logic
"""

class SafetyChecker:
    """Detects high-risk tickets that need human review"""
    
    def __init__(self):
        self.high_risk_keywords = {
            'security': ['hacked', 'unauthorized', 'breach', 'stolen', 'compromised', 
                'identity theft', 'security vulnerability', 'bug bounty'],
            'fraud': ['fraud', 'scam', 'phishing', 'fake', 'unauthorized transaction', 
              'identity stolen'],
            'legal': ['lawsuit', 'attorney', 'legal action', 'court', 'sue', 'lawyer', 
              'illegal'],
            'access': ['restore my access', 'bypass', 'override', 'even though i am not',
               'i am not the owner', 'no permission'],
            'dangerous': ['delete all files', 'rm -rf', 'format drive', 'wipe system',
                  'delete everything'],
            'financial': ['urgent cash', 'need money now', 'refund today', 'immediate refund']  # ADD THIS LINE
    }
        
        self.out_of_scope = [
            'iron man', 'actor', 'movie', 'celebrity', 'sports team',
            'what is the capital', 'who won', 'song lyrics'
        ]
    
    def check(self, text: str) -> dict:
        """
        Returns: {
            'should_escalate': bool,
            'reason': str,
            'risk_level': 'high'|'medium'|'low'
        }
        """
        text_lower = text.lower()
        
        # Check high-risk keywords
        for category, keywords in self.high_risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        'should_escalate': True,
                        'reason': f"High risk: {category} - '{keyword}' detected",
                        'risk_level': 'high'
                    }
        
        # Check out of scope
        for word in self.out_of_scope:
            if word in text_lower:
                return {
                    'should_escalate': False,  # Can reply as invalid
                    'reason': f"Out of scope: unrelated to support domains",
                    'risk_level': 'low'
                }
        
        return {
            'should_escalate': False,
            'reason': 'Safe to answer',
            'risk_level': 'low'
        }