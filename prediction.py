import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
import json

def predict(train_df: pd.DataFrame, 
            test_df: pd.DataFrame, 
            pred_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main prediction function with enhanced statistical analysis
    
    Args:
        train_df (pd.DataFrame): Training data
        test_df (pd.DataFrame): Test data
        pred_df (pd.DataFrame): Prediction data
    
    Returns:
        Dict with comprehensive prediction results
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Basic prediction logic
    results = {
        'model_type': 'Basic Statistical Prediction',
        'predictions': {},
        'odds_analysis': {},
        'historical_stats': {}
    }
    
    try:
        # Analyze odds in prediction DataFrame
        if not pred_df.empty:
            odds_data = pred_df.iloc[0]
            
            # Odds analysis
            results['odds_analysis'] = {
                'home_odds': {
                    'max': float(odds_data.get('MaxH', 0)),
                    'avg': float(odds_data.get('AvgH', 0)),
                    'b365': float(odds_data.get('B365H', 0))
                },
                'draw_odds': {
                    'max': float(odds_data.get('MaxD', 0)),
                    'avg': float(odds_data.get('AvgD', 0)),
                    'b365': float(odds_data.get('B365D', 0))
                },
                'away_odds': {
                    'max': float(odds_data.get('MaxA', 0)),
                    'avg': float(odds_data.get('AvgA', 0)),
                    'b365': float(odds_data.get('B365A', 0))
                }
            }
            
            # Determine most likely outcome based on odds
            odds_dict = results['odds_analysis']
            min_odds_outcome = min(
                ('Home', odds_dict['home_odds']['avg']),
                ('Draw', odds_dict['draw_odds']['avg']),
                ('Away', odds_dict['away_odds']['avg']),
                key=lambda x: x[1]
            )
            
            results['predictions']['most_likely_outcome'] = min_odds_outcome[0]
            results['predictions']['confidence'] = 1 / min_odds_outcome[1]
        
        # Historical statistics analysis
        if 'FTR' in train_df.columns:
            # Outcome distribution
            outcome_counts = train_df['FTR'].value_counts()
            outcome_probs = train_df['FTR'].value_counts(normalize=True)
            
            results['historical_stats'] = {
                'outcome_distribution': outcome_counts.to_dict(),
                'outcome_probabilities': outcome_probs.to_dict()
            }
        
        # Goals analysis if available
        if 'TotalGoals' in train_df.columns:
            goals_stats = {
                'mean': train_df['TotalGoals'].mean(),
                'median': train_df['TotalGoals'].median(),
                'std': train_df['TotalGoals'].std()
            }
            results['historical_stats']['goals'] = goals_stats
        
        logger.info("Prediction analysis completed successfully")
        
        # Convert float values to fixed decimal for JSON serialization
        results = json.loads(json.dumps(results, default=lambda x: round(x, 4) if isinstance(x, float) else x))
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        results['error'] = str(e)
    
    return results
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

# Graceful import handling
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMER_AVAILABLE = True
except ImportError:
    TRANSFORMER_AVAILABLE = False
    # Mock classes to prevent import errors
    class AutoTokenizer:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return None
    
    class AutoModelForCausalLM:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return None
    
    def pipeline(*args, **kwargs):
        return None

def predict(train_df: pd.DataFrame, 
            test_df: pd.DataFrame, 
            pred_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main prediction function
    
    Args:
        train_df (pd.DataFrame): Training data
        test_df (pd.DataFrame): Test data
        pred_df (pd.DataFrame): Prediction data
    
    Returns:
        Dict with comprehensive prediction results
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Basic prediction logic
    results = {
        'model_type': 'Basic Statistical Prediction',
        'predictions': None,
        'probabilities': None,
        'insights': None
    }
    
    try:
        # Prepare features (handle cases with or without FTR column)
        if 'FTR' in train_df.columns:
            # Basic mode prediction based on most frequent outcome
            most_frequent_outcome = train_df['FTR'].mode().iloc[0]
            
            # Outcome probabilities
            outcome_probs = train_df['FTR'].value_counts(normalize=True)
            
            results['predictions'] = most_frequent_outcome
            results['probabilities'] = outcome_probs.to_dict()
        
        # Add basic insights from prediction DataFrame
        if not pred_df.empty:
            insights = []
            for col, value in pred_df.iloc[0].items():
                insights.append(f"{col}: {value}")
            
            results['insights'] = insights
        
        logger.info("Prediction completed successfully")
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        results['error'] = str(e)
    
    return results
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

# Graceful import handling
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMER_AVAILABLE = True
except ImportError:
    TRANSFORMER_AVAILABLE = False
    # Mock classes to prevent import errors
    class AutoTokenizer:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return None
    
    class AutoModelForCausalLM:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return None
    
    def pipeline(*args, **kwargs):
        return None

class MLPredictor:
    def __init__(self, 
                 model_name: str = "microsoft/phi-2",
                 device: Optional[str] = None):
        """
        Initialize ML Predictor with optional LLM integration
        
        Args:
            model_name (str): Hugging Face model identifier
            device (str, optional): Computation device ('cuda', 'cpu')
        """
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Device selection
        if not TRANSFORMER_AVAILABLE:
            self.logger.warning("Transformer libraries not installed. LLM features will be limited.")
            self.device = 'cpu'
            self.model = None
            self.tokenizer = None
            self.generator = None
            return
        
        # Device selection
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
   
        # Model and tokenizer (optional loading)
        self.model = None
        self.tokenizer = None
        self.generator = None
        
        try:
            # Attempt to load model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map='auto',
                offload_folder="offload",  # Specify a folder for offloaded weights
                offload_state_dict=True    # Enable offloading of state dict to disk
            )
            
            # Create text generation pipeline
            self.generator = pipeline(
                'text-generation', 
                model=self.model, 
                tokenizer=self.tokenizer,
                #device=self.device
            )
        except Exception as e:
            self.logger.warning(f"Could not load LLM: {e}")
            self.model = None
            self.tokenizer = None
            self.generator = None

    def prepare_input_features(self, 
                               train_df: pd.DataFrame, 
                               test_df: pd.DataFrame, 
                               pred_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepare input features for prediction
        
        Args:
            train_df (pd.DataFrame): Training data
            test_df (pd.DataFrame): Test data
            pred_df (pd.DataFrame): Prediction data
        
        Returns:
            Dict containing prepared features
        """
        # Basic feature preparation
        features = {
            'train': {
                'X': train_df.drop(['FTR'], axis=1) if 'FTR' in train_df.columns else train_df,
                'y': train_df['FTR'] if 'FTR' in train_df.columns else None
            },
            'test': {
                'X': test_df.drop(['FTR'], axis=1) if 'FTR' in test_df.columns else test_df,
                'y': test_df['FTR'] if 'FTR' in test_df.columns else None
            },
            'pred': {
                'X': pred_df
            }
        }
        
        return features

    def ml_prediction(self, 
                      train_df: pd.DataFrame, 
                      test_df: pd.DataFrame, 
                      pred_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform basic machine learning prediction
        
        Args:
            train_df (pd.DataFrame): Training data
            test_df (pd.DataFrame): Test data
            pred_df (pd.DataFrame): Prediction data
        
        Returns:
            Dict with prediction results
        """
        # Prepare features
        features = self.prepare_input_features(train_df, test_df, pred_df)
        
        # Simple statistical prediction
        results = {
            'model_type': 'Basic Statistical',
            'predictions': None,
            'probabilities': None,
            'accuracy': None
        }
        
        try:
            # If target exists in training data, do basic analysis
            if features['train']['y'] is not None:
                # Most frequent outcome
                most_frequent_outcome = features['train']['y'].mode().iloc[0]
                
                results['predictions'] = most_frequent_outcome
                results['probabilities'] = features['train']['y'].value_counts(normalize=True).to_dict()
        except Exception as e:
            self.logger.warning(f"Basic prediction error: {e}")
        
        return results

    def llm_prediction(self, 
                       train_df: pd.DataFrame, 
                       test_df: pd.DataFrame, 
                       pred_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate LLM-based prediction and insights
        
        Args:
            train_df (pd.DataFrame): Training data
            test_df (pd.DataFrame): Test data
            pred_df (pd.DataFrame): Prediction data
        
        Returns:
            Dict with LLM prediction insights
        """
        # Check if LLM is available
        if not self.generator:
            self.logger.warning("LLM not loaded. Skipping LLM prediction.")
            return {}
        
        # Prepare features
        features = self.prepare_input_features(train_df, test_df, pred_df)
        
        # Construct prompt
        prompt = self._construct_llm_prompt(features)
        
        try:
            # Generate LLM response
            response = self.generator(
                prompt, 
                max_length=500, 
                num_return_sequences=1,
                temperature=0.7
            )[0]['generated_text']
            
            # Parse LLM response
            parsed_response = self._parse_llm_response(response)
            
            return {
                'llm_insights': parsed_response,
                'raw_llm_response': response
            }
        except Exception as e:
            self.logger.error(f"LLM prediction error: {e}")
            return {}

    def _construct_llm_prompt(self, features: Dict[str, Any]) -> str:
        """
        Construct a detailed prompt for LLM prediction
        
        Args:
            features (Dict): Prepared input features
        
        Returns:
            str: Formatted prompt for LLM
        """
        # Basic prompt construction
        prompt = f"""Football Match Prediction Analysis

Training Data Context:
- Total Training Matches: {len(features['train']['X']) if features['train']['X'] is not None else 0}
- Outcome Distribution: {features['train']['y'].value_counts() if features['train']['y'] is not None else 'No training data'}

Prediction Match Features:
{features['pred']['X'].to_string()}

Task: 
1. Analyze the match features
2. Provide insights into potential match outcome
3. Estimate probability of different results
4. Highlight key factors influencing the prediction

Provide a structured response with:
- Predicted Outcome
- Confidence Level
- Key Influencing Factors
"""
        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM generated response
        
        Args:
            response (str): Raw LLM response
        
        Returns:
            Dict with parsed insights
        """
        # Basic parsing (can be enhanced)
        insights = {
            'raw_text': response,
            'predicted_outcome': None,
            'confidence': None,
            'key_factors': []
        }
        
        # Simple parsing logic (can be made more sophisticated)
        try:
            # Extract prediction
            if 'Predicted Outcome:' in response:
                outcome = response.split('Predicted Outcome:')[1].split('\n')[0].strip()
                insights['predicted_outcome'] = outcome
            
            # Extract confidence
            if 'Confidence Level:' in response:
                confidence = response.split('Confidence Level:')[1].split('\n')[0].strip()
                insights['confidence'] = confidence
            
            # Extract key factors
            if 'Key Influencing Factors:' in response:
                factors = response.split('Key Influencing Factors:')[1].split('\n')
                insights['key_factors'] = [f.strip() for f in factors if f.strip()]
        except Exception as e:
            self.logger.warning(f"Error parsing LLM response: {e}")
        
        return insights

def predict(train_df: pd.DataFrame, 
            test_df: pd.DataFrame, 
            pred_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main prediction function
    
    Args:
        train_df (pd.DataFrame): Training data
        test_df (pd.DataFrame): Test data
        pred_df (pd.DataFrame): Prediction data
    
    Returns:
        Dict with comprehensive prediction results
    """
    # Initialize predictor
    predictor = MLPredictor()
    
    # Perform predictions
    ml_results = predictor.ml_prediction(train_df, test_df, pred_df)
    llm_results = predictor.llm_prediction(train_df, test_df, pred_df)
    
    # Combine results
    combined_results = {
        **ml_results,
        **llm_results
    }
    
    return combined_results