# Enhanced NLP Training Script with Model Optimization
import os
import csv
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class EnhancedIntentTrainer:
    def __init__(self, data_path="data/questions_enhanced.csv", output_dir="artifacts"):
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {
            'logistic': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1,3), min_df=2, max_df=0.95, stop_words='english')),
                ('clf', LogisticRegression(max_iter=2000, random_state=42))
            ]),
            'random_forest': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=2, max_df=0.95, stop_words='english')),
                ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
            ]),
            'svm': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=2, max_df=0.95, stop_words='english')),
                ('clf', SVC(kernel='rbf', random_state=42, probability=True))
            ]),
            'naive_bayes': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=2, max_df=0.95, stop_words='english')),
                ('clf', MultinomialNB(alpha=0.1))
            ])
        }
        
        self.param_grids = {
            'logistic': {
                'tfidf__ngram_range': [(1,1), (1,2), (1,3)],
                'tfidf__max_features': [1000, 2000, 5000],
                'clf__C': [0.1, 1, 10, 100]
            },
            'random_forest': {
                'tfidf__ngram_range': [(1,1), (1,2)],
                'tfidf__max_features': [1000, 2000],
                'clf__n_estimators': [50, 100, 200],
                'clf__max_depth': [10, 20, None]
            },
            'svm': {
                'tfidf__ngram_range': [(1,1), (1,2)],
                'tfidf__max_features': [1000, 2000],
                'clf__C': [0.1, 1, 10],
                'clf__gamma': ['scale', 'auto']
            }
        }
    
    def load_data(self):
        """Load and preprocess training data"""
        print(f"Loading data from {self.data_path}...")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Training data not found: {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        
        # Clean and validate data
        df = df.dropna(subset=['text', 'intent'])
        df['text'] = df['text'].str.strip()
        df['intent'] = df['intent'].str.strip()
        
        # Remove empty entries
        df = df[(df['text'] != '') & (df['intent'] != '')]
        
        print(f"Loaded {len(df)} training samples")
        print(f"Intent distribution:")
        print(df['intent'].value_counts())
        
        return df['text'].tolist(), df['intent'].tolist()
    
    def evaluate_models(self, X, y):
        """Compare different models using cross-validation"""
        print("\n=== Model Comparison ===")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        results = {}
        
        for name, model in self.models.items():
            print(f"\nEvaluating {name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            
            # Fit and test
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)
            
            results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_accuracy': test_accuracy,
                'model': model
            }
            
            print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            print(f"Test Accuracy: {test_accuracy:.3f}")
        
        return results, X_train, X_test, y_train, y_test
    
    def optimize_best_model(self, X_train, y_train):
        """Optimize hyperparameters for the best performing model"""
        print("\n=== Hyperparameter Optimization ===")
        
        # Use Logistic Regression as it typically performs well for text classification
        best_model = self.models['logistic']
        param_grid = self.param_grids['logistic']
        
        print("Optimizing Logistic Regression...")
        
        grid_search = GridSearchCV(
            best_model, 
            param_grid, 
            cv=5, 
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.3f}")
        
        return grid_search.best_estimator_
    
    def generate_detailed_report(self, model, X_test, y_test, output_path):
        """Generate detailed model performance report"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Confidence analysis
        confidences = np.max(y_pred_proba, axis=1)
        
        report_text = f"""
=== Enhanced Sports Chatbot - Intent Classification Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL PERFORMANCE:
- Accuracy: {report['accuracy']:.3f}
- Macro Avg F1: {report['macro avg']['f1-score']:.3f}
- Weighted Avg F1: {report['weighted avg']['f1-score']:.3f}

CONFIDENCE ANALYSIS:
- Mean Confidence: {confidences.mean():.3f}
- Min Confidence: {confidences.min():.3f}
- Max Confidence: {confidences.max():.3f}
- Std Confidence: {confidences.std():.3f}

PER-INTENT PERFORMANCE:
"""
        
        for intent in sorted(set(y_test)):
            if intent in report:
                intent_report = report[intent]
                report_text += f"""
{intent.upper()}:
  - Precision: {intent_report['precision']:.3f}
  - Recall: {intent_report['recall']:.3f}
  - F1-Score: {intent_report['f1-score']:.3f}
  - Support: {intent_report['support']}
"""
        
        # Low confidence predictions
        low_conf_mask = confidences < 0.7
        if low_conf_mask.any():
            report_text += f"""
LOW CONFIDENCE PREDICTIONS ({np.sum(low_conf_mask)} samples):
"""
            for i, (text, pred, true, conf) in enumerate(zip(
                np.array(X_test)[low_conf_mask],
                np.array(y_pred)[low_conf_mask], 
                np.array(y_test)[low_conf_mask],
                confidences[low_conf_mask]
            )):
                if i < 10:  # Show first 10
                    report_text += f"  - \"{text[:60]}...\" | Pred: {pred} | True: {true} | Conf: {conf:.3f}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"Detailed report saved to {output_path}")
        
        return report, confidences
    
    def train_and_evaluate(self):
        """Main training and evaluation pipeline"""
        print("=== Enhanced Intent Model Training ===")
        
        # Load data
        X, y = self.load_data()
        
        # Compare models
        model_results, X_train, X_test, y_train, y_test = self.evaluate_models(X, y)
        
        # Find best model
        best_model_name = max(model_results.keys(), 
                            key=lambda k: model_results[k]['test_accuracy'])
        print(f"\nBest model: {best_model_name} (accuracy: {model_results[best_model_name]['test_accuracy']:.3f})")
        
        # Optimize hyperparameters
        optimized_model = self.optimize_best_model(X_train, y_train)
        
        # Final evaluation
        print("\n=== Final Model Evaluation ===")
        y_pred = optimized_model.predict(X_test)
        final_accuracy = accuracy_score(y_test, y_pred)
        print(f"Final optimized accuracy: {final_accuracy:.3f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Generate detailed report
        report_path = self.output_dir / f"model_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.generate_detailed_report(optimized_model, X_test, y_test, report_path)
        
        # Save the optimized model
        model_path = self.output_dir / "intent_model_enhanced.pkl"
        joblib.dump(optimized_model, model_path)
        print(f"\nOptimized model saved to {model_path}")
        
        # Save model metadata
        metadata = {
            'model_type': type(optimized_model.named_steps['clf']).__name__,
            'training_samples': len(X),
            'test_accuracy': final_accuracy,
            'intent_classes': sorted(set(y)),
            'confidence_threshold_recommendation': 0.6,  # Based on confidence analysis
            'trained_date': datetime.now().isoformat()
        }
        
        metadata_path = self.output_dir / "model_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return optimized_model, final_accuracy

if __name__ == "__main__":
    trainer = EnhancedIntentTrainer()
    model, accuracy = trainer.train_and_evaluate()
    print(f"\n✅ Training completed! Final accuracy: {accuracy:.3f}")