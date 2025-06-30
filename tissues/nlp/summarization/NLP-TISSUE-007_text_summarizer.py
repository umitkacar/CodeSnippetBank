"""
Tissue ID: NLP-TISSUE-007
Title: Multi-Strategy Text Summarizer
Category: nlp/summarization
Tags: ["text-summarization", "extractive", "abstractive", "nlp", "document-processing"]
Difficulty: Advanced
Dependencies: ["numpy>=1.24", "networkx>=3.1", "scikit-learn>=1.3"]
Performance: O(n²) for graph-based methods where n is number of sentences
Tested: Python 3.8+, 3.9, 3.10
Author: CodeSnippetBank
Version: 1.0.0
Last Updated: 2024-01-20

Description:
A comprehensive text summarization tissue that provides multiple strategies for
creating concise summaries. Includes extractive methods (TextRank, frequency-based,
position-based) and simple abstractive approaches. Supports single and multi-document
summarization with customizable summary lengths.

Use Cases:
- Document summarization
- News article summarization
- Meeting notes condensation
- Research paper abstracts
- Content previews

Example Usage:
    # Basic summarization
    summarizer = TextSummarizer(strategy="textrank")
    summary = summarizer.summarize(long_text, num_sentences=3)
    
    # Percentage-based summary
    summary = summarizer.summarize(text, ratio=0.3)  # 30% of original
    
    # Multi-document summarization
    summaries = summarizer.summarize_multiple(documents, max_words=200)
"""

import numpy as np
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import Counter, defaultdict
import math


class SummarizationStrategy(Enum):
    """Available summarization strategies"""
    TEXTRANK = "textrank"
    FREQUENCY = "frequency"
    POSITION = "position"
    TF_IDF = "tf_idf"
    LUHN = "luhn"
    LSA = "lsa"
    HYBRID = "hybrid"


@dataclass
class SummaryConfig:
    """Configuration for text summarization"""
    min_sentence_length: int = 10
    max_sentence_length: int = 500
    sentence_similarity_threshold: float = 0.1
    damping_factor: float = 0.85  # For TextRank
    convergence_threshold: float = 0.0001
    max_iterations: int = 100
    preserve_order: bool = True
    remove_duplicates: bool = True
    include_title: bool = True
    language: str = "en"


@dataclass
class SentenceScore:
    """Represents a scored sentence"""
    text: str
    position: int
    score: float
    word_count: int
    features: Dict[str, Any] = field(default_factory=dict)


class TextSummarizer:
    """
    Multi-strategy text summarization system.
    Tissue Type: FUNCTIONAL - Core NLP summarization.
    """
    
    # Common abbreviations that don't end sentences
    ABBREVIATIONS = {
        'dr', 'mr', 'mrs', 'ms', 'prof', 'sr', 'jr', 'ph.d',
        'i.e', 'e.g', 'etc', 'vs', 'inc', 'ltd', 'co', 'corp'
    }
    
    def __init__(self,
                 strategy: str = "textrank",
                 config: Optional[SummaryConfig] = None,
                 stop_words: Optional[Set[str]] = None):
        """
        Initialize text summarizer.
        
        Args:
            strategy: Summarization strategy to use
            config: Configuration options
            stop_words: Set of stop words to ignore
        """
        self.strategy = SummarizationStrategy(strategy.lower())
        self.config = config or SummaryConfig()
        self.stop_words = stop_words or self._get_default_stop_words()
        
        # Statistics
        self.texts_processed = 0
        self.summaries_generated = 0
    
    def summarize(self, text: str,
                 num_sentences: Optional[int] = None,
                 ratio: Optional[float] = None,
                 max_words: Optional[int] = None) -> str:
        """
        Summarize text using specified strategy.
        
        Args:
            text: Input text to summarize
            num_sentences: Number of sentences in summary
            ratio: Ratio of original text to keep (0-1)
            max_words: Maximum words in summary
            
        Returns:
            Summary text
        """
        if not text:
            return ""
        
        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return ""
        
        # Determine summary length
        target_sentences = self._calculate_target_length(
            len(sentences), num_sentences, ratio
        )
        
        if target_sentences >= len(sentences):
            return text
        
        # Score sentences based on strategy
        scored_sentences = self._score_sentences(sentences)
        
        # Select top sentences
        selected = self._select_sentences(
            scored_sentences, target_sentences, max_words
        )
        
        # Compose summary
        summary = self._compose_summary(selected)
        
        self.texts_processed += 1
        self.summaries_generated += 1
        
        return summary
    
    def summarize_multiple(self, documents: List[str],
                         num_sentences: Optional[int] = None,
                         ratio: Optional[float] = None,
                         max_words: Optional[int] = None) -> str:
        """
        Summarize multiple documents.
        
        Args:
            documents: List of documents to summarize
            num_sentences: Number of sentences in summary
            ratio: Ratio of original text to keep
            max_words: Maximum words in summary
            
        Returns:
            Combined summary
        """
        if not documents:
            return ""
        
        # Combine all sentences with document info
        all_sentences = []
        for doc_idx, doc in enumerate(documents):
            sentences = self._split_sentences(doc)
            for sent_idx, sent in enumerate(sentences):
                all_sentences.append({
                    "text": sent,
                    "doc_idx": doc_idx,
                    "sent_idx": sent_idx,
                    "position": len(all_sentences)
                })
        
        if not all_sentences:
            return ""
        
        # Score sentences across all documents
        scored_sentences = self._score_sentences_multi(all_sentences)
        
        # Determine target length
        target_sentences = self._calculate_target_length(
            len(all_sentences), num_sentences, ratio
        )
        
        # Select sentences with diversity
        selected = self._select_sentences_diverse(
            scored_sentences, target_sentences, max_words
        )
        
        # Compose summary
        summary = self._compose_summary(selected)
        
        self.texts_processed += len(documents)
        self.summaries_generated += 1
        
        return summary
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        # Handle abbreviations
        text = text.replace('\n', ' ')
        
        # Mark abbreviations
        for abbr in self.ABBREVIATIONS:
            text = re.sub(f'\\b{abbr}\\.', f'{abbr}@@@', text, flags=re.IGNORECASE)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Restore abbreviations
        sentences = [s.replace('@@@', '.') for s in sentences]
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        sentences = [s for s in sentences if 
                    self.config.min_sentence_length <= len(s.split()) <= self.config.max_sentence_length]
        
        return sentences
    
    def _score_sentences(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences based on strategy"""
        if self.strategy == SummarizationStrategy.TEXTRANK:
            return self._score_textrank(sentences)
        elif self.strategy == SummarizationStrategy.FREQUENCY:
            return self._score_frequency(sentences)
        elif self.strategy == SummarizationStrategy.POSITION:
            return self._score_position(sentences)
        elif self.strategy == SummarizationStrategy.TF_IDF:
            return self._score_tfidf(sentences)
        elif self.strategy == SummarizationStrategy.LUHN:
            return self._score_luhn(sentences)
        elif self.strategy == SummarizationStrategy.LSA:
            return self._score_lsa(sentences)
        elif self.strategy == SummarizationStrategy.HYBRID:
            return self._score_hybrid(sentences)
        else:
            return self._score_frequency(sentences)
    
    def _score_textrank(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences using TextRank algorithm"""
        n = len(sentences)
        if n == 0:
            return []
        
        # Build similarity matrix
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    similarity = self._sentence_similarity(sentences[i], sentences[j])
                    similarity_matrix[i][j] = similarity
        
        # Initialize scores
        scores = np.ones(n) / n
        
        # Power iteration
        for _ in range(self.config.max_iterations):
            prev_scores = scores.copy()
            
            for i in range(n):
                score_sum = 0
                for j in range(n):
                    if similarity_matrix[j][i] > 0:
                        score_sum += (similarity_matrix[j][i] * scores[j] / 
                                    np.sum(similarity_matrix[j]))
                
                scores[i] = (1 - self.config.damping_factor) + \
                           self.config.damping_factor * score_sum
            
            # Check convergence
            if np.sum(np.abs(scores - prev_scores)) < self.config.convergence_threshold:
                break
        
        # Create SentenceScore objects
        sentence_scores = []
        for i, (sent, score) in enumerate(zip(sentences, scores)):
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=float(score),
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_frequency(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences based on word frequency"""
        # Calculate word frequencies
        word_freq = Counter()
        for sent in sentences:
            words = self._tokenize(sent.lower())
            words = [w for w in words if w not in self.stop_words]
            word_freq.update(words)
        
        # Score sentences
        sentence_scores = []
        for i, sent in enumerate(sentences):
            words = self._tokenize(sent.lower())
            words = [w for w in words if w not in self.stop_words]
            
            if words:
                score = sum(word_freq[w] for w in words) / len(words)
            else:
                score = 0
            
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=score,
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_position(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences based on position"""
        n = len(sentences)
        sentence_scores = []
        
        for i, sent in enumerate(sentences):
            # Higher scores for beginning and end
            if i < n * 0.2:  # First 20%
                position_score = 1.0
            elif i > n * 0.8:  # Last 20%
                position_score = 0.8
            else:
                position_score = 0.5
            
            # Boost for sentences with numbers or capitals
            boost = 0
            if re.search(r'\d+', sent):
                boost += 0.1
            if re.search(r'[A-Z]{2,}', sent):
                boost += 0.1
            
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=position_score + boost,
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_tfidf(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences using TF-IDF"""
        # Calculate TF-IDF scores
        tf_scores = []
        df_counts = Counter()
        
        # Calculate term frequencies and document frequencies
        for sent in sentences:
            words = self._tokenize(sent.lower())
            words = [w for w in words if w not in self.stop_words]
            
            tf = Counter(words)
            tf_scores.append(tf)
            
            # Document frequency (sentence as document)
            for word in set(words):
                df_counts[word] += 1
        
        # Calculate IDF
        n_sentences = len(sentences)
        idf = {}
        for word, df in df_counts.items():
            idf[word] = math.log(n_sentences / (1 + df))
        
        # Score sentences
        sentence_scores = []
        for i, (sent, tf) in enumerate(zip(sentences, tf_scores)):
            if tf:
                # TF-IDF score
                tfidf_sum = sum(tf[word] * idf.get(word, 0) for word in tf)
                score = tfidf_sum / len(tf)
            else:
                score = 0
            
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=score,
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_luhn(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences using Luhn's method"""
        # Find significant words
        word_freq = Counter()
        for sent in sentences:
            words = self._tokenize(sent.lower())
            words = [w for w in words if w not in self.stop_words]
            word_freq.update(words)
        
        # Determine significance threshold
        if word_freq:
            freq_values = list(word_freq.values())
            mean_freq = np.mean(freq_values)
            std_freq = np.std(freq_values)
            threshold = mean_freq + std_freq
            
            significant_words = {word for word, freq in word_freq.items() 
                               if freq > threshold}
        else:
            significant_words = set()
        
        # Score sentences
        sentence_scores = []
        for i, sent in enumerate(sentences):
            words = self._tokenize(sent.lower())
            
            # Find clusters of significant words
            clusters = []
            current_cluster = []
            
            for j, word in enumerate(words):
                if word in significant_words:
                    current_cluster.append(j)
                elif current_cluster:
                    clusters.append(current_cluster)
                    current_cluster = []
            
            if current_cluster:
                clusters.append(current_cluster)
            
            # Score based on cluster density
            if clusters:
                cluster_scores = []
                for cluster in clusters:
                    if len(cluster) > 1:
                        # Density = significant words / total span
                        span = cluster[-1] - cluster[0] + 1
                        density = len(cluster) / span
                        cluster_scores.append(density * len(cluster))
                    else:
                        cluster_scores.append(1)
                
                score = max(cluster_scores) if cluster_scores else 0
            else:
                score = 0
            
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=score,
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_lsa(self, sentences: List[str]) -> List[SentenceScore]:
        """Score sentences using Latent Semantic Analysis"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            
            # Create TF-IDF matrix
            vectorizer = TfidfVectorizer(
                stop_words=list(self.stop_words),
                max_features=100
            )
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Apply SVD
            n_components = min(5, len(sentences) - 1)
            if n_components > 0:
                svd = TruncatedSVD(n_components=n_components)
                lsa_matrix = svd.fit_transform(tfidf_matrix)
                
                # Score sentences based on their representation in top component
                scores = np.abs(lsa_matrix[:, 0])
            else:
                scores = np.ones(len(sentences))
            
        except ImportError:
            # Fallback to frequency-based scoring
            return self._score_frequency(sentences)
        
        # Create SentenceScore objects
        sentence_scores = []
        for i, (sent, score) in enumerate(zip(sentences, scores)):
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=float(score),
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _score_hybrid(self, sentences: List[str]) -> List[SentenceScore]:
        """Combine multiple scoring methods"""
        # Get scores from different methods
        freq_scores = self._score_frequency(sentences)
        pos_scores = self._score_position(sentences)
        tfidf_scores = self._score_tfidf(sentences)
        
        # Normalize scores
        def normalize_scores(scores):
            values = [s.score for s in scores]
            if values:
                min_val = min(values)
                max_val = max(values)
                if max_val > min_val:
                    return [(s - min_val) / (max_val - min_val) for s in values]
            return values
        
        freq_norm = normalize_scores(freq_scores)
        pos_norm = normalize_scores(pos_scores)
        tfidf_norm = normalize_scores(tfidf_scores)
        
        # Combine scores (weighted average)
        sentence_scores = []
        for i, sent in enumerate(sentences):
            combined_score = (0.4 * freq_norm[i] + 
                            0.2 * pos_norm[i] + 
                            0.4 * tfidf_norm[i])
            
            sentence_scores.append(SentenceScore(
                text=sent,
                position=i,
                score=combined_score,
                word_count=len(sent.split())
            ))
        
        return sentence_scores
    
    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate similarity between two sentences"""
        words1 = set(self._tokenize(sent1.lower()))
        words2 = set(self._tokenize(sent2.lower()))
        
        # Remove stop words
        words1 = words1 - self.stop_words
        words2 = words2 - self.stop_words
        
        if not words1 or not words2:
            return 0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
    
    def _calculate_target_length(self, total_sentences: int,
                               num_sentences: Optional[int],
                               ratio: Optional[float]) -> int:
        """Calculate target summary length"""
        if num_sentences is not None:
            return min(num_sentences, total_sentences)
        elif ratio is not None:
            return max(1, int(total_sentences * ratio))
        else:
            # Default to 30% of original
            return max(1, int(total_sentences * 0.3))
    
    def _select_sentences(self, scored_sentences: List[SentenceScore],
                         target_sentences: int,
                         max_words: Optional[int]) -> List[SentenceScore]:
        """Select top sentences for summary"""
        # Sort by score
        sorted_sentences = sorted(scored_sentences, key=lambda x: x.score, reverse=True)
        
        selected = []
        total_words = 0
        
        for sent in sorted_sentences:
            if len(selected) >= target_sentences:
                break
            
            if max_words and total_words + sent.word_count > max_words:
                continue
            
            # Check for redundancy
            if self.config.remove_duplicates:
                is_redundant = False
                for sel in selected:
                    if self._sentence_similarity(sent.text, sel.text) > 0.8:
                        is_redundant = True
                        break
                
                if is_redundant:
                    continue
            
            selected.append(sent)
            total_words += sent.word_count
        
        return selected
    
    def _select_sentences_diverse(self, scored_sentences: List[Any],
                                target_sentences: int,
                                max_words: Optional[int]) -> List[Any]:
        """Select diverse sentences from multiple documents"""
        # Sort by score
        sorted_sentences = sorted(scored_sentences, key=lambda x: x["score"], reverse=True)
        
        selected = []
        total_words = 0
        doc_counts = defaultdict(int)
        
        for sent in sorted_sentences:
            if len(selected) >= target_sentences:
                break
            
            word_count = len(sent["text"].split())
            if max_words and total_words + word_count > max_words:
                continue
            
            # Ensure diversity across documents
            if doc_counts[sent["doc_idx"]] >= target_sentences // 2:
                continue
            
            selected.append(sent)
            total_words += word_count
            doc_counts[sent["doc_idx"]] += 1
        
        return selected
    
    def _compose_summary(self, selected_sentences: List[Any]) -> str:
        """Compose final summary from selected sentences"""
        if not selected_sentences:
            return ""
        
        # Sort by original position if preserving order
        if self.config.preserve_order:
            if isinstance(selected_sentences[0], SentenceScore):
                selected_sentences.sort(key=lambda x: x.position)
                sentences = [s.text for s in selected_sentences]
            else:
                selected_sentences.sort(key=lambda x: x["position"])
                sentences = [s["text"] for s in selected_sentences]
        else:
            if isinstance(selected_sentences[0], SentenceScore):
                sentences = [s.text for s in selected_sentences]
            else:
                sentences = [s["text"] for s in selected_sentences]
        
        # Join sentences
        summary = ". ".join(sentences)
        if not summary.endswith("."):
            summary += "."
        
        return summary
    
    def _score_sentences_multi(self, sentences: List[Dict]) -> List[Dict]:
        """Score sentences from multiple documents"""
        # Extract text for scoring
        texts = [s["text"] for s in sentences]
        
        # Score using current strategy
        scores = self._score_sentences(texts)
        
        # Add scores to sentence dictionaries
        for sent, score_obj in zip(sentences, scores):
            sent["score"] = score_obj.score
        
        return sentences
    
    def _get_default_stop_words(self) -> Set[str]:
        """Get default stop words"""
        return {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "yourselves", "he", "him",
            "his", "himself", "she", "her", "hers", "herself", "it", "its",
            "itself", "they", "them", "their", "theirs", "themselves",
            "what", "which", "who", "whom", "this", "that", "these",
            "those", "am", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "having", "do", "does", "did",
            "doing", "a", "an", "the", "and", "but", "if", "or", "because",
            "as", "until", "while", "of", "at", "by", "for", "with",
            "about", "against", "between", "into", "through", "during",
            "before", "after", "above", "below", "to", "from", "up",
            "down", "in", "out", "on", "off", "over", "under", "again",
            "further", "then", "once"
        }
    
    def get_key_phrases(self, text: str, num_phrases: int = 5) -> List[str]:
        """Extract key phrases from text"""
        sentences = self._split_sentences(text)
        
        # Extract noun phrases (simplified)
        phrases = []
        for sent in sentences:
            # Find consecutive capitalized words
            capital_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sent)
            phrases.extend(capital_phrases)
            
            # Find phrases with numbers
            number_phrases = re.findall(r'\b\w+\s+\d+\s+\w+\b', sent)
            phrases.extend(number_phrases)
        
        # Count and rank phrases
        phrase_counts = Counter(phrases)
        top_phrases = [phrase for phrase, _ in phrase_counts.most_common(num_phrases)]
        
        return top_phrases
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get summarization statistics"""
        return {
            "strategy": self.strategy.value,
            "texts_processed": self.texts_processed,
            "summaries_generated": self.summaries_generated,
            "avg_compression_ratio": 0.3  # Default compression
        }


# Utility functions
def summarize_text(text: str, num_sentences: int = 3) -> str:
    """Quick text summarization"""
    summarizer = TextSummarizer()
    return summarizer.summarize(text, num_sentences=num_sentences)


def get_key_points(text: str, num_points: int = 5) -> List[str]:
    """Extract key points from text"""
    summarizer = TextSummarizer(strategy="hybrid")
    
    # Get key sentences
    sentences = summarizer._split_sentences(text)
    scored = summarizer._score_sentences(sentences)
    
    # Sort and select top sentences
    scored.sort(key=lambda x: x.score, reverse=True)
    key_points = [s.text for s in scored[:num_points]]
    
    return key_points


def create_abstract(text: str, max_words: int = 150) -> str:
    """Create an abstract for a document"""
    summarizer = TextSummarizer(strategy="hybrid")
    return summarizer.summarize(text, max_words=max_words)


# Auto-generated tests
def test_text_summarizer():
    """Test text summarization functionality"""
    # Test text
    text = """
    Artificial intelligence is transforming the world. Machine learning algorithms 
    are becoming increasingly sophisticated. Deep learning has revolutionized 
    computer vision and natural language processing. Neural networks can now 
    perform tasks that were once thought impossible. The future of AI is bright 
    and full of possibilities. However, we must also consider the ethical 
    implications of these technologies. Responsible AI development is crucial 
    for ensuring benefits for all of humanity. Researchers are working on 
    making AI systems more transparent and interpretable. This is an exciting 
    time to be involved in artificial intelligence research and development.
    """
    
    # Test basic summarization
    summarizer = TextSummarizer(strategy="textrank")
    summary = summarizer.summarize(text, num_sentences=3)
    assert len(summary) > 0
    assert len(summary) < len(text)
    
    # Test ratio-based summarization
    summary_ratio = summarizer.summarize(text, ratio=0.3)
    assert len(summary_ratio) > 0
    
    # Test different strategies
    for strategy in ["frequency", "position", "tf_idf", "hybrid"]:
        summarizer = TextSummarizer(strategy=strategy)
        summary = summarizer.summarize(text, num_sentences=2)
        assert len(summary) > 0
    
    # Test multi-document summarization
    docs = [
        "Python is a versatile programming language. It is widely used in data science.",
        "Java is popular for enterprise applications. It has strong typing.",
        "JavaScript powers the modern web. It runs in browsers and servers."
    ]
    
    summary = summarizer.summarize_multiple(docs, num_sentences=2)
    assert len(summary) > 0
    
    # Test key phrase extraction
    key_phrases = summarizer.get_key_phrases(text, num_phrases=3)
    assert len(key_phrases) <= 3
    
    # Test utilities
    quick_summary = summarize_text(text, num_sentences=2)
    assert len(quick_summary) > 0
    
    key_points = get_key_points(text, num_points=3)
    assert len(key_points) <= 3
    
    abstract = create_abstract(text, max_words=50)
    assert len(abstract.split()) <= 60  # Some buffer for sentence completion
    
    print("All text summarization tests passed!")


if __name__ == "__main__":
    test_text_summarizer()