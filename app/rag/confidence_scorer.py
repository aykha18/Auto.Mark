"""
Confidence Scoring for RAG Responses
Evaluates the quality and reliability of generated answers
"""

import logging
from typing import Dict, Any, List

try:
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGConfidenceScorer:
    """Scores confidence in RAG-generated answers based on multiple factors"""

    def __init__(self):
        self.confidence_weights = {
            'relevance_score': 0.3,
            'document_count': 0.2,
            'semantic_similarity': 0.25,
            'source_authority': 0.15,
            'answer_consistency': 0.1
        }

    def score_response(self, question: str, retrieved_docs: List[Document], response: str) -> Dict[str, Any]:
        """Calculate comprehensive confidence score for RAG response"""

        if not LANGCHAIN_AVAILABLE:
            return {"score": 0.5, "level": "medium", "error": "LangChain not available"}

        try:
            # Calculate individual factors
            relevance_score = self._calculate_relevance_score(question, retrieved_docs)
            doc_count_score = self._calculate_document_count_score(retrieved_docs)
            semantic_score = self._calculate_semantic_similarity(question, retrieved_docs)
            authority_score = self._calculate_source_authority(retrieved_docs)
            consistency_score = self._calculate_answer_consistency(response, retrieved_docs)

            # Calculate weighted confidence score
            confidence_score = (
                relevance_score * self.confidence_weights['relevance_score'] +
                doc_count_score * self.confidence_weights['document_count'] +
                semantic_score * self.confidence_weights['semantic_similarity'] +
                authority_score * self.confidence_weights['source_authority'] +
                consistency_score * self.confidence_weights['answer_consistency']
            )

            # Ensure score is between 0 and 1
            confidence_score = max(0.0, min(1.0, confidence_score))

            return {
                'score': round(confidence_score, 3),
                'level': self._get_confidence_level(confidence_score),
                'factors': {
                    'relevance_score': round(relevance_score, 3),
                    'document_count': round(doc_count_score, 3),
                    'semantic_similarity': round(semantic_score, 3),
                    'source_authority': round(authority_score, 3),
                    'answer_consistency': round(consistency_score, 3)
                },
                'explanation': self._generate_explanation(confidence_score, retrieved_docs)
            }

        except Exception as e:
            logger.error(f"Confidence scoring failed: {e}")
            return {
                'score': 0.0,
                'level': 'low',
                'error': str(e),
                'factors': {}
            }

    def _calculate_relevance_score(self, question: str, docs: List[Document]) -> float:
        """Calculate relevance based on keyword overlap and context matching"""
        if not docs:
            return 0.0

        question_lower = question.lower()
        question_words = set(question_lower.split())

        total_relevance = 0.0

        for doc in docs:
            doc_content = doc.page_content.lower()
            doc_words = set(doc_content.split())

            # Calculate word overlap
            overlap = len(question_words.intersection(doc_words))
            if question_words:
                overlap_ratio = overlap / len(question_words)
            else:
                overlap_ratio = 0.0

            # Calculate context relevance (check for marketing-specific terms)
            marketing_terms = ['marketing', 'advertising', 'content', 'strategy', 'campaign', 'audience', 'conversion']
            marketing_matches = sum(1 for term in marketing_terms if term in doc_content)
            context_bonus = min(0.2, marketing_matches * 0.05)  # Up to 0.2 bonus

            doc_relevance = min(1.0, overlap_ratio + context_bonus)
            total_relevance += doc_relevance

        # Average relevance across documents
        avg_relevance = total_relevance / len(docs)

        # Boost score for multiple relevant documents
        if len(docs) >= 3:
            avg_relevance = min(1.0, avg_relevance * 1.1)

        return avg_relevance

    def _calculate_document_count_score(self, docs: List[Document]) -> float:
        """Score based on number of retrieved documents"""
        count = len(docs)

        if count == 0:
            return 0.0
        elif count == 1:
            return 0.3  # Low confidence with single source
        elif count == 2:
            return 0.6  # Medium confidence
        elif count <= 5:
            return 0.9  # High confidence with multiple sources
        else:
            return 1.0  # Very high confidence

    def _calculate_semantic_similarity(self, question: str, docs: List[Document]) -> float:
        """Calculate semantic similarity (simplified version)"""
        # In a production system, this would use embeddings to calculate
        # cosine similarity between question and document embeddings
        # For now, use a heuristic based on content overlap

        if not docs:
            return 0.0

        # Simple heuristic: check for conceptual matches
        question_concepts = self._extract_concepts(question)
        total_similarity = 0.0

        for doc in docs:
            doc_concepts = self._extract_concepts(doc.page_content)
            concept_overlap = len(question_concepts.intersection(doc_concepts))
            similarity = min(1.0, concept_overlap / max(len(question_concepts), 1))
            total_similarity += similarity

        return total_similarity / len(docs)

    def _extract_concepts(self, text: str) -> set:
        """Extract key concepts from text (simplified)"""
        # This is a very basic implementation
        # In production, use NLP techniques like NER, keyword extraction, etc.

        text_lower = text.lower()
        concepts = set()

        # Marketing-specific concepts
        marketing_concepts = [
            'seo', 'sem', 'social media', 'content marketing', 'email marketing',
            'lead generation', 'conversion rate', 'customer acquisition',
            'brand awareness', 'target audience', 'buyer persona',
            'funnel', 'retention', 'engagement', 'analytics'
        ]

        for concept in marketing_concepts:
            if concept in text_lower:
                concepts.add(concept)

        # Add some basic noun phrases (very simplified)
        words = text_lower.split()
        for i in range(len(words) - 1):
            if words[i] in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
                continue
            if len(words[i]) > 3 and len(words[i+1]) > 3:
                concepts.add(f"{words[i]} {words[i+1]}")

        return concepts

    def _calculate_source_authority(self, docs: List[Document]) -> float:
        """Score based on source credibility and authority"""
        if not docs:
            return 0.0

        authority_sources = {
            'forrester': 1.0,
            'gartner': 1.0,
            'mckinsey': 1.0,
            'harvard': 0.9,
            'stanford': 0.9,
            'google': 0.8,
            'hubspot': 0.8,
            'salesforce': 0.8,
            'expert_compilation': 0.7,
            'industry_report': 0.6
        }

        total_authority = 0.0

        for doc in docs:
            source = doc.metadata.get('source', '').lower()
            authority_score = 0.5  # Default medium authority

            # Check for authority sources
            for auth_source, score in authority_sources.items():
                if auth_source in source:
                    authority_score = score
                    break

            # Check for expert tags
            if doc.metadata.get('tags'):
                tags = [tag.lower() for tag in doc.metadata['tags']]
                if 'expert' in tags or 'authority' in tags:
                    authority_score = min(1.0, authority_score + 0.2)

            total_authority += authority_score

        return total_authority / len(docs)

    def _calculate_answer_consistency(self, response: str, docs: List[Document]) -> float:
        """Check if the answer is consistent with the source documents"""
        if not docs or not response:
            return 0.0

        response_lower = response.lower()
        total_consistency = 0.0

        for doc in docs:
            doc_content = doc.page_content.lower()

            # Check for factual consistency (simplified)
            # Count shared key terms
            response_words = set(response_lower.split())
            doc_words = set(doc_content.split())

            overlap = len(response_words.intersection(doc_words))
            consistency = overlap / max(len(response_words), 1)

            # Boost if response contains key marketing terms from documents
            marketing_terms = ['strategy', 'optimization', 'performance', 'conversion', 'engagement']
            marketing_overlap = sum(1 for term in marketing_terms if term in response_lower and term in doc_content)
            consistency += marketing_overlap * 0.1

            total_consistency += min(1.0, consistency)

        return total_consistency / len(docs)

    def _get_confidence_level(self, score: float) -> str:
        """Convert numeric score to confidence level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'

    def _generate_explanation(self, score: float, docs: List[Document]) -> str:
        """Generate human-readable explanation of confidence score"""
        level = self._get_confidence_level(score)
        doc_count = len(docs)

        explanations = {
            'high': f"High confidence based on {doc_count} relevant sources with strong alignment to the query.",
            'medium': f"Medium confidence with {doc_count} sources providing reasonable coverage of the topic.",
            'low': f"Low confidence due to limited source material ({doc_count} documents) or weak relevance.",
            'very_low': f"Very low confidence - insufficient or irrelevant source material found."
        }

        return explanations.get(level, "Unable to determine confidence level.")


class ConfidenceThresholds:
    """Predefined confidence thresholds for different use cases"""

    # Thresholds for different confidence levels
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4

    # Use case specific thresholds
    AGENT_DECISION_MAKING = 0.7  # Higher threshold for automated decisions
    USER_RESPONSE = 0.5  # Lower threshold for user-facing responses
    EXPERT_REVIEW = 0.3  # Even lower for expert review scenarios

    @staticmethod
    def get_threshold(use_case: str) -> float:
        """Get confidence threshold for specific use case"""
        thresholds = {
            'agent_decision': ConfidenceThresholds.AGENT_DECISION_MAKING,
            'user_response': ConfidenceThresholds.USER_RESPONSE,
            'expert_review': ConfidenceThresholds.EXPERT_REVIEW,
            'default': ConfidenceThresholds.MEDIUM_CONFIDENCE
        }

        return thresholds.get(use_case, thresholds['default'])

    @staticmethod
    def meets_threshold(score: float, use_case: str = 'default') -> bool:
        """Check if confidence score meets threshold for use case"""
        threshold = ConfidenceThresholds.get_threshold(use_case)
        return score >= threshold


# Global instance
_confidence_scorer = None


def get_confidence_scorer() -> RAGConfidenceScorer:
    """Get global confidence scorer instance"""
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = RAGConfidenceScorer()
    return _confidence_scorer


# Convenience functions
def score_rag_response(question: str, docs: List[Document], response: str) -> Dict[str, Any]:
    """Convenience function to score RAG response"""
    scorer = get_confidence_scorer()
    return scorer.score_response(question, docs, response)


def check_confidence_threshold(score: float, use_case: str = 'default') -> bool:
    """Check if confidence score meets threshold"""
    return ConfidenceThresholds.meets_threshold(score, use_case)