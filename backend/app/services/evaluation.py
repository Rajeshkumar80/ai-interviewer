from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
import time
import math

class EvaluationEngine:
    def __init__(self):
        nltk.download('stopwords', quiet=True)
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def preprocess_text(self, text):
        if not text:
            return ""
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        tokens = [word for word in text.split() if word not in self.stop_words]
        return ' '.join(tokens)
    
    def calculate_semantic_similarity(self, answer, ideal_answer):
        try:
            answer_processed = self.preprocess_text(answer)
            ideal_processed = self.preprocess_text(ideal_answer)
                
            if not answer_processed or not ideal_processed:
                return 0.0
                
            tfidf_matrix = self.vectorizer.fit_transform([answer_processed, ideal_processed])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            print(f"Error in semantic similarity: {str(e)}")
            return 0.0
    
    def analyze_speech_metrics(self, transcript, audio_duration):
        if not transcript:
            return {
                'word_count': 0,
                'speech_rate': 0,
                'filler_word_count': 0,
                'pauses': 0,
                'clarity_score': 0
            }
            
        words = transcript.split()
        word_count = len(words)
        speech_rate = (word_count / audio_duration) * 60 if audio_duration > 0 else 0
        
        filler_words = ['um', 'uh', 'ah', 'like', 'you know', 'so', 'well']
        filler_count = sum(1 for word in words if word.lower() in filler_words)
        
        pause_threshold = 1.5
        pauses = transcript.count('.') + transcript.count('?') + transcript.count('!')
        pause_frequency = pauses / audio_duration if audio_duration > 0 else 0
        
        unique_words = set(words)
        ttr = len(unique_words) / word_count if word_count > 0 else 0
        clarity = min(1.0, ttr * 0.8 + (1 - (filler_count / word_count)) * 0.2 if word_count > 0 else 0)
        
        return {
            'word_count': word_count,
            'speech_rate': round(speech_rate, 2),
            'filler_word_count': filler_count,
            'pauses': round(pause_frequency, 2),
            'clarity_score': round(clarity, 2)
        }
    
    def evaluate_code(self, user_code, test_cases):
        results = {
            'passed': 0,
            'failed': 0,
            'test_results': [],
            'error': None
        }
        
        try:
            local_namespace = {}
            exec(user_code, globals(), local_namespace)
            
            for i, test_case in enumerate(test_cases, 1):
                try:
                    func = local_namespace.get('solution')
                    if not callable(func):
                        raise ValueError("No callable 'solution' function found")
                    
                    result = {
                        'test_case': i,
                        'input': test_case.get('input'),
                        'expected': test_case.get('expected'),
                        'passed': False,
                        'output': None,
                        'error': None
                    }
                    
                    start_time = time.time()
                    output = func(*test_case['input'])
                    execution_time = time.time() - start_time
                    
                    result['output'] = output
                    result['execution_time'] = execution_time
                    result['passed'] = output == test_case['expected']
                    
                    if result['passed']:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                        
                    results['test_results'].append(result)
                    
                except Exception as e:
                    results['failed'] += 1
                    results['test_results'].append({
                        'test_case': i,
                        'input': test_case.get('input'),
                        'expected': test_case.get('expected'),
                        'passed': False,
                        'output': None,
                        'error': str(e)
                    })
            
        except Exception as e:
            results['error'] = f"Code execution error: {str(e)}"
        
        return results
    
    def generate_feedback(self, evaluation_results):
        feedback = {
            'score': 0,
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
            'ideal_answer': evaluation_results.get('ideal_answer', ''),
            'detailed_feedback': {}
        }
        
        semantic_score = evaluation_results.get('semantic_similarity', 0)
        feedback['score'] = round(semantic_score * 100, 1)
        
        if 'speech_metrics' in evaluation_results:
            metrics = evaluation_results['speech_metrics']
            
            if metrics['speech_rate'] < 100:
                feedback['suggestions'].append("Try speaking a bit faster for better engagement.")
            elif metrics['speech_rate'] > 180:
                feedback['suggestions'].append("You're speaking quite fast. Try to slow down for better clarity.")
            else:
                feedback['strengths'].append("Good speaking pace!")
            
            if metrics['filler_word_count'] > 5:
                feedback['suggestions'].append(
                    f"Try to reduce filler words (used {metrics['filler_word_count']} times). "
                    "Practice pausing instead of using fillers."
                )
            
            if metrics['clarity_score'] < 0.5:
                feedback['suggestions'].append(
                    "Work on making your answers more concise and clear. "
                    "Try structuring your thoughts before speaking."
                )
        
        if 'code_evaluation' in evaluation_results:
            code_results = evaluation_results['code_evaluation']
            if code_results['passed'] > 0:
                feedback['strengths'].append(
                    f"Great job! Your code passed {code_results['passed']} test case(s)."
                )
            if code_results['failed'] > 0:
                feedback['suggestions'].append(
                    f"Your code failed {code_results['failed']} test case(s). "
                    "Review the test cases and try to understand where your solution differs."
                )
        
        if 'missing_keywords' in evaluation_results:
            missing = evaluation_results['missing_keywords']
            if missing:
                feedback['suggestions'].append(
                    f"Consider mentioning these key concepts: {', '.join(missing[:3])}."
                )
        
        if not feedback['strengths'] and feedback['score'] > 70:
            feedback['strengths'].append("Good overall response!")
        
        if not feedback['suggestions'] and feedback['score'] < 50:
            feedback['suggestions'].append(
                "Try to provide more detailed and structured answers. "
                "Mention specific examples or steps where applicable."
            )
        
        feedback['detailed_feedback'] = evaluation_results
        return feedback
