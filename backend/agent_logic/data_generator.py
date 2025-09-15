"""
Data Generator Module for ValtricAI
Generates structured data from AI responses (CSV, JSON, Charts)
"""

import json
import csv
import io
import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import pandas as pd
from datetime import datetime

class DataType(str, Enum):
    """Types of structured data we can generate"""
    TABLE = "table"
    JSON = "json"
    CHART = "chart"
    SWOT = "swot"
    FINANCIAL = "financial"
    COMPARISON = "comparison"
    TIMELINE = "timeline"
    TEXT = "text"

class DataGenerator:
    """Generates structured data from AI responses"""
    
    def __init__(self):
        self.patterns = {
            'csv': re.compile(r'^[A-Za-z\s,]+\n[\w\s,.-]+', re.MULTILINE),
            'json': re.compile(r'^\s*\{[\s\S]*\}\s*$'),
            'table': re.compile(r'\|.*\|.*\|'),
            'financial': re.compile(r'(revenue|profit|expense|year|quarter)', re.IGNORECASE),
            'swot': re.compile(r'(strength|weakness|opportunity|threat)', re.IGNORECASE),
        }
    
    def detect_data_type(self, text: str) -> DataType:
        """Detect what type of data the AI generated"""
        text_lower = text.lower()
        
        # Check for specific data patterns
        if self.patterns['json'].match(text.strip()):
            return DataType.JSON
        elif self.patterns['csv'].match(text):
            return DataType.TABLE
        elif self.patterns['table'].match(text):
            return DataType.TABLE
        elif 'swot' in text_lower and self.patterns['swot'].search(text):
            return DataType.SWOT
        elif self.patterns['financial'].search(text) and any(char.isdigit() for char in text):
            return DataType.FINANCIAL
        else:
            return DataType.TEXT
    
    def parse_csv_data(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse CSV data from AI response"""
        try:
            # Find CSV-like content
            lines = text.strip().split('\n')
            csv_lines = []
            
            # Look for lines with commas that look like CSV
            for line in lines:
                if ',' in line:
                    # Skip lines that are clearly not CSV (too few or too many parts)
                    parts = line.split(',')
                    if 2 <= len(parts) <= 10:  # Reasonable number of columns
                        # Check if it looks like a header or data row
                        if any(part.strip().replace('%', '').replace('$', '').replace('-', '').isdigit() 
                              for part in parts) or any(keyword in line.lower() 
                              for keyword in ['year', 'revenue', 'profit', 'quarter']):
                            csv_lines.append(line.strip())
            
            if len(csv_lines) < 2:
                return None
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO('\n'.join(csv_lines)))
            data = list(reader)
            
            # Validate that we have actual data
            if data and len(data) > 0 and len(data[0]) > 1:
                return {
                    'type': DataType.TABLE,
                    'headers': list(data[0].keys()),
                    'rows': data,
                    'row_count': len(data),
                    'format': 'csv'
                }
        except Exception as e:
            print(f"CSV parsing error: {e}")
        return None
    
    def parse_json_data(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON data from AI response"""
        try:
            # First try to match complete JSON pattern
            json_match = self.patterns['json'].search(text.strip())
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                # Extract JSON block from mixed content
                lines = text.split('\n')
                json_lines = []
                in_json = False
                brace_count = 0
                
                for line in lines:
                    if '{' in line and not in_json:
                        in_json = True
                        json_lines = [line]
                        brace_count = line.count('{') - line.count('}')
                    elif in_json:
                        json_lines.append(line)
                        brace_count += line.count('{') - line.count('}')
                        if brace_count == 0:
                            break
                
                if not json_lines:
                    return None
                    
                json_str = '\n'.join(json_lines)
                data = json.loads(json_str)
            
            # Detect specific JSON types
            if all(key in data for key in ['strengths', 'weaknesses', 'opportunities', 'threats']):
                return {
                    'type': DataType.SWOT,
                    'data': data,
                    'format': 'json'
                }
            else:
                return {
                    'type': DataType.JSON,
                    'data': data,
                    'format': 'json'
                }
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
        except Exception as e:
            print(f"JSON extraction error: {e}")
        return None
    
    def parse_markdown_table(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse markdown table from AI response"""
        try:
            lines = text.strip().split('\n')
            table_lines = [line for line in lines if '|' in line]
            
            if len(table_lines) >= 3:  # Header + separator + at least one row
                # Parse header
                header_line = table_lines[0]
                headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
                
                # Parse rows (skip separator line)
                rows = []
                for line in table_lines[2:]:
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(cells) == len(headers):
                        row_dict = dict(zip(headers, cells))
                        rows.append(row_dict)
                
                if rows:
                    return {
                        'type': DataType.TABLE,
                        'headers': headers,
                        'rows': rows,
                        'row_count': len(rows),
                        'format': 'markdown'
                    }
        except Exception as e:
            print(f"Markdown table parsing error: {e}")
        return None
    
    def generate_financial_projection(self, 
                                     start_revenue: float = 100000,
                                     growth_rate: float = 0.3,
                                     years: int = 5) -> Dict[str, Any]:
        """Generate a financial projection table"""
        data = []
        revenue = start_revenue
        
        for year in range(1, years + 1):
            expenses = revenue * 0.7  # 70% expense ratio
            profit = revenue - expenses
            ebitda = profit * 1.2  # Simplified EBITDA
            
            data.append({
                'Year': f'Year {year}',
                'Revenue': round(revenue, 2),
                'Expenses': round(expenses, 2),
                'Profit': round(profit, 2),
                'EBITDA': round(ebitda, 2),
                'Growth %': f'{growth_rate * 100:.0f}%' if year > 1 else '-'
            })
            
            revenue *= (1 + growth_rate)
        
        return {
            'type': DataType.FINANCIAL,
            'headers': ['Year', 'Revenue', 'Expenses', 'Profit', 'EBITDA', 'Growth %'],
            'rows': data,
            'row_count': len(data),
            'format': 'generated',
            'metadata': {
                'start_revenue': start_revenue,
                'growth_rate': growth_rate,
                'years': years
            }
        }
    
    def generate_swot_analysis(self, business_type: str = "SaaS") -> Dict[str, Any]:
        """Generate a SWOT analysis structure"""
        swot_data = {
            'strengths': [
                {'item': 'Strong technical team', 'priority': 5},
                {'item': 'Innovative product features', 'priority': 4},
                {'item': 'Low operational costs', 'priority': 3}
            ],
            'weaknesses': [
                {'item': 'Limited brand recognition', 'priority': 5},
                {'item': 'Small marketing budget', 'priority': 4},
                {'item': 'Limited geographic presence', 'priority': 3}
            ],
            'opportunities': [
                {'item': 'Growing market demand', 'priority': 5},
                {'item': 'Partnership opportunities', 'priority': 4},
                {'item': 'International expansion', 'priority': 3}
            ],
            'threats': [
                {'item': 'Established competitors', 'priority': 5},
                {'item': 'Economic uncertainty', 'priority': 4},
                {'item': 'Regulatory changes', 'priority': 3}
            ]
        }
        
        return {
            'type': DataType.SWOT,
            'data': swot_data,
            'format': 'json',
            'metadata': {
                'business_type': business_type,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def generate_chart_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart.js compatible configuration"""
        if data['type'] == DataType.FINANCIAL:
            # Line chart for financial data
            labels = [row['Year'] for row in data['rows']]
            revenue_data = [row['Revenue'] for row in data['rows']]
            profit_data = [row['Profit'] for row in data['rows']]
            
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Revenue',
                            'data': revenue_data,
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                        },
                        {
                            'label': 'Profit',
                            'data': profit_data,
                            'borderColor': 'rgb(255, 99, 132)',
                            'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Financial Projection'
                        }
                    }
                }
            }
        elif data['type'] == DataType.SWOT:
            # Radar chart for SWOT
            categories = ['Strengths', 'Weaknesses', 'Opportunities', 'Threats']
            values = [
                len(data['data']['strengths']),
                len(data['data']['weaknesses']),
                len(data['data']['opportunities']),
                len(data['data']['threats'])
            ]
            
            return {
                'type': 'radar',
                'data': {
                    'labels': categories,
                    'datasets': [{
                        'label': 'SWOT Analysis',
                        'data': values,
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': 'rgb(54, 162, 235)',
                        'pointBackgroundColor': 'rgb(54, 162, 235)'
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'SWOT Analysis Overview'
                        }
                    }
                }
            }
        
        return {}
    
    def process_ai_response(self, text: str) -> Dict[str, Any]:
        """Main method to process AI response and extract structured data"""
        result = {
            'original_text': text,
            'data_type': DataType.TEXT,
            'structured_data': None,
            'chart_config': None,
            'exportable': False
        }
        
        # Detect data type
        data_type = self.detect_data_type(text)
        result['data_type'] = data_type
        
        # Parse based on type
        if data_type == DataType.JSON or data_type == DataType.SWOT:
            parsed = self.parse_json_data(text)
            if parsed:
                result['structured_data'] = parsed
                result['chart_config'] = self.generate_chart_config(parsed)
                result['exportable'] = True
        
        elif data_type == DataType.TABLE or data_type == DataType.FINANCIAL:
            # Try CSV first
            parsed = self.parse_csv_data(text)
            if not parsed:
                # Try markdown table
                parsed = self.parse_markdown_table(text)
            
            if parsed:
                result['structured_data'] = parsed
                if data_type == DataType.FINANCIAL:
                    result['chart_config'] = self.generate_chart_config(parsed)
                result['exportable'] = True
        
        return result

# Global instance
data_generator = DataGenerator()