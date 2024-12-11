# condition_checker.py

from typing import Any, Dict
from sentence_transformers import SentenceTransformer
import spacy
import openai
from fuzzywuzzy import fuzz
import logging
import os
from server.src.common.utils.singleton import singleton
from server.src.features.big_data.calculations.calculations_orch import CalculationsOrch
from server.src.features.big_data.conditions.bl.conditions_embedding_bl import ConditionsEmbeddingBl
from server.src.features.big_data.conditions.conditions_bl import ConditionsBl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConditionChecker:
    def __init__(self):
        # Load spaCy model for entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.error("Failed to load spaCy model: %s", e)
            raise
        
        self.calculations_orch = CalculationsOrch()
        self.conditions_bl = ConditionsBl()
        self.conditions_embeddings_bl = ConditionsEmbeddingBl()

        # Fetch supported indicators dynamically
        self.supported_indicators = self.fetch_supported_indicators()
        logger.info("Supported indicators: %s", self.supported_indicators)
        
        # Fetch supported actions dynamically or define them
        self.supported_actions = self.fetch_supported_actions()
        logger.info("Supported actions: %s", self.supported_actions)
        
        # Set OpenAI API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not found.")
        
        # Initialize embedding cache
        self.embedding_cache = {}  # Simple in-memory cache
    
    def fetch_supported_indicators(self):
        """
        Fetch supported indicators from the database.
        """
        indicators = self.calculations_orch.get_all_symbols()
        # Normalize to lowercase for consistency
        return [ind.lower() for ind in indicators]
    
    def fetch_supported_actions(self):
        """
        Fetch supported actions dynamically.
        For this example, we'll assume they are predefined.
        """
        # Actions can also be fetched from the database if stored there
        actions = ["crosses above", "crosses below", "greater than", "less than", "equals", "diverges"]
        return [act.lower() for act in actions]
    
    def normalize_text(self, text):
        """
        Normalize the user input by converting to lowercase,
        removing punctuation, and extra whitespace.
        """
        if not isinstance(text, str):
            logger.error("Input must be a string.")
            raise ValueError("Input must be a string.")
        
        # Remove punctuation and extra whitespace
        doc = self.nlp(text)
        tokens = [token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space]
        normalized_text = ' '.join(tokens)
        logger.debug("Normalized text: %s", normalized_text)
        return normalized_text
    
    def extract_entities(self, user_input):
        """
        Extract entities like indicators, actions, and thresholds using spaCy.
        """
        doc = self.nlp(user_input)
        indicators = []
        actions = []
        thresholds = []
        
        # Normalize the supported indicators and actions for comparison
        normalized_indicators = self.supported_indicators
        normalized_actions = self.supported_actions
        
        for token in doc:
            token_text = token.text.lower()
            if token_text in normalized_indicators:
                indicators.append(token_text)
            elif token_text in normalized_actions:
                actions.append(token_text)
            elif token.like_num:
                thresholds.append(token.text)
        
        # Remove duplicates
        indicators = list(set(indicators))
        actions = list(set(actions))
        
        logger.debug("Extracted indicators: %s", indicators)
        logger.debug("Extracted actions: %s", actions)
        logger.debug("Extracted thresholds: %s", thresholds)
        
        return {
            "indicators": indicators,
            "actions": actions,
            "thresholds": thresholds
        }
    
    def fuzzy_match_conditions(self, entities):
        """
        Attempt to find a fuzzy match for the user's input based on extracted entities.
        """
        conditions = self.conditions_bl.find_all()
        matched_conditions = []
        for condition in conditions:
            condition_indicators = ' '.join(condition.identifiers).lower()
            condition_actions = ' '.join(condition.actions).lower() if condition.actions else ''
            
            # Calculate fuzzy match ratios
            indicator_ratios = [fuzz.token_set_ratio(ind, condition_indicators) for ind in entities['indicators']]
            action_ratios = [fuzz.token_set_ratio(act, condition_actions) for act in entities['actions']]
            
            if indicator_ratios:
                indicator_ratio = max(indicator_ratios)
            else:
                indicator_ratio = 0
            if action_ratios:
                action_ratio = max(action_ratios)
            else:
                action_ratio = 0
            
            logger.debug("Fuzzy match ratios - Indicator: %s, Action: %s", indicator_ratio, action_ratio)
            
            # Set thresholds for fuzzy matching
            if indicator_ratio > 80 and action_ratio > 80:
                total_ratio = indicator_ratio + action_ratio
                matched_conditions.append((condition, total_ratio))
        
        if matched_conditions:
            # Return the best match
            matched_conditions.sort(key=lambda x: x[1], reverse=True)
            best_match = matched_conditions[0][0]
            logger.info("Fuzzy match found: %s", best_match['name'])
            return best_match
        return None
    
    
    def find_similar_conditions(self, user_embedding):
        """
        Find similar conditions using the user's input embedding.
        """
        similar_conditions = self.conditions_embeddings_bl.find_similar_conditions(user_embedding)
        return similar_conditions
    
    def validate_parameters(self, condition, entities):
        """
        Validate that the user's thresholds and parameters align with the condition's requirements.
        """
        # Extract required parameters from the condition
        required_params = condition.get('params_fields', {})
        missing_params = []
        
        for param, details in required_params.items():
            if param not in entities['thresholds'] and 'default' not in details:
                missing_params.append(param)
        
        if missing_params:
            logger.warning("Missing required parameters: %s", missing_params)
            return False, missing_params
        else:
            return True, []
        
    def is_embedding_exists(self, embedding):
        """
        Check if the embedding already exists in the database.
        """
                        # Find similar conditions using vector search
        similar_conditions = self.find_similar_conditions(embedding)
        if similar_conditions:
            top_condition = similar_conditions[0]
            similarity_score = top_condition.get('score', 0)
            condition_name = top_condition.get('name', 'Unnamed Condition')
            logger.info("Found similar condition: %s with score %f", condition_name, similarity_score)
            # Set a threshold for similarity
        if similarity_score > 0.8:
            return top_condition
        else:
            return None
    
    def process_user_request(self, user_input):
        """
        Main method to handle the user input and check if the condition already exists.
        """
        try:
            
            # Step 1: Normalize the input
            normalized_input = self.normalize_text(user_input)
            
            # Step 2: Extract entities from the user input
            entities = self.extract_entities(normalized_input)



            # Step 5: Attempt fuzzy matching
            matched_condition = self.fuzzy_match_conditions(entities)
            if matched_condition:
                return matched_condition
            else:
                # Step 6: Use embeddings as a last resort
                logger.info("No matching conditions found using exact or fuzzy matching. Attempting semantic matching using embeddings.")
                # Generate embedding for the user's input
                mode = SentenceTransformer('all-MiniLM-L6-v2')
                user_embedding = mode.encode(user_input)
                return self.is_embedding_exists(user_embedding)
        except Exception as e:
            logger.error("An error occurred while processing the request: %s", e)
            raise ValueError(e)


    def validate_generated_condition(self, condition: Dict[str, Any]):
        """
        Validate the generated condition by checking if it already exists.
        """
        existing_condition = self.is_embedding_exists(self.conditions_bl.get_embedding(condition))
        return existing_condition