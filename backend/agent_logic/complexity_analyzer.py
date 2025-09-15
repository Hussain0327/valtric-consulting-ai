"""
Query Complexity Analyzer for ValtricAI Consulting Agent

Analyzes incoming queries to determine complexity level and appropriate model routing:
- Low complexity (0.0-0.4): Simple greetings, acknowledgments → gpt-5-mini
- Medium complexity (0.4-0.7): Basic questions, simple requests → gpt-5-mini  
- High complexity (0.7-1.0): Strategic analysis, frameworks, complex reasoning → o4-mini

Based on ValtricAI's L0-L3 classification system from N8N template.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IntentLevel(str, Enum):
    """ValtricAI Intent Classification Levels"""
    L0_GREETING = "L0"        # Greeting, small talk
    L1_VAGUE = "L1"          # Vague intent, needs clarification  
    L2_CONCRETE = "L2"       # Concrete question, specific need
    L3_STRATEGIC = "L3"      # Deep strategic analysis
    DATA_DOCS = "DATA"       # Document/data analysis


@dataclass
class ComplexityAnalysis:
    """Complexity analysis results"""
    score: float              # 0.0-1.0 complexity score
    level: IntentLevel       # L0-L3 classification
    reasoning: str           # Why this classification
    keywords_found: List[str] # Relevant keywords detected
    requires_reasoning: bool  # Should use o4-mini vs gpt-5-mini


class ComplexityAnalyzer:
    """Analyzes query complexity for intelligent model routing"""
    
    def __init__(self):
        # L0 - Greeting/Small Talk Patterns
        self.l0_patterns = [
            r"^(hi|hello|hey|good morning|good afternoon|good evening)",
            r"^(how are you|what.*up|how.*going)",
            r"^(thanks|thank you|thx|appreciate)",
            r"^(yes|no|ok|okay|cool|got it|understood|sure)",
            r"^(bye|goodbye|see you|talk later)",
            r"^(sorry|my bad|oops)"
        ]
        
        # L1 - Vague Intent Keywords
        self.l1_keywords = [
            "help", "advice", "guidance", "suggestions", "ideas",
            "what should i", "how can i", "need help with",
            "can you help", "looking for", "want to know"
        ]
        
        # L2 - Concrete Business Keywords  
        self.l2_keywords = [
            "pricing", "revenue", "costs", "expenses", "budget", "forecast",
            "hiring", "recruitment", "team", "staff", "employees",
            "marketing", "sales", "customers", "clients", "leads",
            "operations", "processes", "workflow", "efficiency", 
            "tools", "software", "systems", "technology", "crm"
        ]
        
        # L3 - Strategic/Complex Keywords
        self.l3_keywords = [
            # Strategic Planning
            "strategy", "strategic", "vision", "mission", "objectives", "goals",
            "roadmap", "planning", "long-term", "short-term",
            
            # Frameworks
            "swot", "porter", "mckinsey", "framework", "analysis", "assessment",
            "competitive analysis", "market analysis", "business model",
            
            # Financial/Investment
            "roi", "investment", "valuation", "financial", "business case",
            "profit", "margin", "cash flow", "funding", "capital",
            
            # Strategic Decisions
            "acquisition", "merger", "partnership", "expansion", "scaling",
            "restructure", "optimization", "transformation", "pivot",
            
            # Risk & Opportunities
            "risk", "threat", "opportunity", "competitive", "advantage",
            "market position", "differentiation", "value proposition"
        ]
        
        # Data/Document Analysis Keywords
        self.data_keywords = [
            "analyze", "report", "data", "spreadsheet", "csv", "excel",
            "document", "file", "attachment", "chart", "graph", "metrics",
            "kpi", "dashboard", "analytics", "trends", "insights"
        ]
        
        # Complexity modifiers
        self.complexity_boosters = [
            r"compare.*options", r"evaluate.*alternatives", r"what.*best",
            r"should.*or.*should", r"pros.*cons", r"trade.*off",
            r"multiple.*factors", r"complex.*situation", r"several.*issues"
        ]
        
        # Question complexity indicators
        self.complex_question_patterns = [
            r"why.*and.*how", r"what.*if.*then", r"how.*would.*affect",
            r"what.*impact.*on", r"which.*better.*for", r"when.*should.*vs"
        ]

    def analyze_complexity(
        self, 
        message: str, 
        context: str = "",
        conversation_history: Optional[List[Dict]] = None
    ) -> float:
        """
        Analyze query complexity and return score (0.0-1.0)
        
        Args:
            message: User input message
            context: Additional context 
            conversation_history: Previous conversation turns
            
        Returns:
            Complexity score (0.0-1.0)
        """
        analysis = self.get_detailed_analysis(message, context, conversation_history)
        return analysis.score

    def get_detailed_analysis(
        self, 
        message: str, 
        context: str = "",
        conversation_history: Optional[List[Dict]] = None
    ) -> ComplexityAnalysis:
        """Get detailed complexity analysis with reasoning"""
        
        message_lower = message.lower()
        context_lower = context.lower() if context else ""
        combined_text = f"{message_lower} {context_lower}".strip()
        
        # Initialize scoring
        score = 0.0
        keywords_found = []
        reasoning_parts = []
        
        # L0 Check - Greeting/Small Talk
        l0_matches = self._check_patterns(message_lower, self.l0_patterns)
        if l0_matches:
            return ComplexityAnalysis(
                score=0.1,
                level=IntentLevel.L0_GREETING,
                reasoning=f"Greeting/small talk pattern detected: {l0_matches[0]}",
                keywords_found=[],
                requires_reasoning=False
            )
        
        # Check for acknowledgments (very short responses)
        if len(message.split()) <= 3 and any(word in message_lower for word in ["yes", "no", "ok", "thanks", "sure"]):
            return ComplexityAnalysis(
                score=0.05,
                level=IntentLevel.L0_GREETING,
                reasoning="Short acknowledgment",
                keywords_found=[],
                requires_reasoning=False
            )
        
        # Keyword Analysis
        l1_found = self._find_keywords(combined_text, self.l1_keywords)
        l2_found = self._find_keywords(combined_text, self.l2_keywords)  
        l3_found = self._find_keywords(combined_text, self.l3_keywords)
        data_found = self._find_keywords(combined_text, self.data_keywords)
        
        keywords_found = l1_found + l2_found + l3_found + data_found
        
        # Base scoring
        if data_found:
            score += 0.8  # Data analysis is complex
            reasoning_parts.append(f"Data analysis keywords: {data_found}")
        
        if l3_found:
            score += 0.7  # Strategic keywords
            reasoning_parts.append(f"Strategic keywords: {l3_found}")
        
        if l2_found:
            score += 0.4  # Business keywords
            reasoning_parts.append(f"Business keywords: {l2_found}")
            
        if l1_found:
            score += 0.2  # Vague intent
            reasoning_parts.append(f"Help-seeking keywords: {l1_found}")
        
        # Length-based complexity
        word_count = len(message.split())
        if word_count > 50:
            score += 0.3
            reasoning_parts.append(f"Long query ({word_count} words)")
        elif word_count > 25:
            score += 0.2
            reasoning_parts.append(f"Medium query ({word_count} words)")
        
        # Question complexity
        question_marks = message.count("?")
        if question_marks > 1:
            score += 0.2
            reasoning_parts.append(f"Multiple questions ({question_marks})")
        
        # Complex patterns
        complex_patterns = self._check_patterns(combined_text, self.complexity_boosters)
        if complex_patterns:
            score += 0.3
            reasoning_parts.append(f"Complex patterns: {complex_patterns}")
            
        question_patterns = self._check_patterns(combined_text, self.complex_question_patterns)
        if question_patterns:
            score += 0.25
            reasoning_parts.append(f"Complex questions: {question_patterns}")
        
        # Context considerations
        if conversation_history and len(conversation_history) > 3:
            score += 0.1  # Multi-turn conversations tend to be more complex
            reasoning_parts.append("Multi-turn conversation context")
        
        # Cap the score
        score = min(1.0, score)
        
        # Determine level and requirements
        if score <= 0.15:
            level = IntentLevel.L0_GREETING
            requires_reasoning = False
        elif score <= 0.4:
            level = IntentLevel.L1_VAGUE
            requires_reasoning = False
        elif score <= 0.65:
            level = IntentLevel.L2_CONCRETE  
            requires_reasoning = False
        else:
            if data_found:
                level = IntentLevel.DATA_DOCS
            else:
                level = IntentLevel.L3_STRATEGIC
            requires_reasoning = True
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Basic query analysis"
        
        return ComplexityAnalysis(
            score=score,
            level=level,
            reasoning=reasoning,
            keywords_found=keywords_found,
            requires_reasoning=requires_reasoning
        )

    def _check_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Check text against regex patterns"""
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return matches

    def _find_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find keywords in text"""
        found = []
        for keyword in keywords:
            if keyword in text:
                found.append(keyword)
        return found

    def should_use_reasoning_model(
        self, 
        message: str, 
        context: str = "",
        threshold: float = 0.6
    ) -> bool:
        """Determine if query should use reasoning model (o4-mini)"""
        analysis = self.get_detailed_analysis(message, context)
        return analysis.score >= threshold or analysis.requires_reasoning

    def classify_intent_level(self, message: str, context: str = "") -> IntentLevel:
        """Classify message according to ValtricAI L0-L3 system"""
        analysis = self.get_detailed_analysis(message, context)
        return analysis.level


# Global complexity analyzer instance
complexity_analyzer = ComplexityAnalyzer()