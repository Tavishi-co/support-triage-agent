#!/usr/bin/env python3
"""
Support Triage Agent for HackerRank Orchestrate Challenge
Windows-compatible version
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, Tuple
from difflib import SequenceMatcher

class SupportTriageAgent:
    def __init__(self):
        # Load sample tickets if they exist
        self.sample_patterns = {}
        self.load_sample_tickets()
        
        # Escalation triggers (keywords that require human review)
        self.escalation_triggers = {
            'security': ['hacked', 'unauthorized', 'breach', 'stolen', 'compromised', 
                        'identity theft', 'fraud', 'scam'],
            'permission': ['restore my access', 'bypass', 'override', 'unfairly', 
                          'increase my score', 'review my answers'],
            'dangerous': ['delete all files', 'rm -rf', 'format', 'wipe'],
            'out_of_scope': ['iron man', 'actor', 'movie', 'celebrity', 'sports']
        }
        
        # Product keywords
        self.product_keywords = {
            'hackerrank': ['hackerrank', 'test', 'assessment', 'coding', 'challenge', 
                          'recruiter', 'score', 'mock interview', 'submission'],
            'claude': ['claude', 'anthropic', 'conversation', 'ai', 'model', 'bedrock',
                      'assistant'],
            'visa': ['visa', 'card', 'payment', 'transaction', 'charge', 'refund',
                    'dispute', 'fraud']
        }
    
    def load_sample_tickets(self):
        """Load sample tickets to learn patterns"""
        sample_path = Path('support_tickets/sample_support_tickets.csv')
        if sample_path.exists():
            try:
                df = pd.read_csv(sample_path)
                print(f"✅ Loaded {len(df)} sample tickets for learning")
                
                # Store patterns from samples
                for _, row in df.iterrows():
                    issue = str(row.get('Issue', row.get('issue', ''))).lower()
                    if len(issue) > 10:  # Only store meaningful issues
                        self.sample_patterns[issue[:100]] = {
                            'status': row.get('Status', row.get('status', 'replied')),
                            'product_area': row.get('Product Area', row.get('product_area', 'general')),
                            'response': row.get('Response', row.get('response', '')),
                            'request_type': row.get('Request Type', row.get('request_type', 'product_issue'))
                        }
            except Exception as e:
                print(f"⚠️ Could not load samples: {e}")
    
    def classify_product(self, text: str, provided_company: str) -> str:
        """Determine which product domain this belongs to"""
        # If company is explicitly provided
        if provided_company and provided_company != 'None' and provided_company != 'nan':
            return provided_company.lower()
        
        text_lower = text.lower()
        
        # Check keywords
        for product, keywords in self.product_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return product
        
        return 'unknown'
    
    def check_escalation_needed(self, text: str) -> Tuple[bool, str]:
        """Determine if this ticket should be escalated"""
        text_lower = text.lower()
        
        for category, keywords in self.escalation_triggers.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True, f"{category}: '{keyword}'"
        
        return False, "safe"
    
    def find_similar_pattern(self, text: str) -> Dict:
        """Find if any sample pattern matches this issue"""
        text_lower = text.lower()
        
        for pattern, result in self.sample_patterns.items():
            # Check if pattern is contained in the issue
            if pattern in text_lower or text_lower in pattern:
                # Calculate similarity
                similarity = SequenceMatcher(None, text_lower[:50], pattern[:50]).ratio()
                if similarity > 0.6:  # High confidence match
                    return result
        
        return None
    
    def process_ticket(self, issue: str, subject: str, company: str) -> Dict:
        """Main logic to process a single ticket"""
        
        # Combine subject and issue for better context
        full_text = f"{subject} {issue}".lower()
        
        # Skip empty tickets
        if not full_text or len(full_text) < 3:
            return {
                'status': 'escalated',
                'product_area': 'unknown',
                'response': 'Unable to process empty ticket.',
                'justification': 'No content to analyze',
                'request_type': 'invalid'
            }
        
        # Check for pattern match from samples
        pattern_match = self.find_similar_pattern(full_text)
        if pattern_match:
            return pattern_match
        
        # Check if escalation is needed
        needs_escalation, reason = self.check_escalation_needed(full_text)
        
        if needs_escalation:
            return {
                'status': 'escalated',
                'product_area': self.classify_product(full_text, company),
                'response': 'This issue requires human review due to sensitive content.',
                'justification': f'Escalated: {reason}',
                'request_type': 'product_issue'
            }
        
        # Classify product
        product = self.classify_product(full_text, company)
        
        # Generate response based on product
        if product == 'hackerrank':
            return {
                'status': 'replied',
                'product_area': 'general_support',
                'response': 'Please visit support.hackerrank.com for assistance with HackerRank issues. Check your test settings and candidate management in your dashboard.',
                'justification': 'Routed to HackerRank support domain',
                'request_type': self.determine_request_type(full_text)
            }
        elif product == 'claude':
            return {
                'status': 'replied',
                'product_area': 'general_support',
                'response': 'For Claude assistance, please refer to help.claude.com or check the Anthropic documentation center for detailed guides.',
                'justification': 'Routed to Claude support domain',
                'request_type': self.determine_request_type(full_text)
            }
        elif product == 'visa':
            # Visa issues often need escalation due to financial sensitivity
            return {
                'status': 'escalated',
                'product_area': 'card_services',
                'response': 'For Visa card issues, please call the customer service number on the back of your card for immediate assistance.',
                'justification': 'Financial matters require human handling',
                'request_type': 'product_issue'
            }
        else:
            # Check if completely out of scope
            if any(word in full_text for word in ['movie', 'actor', 'celebrity', 'song', 'book']):
                return {
                    'status': 'replied',
                    'product_area': 'out_of_scope',
                    'response': "I apologize, but I can only help with HackerRank, Claude, and Visa-related issues. Your question appears to be outside these domains.",
                    'justification': 'Question unrelated to supported products',
                    'request_type': 'invalid'
                }
            
            return {
                'status': 'escalated',
                'product_area': 'unknown',
                'response': 'Unable to determine which product this relates to. Please specify if this is about HackerRank, Claude, or Visa.',
                'justification': 'Could not classify to any supported domain',
                'request_type': 'invalid'
            }
    
    def determine_request_type(self, text: str) -> str:
        """Classify the type of request"""
        if any(word in text for word in ['bug', 'error', 'crash', 'not working', 'broken', 'failing']):
            return 'bug'
        elif any(word in text for word in ['feature', 'suggest', 'improve', 'add', 'enhance']):
            return 'feature_request'
        elif any(word in text for word in ['spam', 'test test', 'ignore', 'junk']):
            return 'invalid'
        else:
            return 'product_issue'

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 HACKERRANK ORCHESTRATE - SUPPORT TRIAGE AGENT")
    print("=" * 60)
    
    # Define paths (Windows style)
    tickets_path = Path('support_tickets/support_tickets.csv')
    output_path = Path('support_tickets/output.csv')
    
    # Check if tickets file exists
    if not tickets_path.exists():
        print(f"\n❌ Error: Cannot find {tickets_path}")
        print("Make sure you're in the correct directory.")
        print(f"Current directory: {Path.cwd()}")
        exit(1)
    
    # Load tickets
    print(f"\n📂 Loading tickets...")
    try:
        tickets_df = pd.read_csv(tickets_path)
        print(f"✅ Loaded {len(tickets_df)} tickets")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        exit(1)
    
    # Initialize agent
    print("🚀 Initializing agent...")
    agent = SupportTriageAgent()
    
    # Process tickets
    results = []
    print("\n📝 Processing tickets...\n")
    
    for idx, row in tickets_df.iterrows():
        # Handle different column name possibilities
        issue_col = 'Issue' if 'Issue' in tickets_df.columns else 'issue'
        subject_col = 'Subject' if 'Subject' in tickets_df.columns else 'subject'
        company_col = 'Company' if 'Company' in tickets_df.columns else 'company'
        
        issue = str(row[issue_col]) if pd.notna(row[issue_col]) else ""
        subject = str(row[subject_col]) if pd.notna(row[subject_col]) else ""
        company = str(row[company_col]) if pd.notna(row[company_col]) else "None"
        
        # Skip if issue is empty
        if not issue or issue == 'nan':
            print(f"  ⚠️ Ticket {idx + 1}: Empty issue, skipping")
            continue
        
        print(f"  Ticket {idx + 1}: {issue[:60]}...")
        
        # Process
        result = agent.process_ticket(issue, subject, company)
        results.append(result)
        
        status_icon = "✅" if result['status'] == 'replied' else "⚠️"
        print(f"    {status_icon} {result['status'].upper()} | {result['product_area']}")
    
    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Results saved to {output_path}")
    print("\n📊 SUMMARY:")
    print(f"   Total processed: {len(results)}")
    print(f"   Replied: {sum(1 for r in results if r['status'] == 'replied')}")
    print(f"   Escalated: {sum(1 for r in results if r['status'] == 'escalated')}")
    print("\n📋 Request Types:")
    for req_type in output_df['request_type'].unique():
        count = sum(1 for r in results if r['request_type'] == req_type)
        print(f"   {req_type}: {count}")
        print("=" * 60)