"""
Firebase Firestore integration for agent state persistence.
Provides real-time data streaming and state management.
"""
import json
from typing import Any, Dict, Optional, List
from datetime import datetime
import structlog

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

from config import config

logger = structlog.get_logger()

class FirebaseManager:
    """Manages Firebase Firestore connections and operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase with proper error handling"""
        try:
            # Convert Pydantic config to dict for Firebase
            firebase_dict = config.firebase.dict()
            
            # Ensure private key is properly formatted
            if '\\n' in firebase_dict.get('private_key', ''):
                firebase_dict['private_key'] = firebase_dict['private_key'].replace('\\n', '\n')
            
            cred = credentials.Certificate(firebase_dict)
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("Firebase Firestore initialized successfully")
            
        except ValueError as e:
            logger.error("Invalid Firebase configuration", error=str(e))
            raise
        except FirebaseError as e:
            logger.error("Firebase initialization failed", error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error during Firebase initialization", error=str(e))
            raise
    
    def save_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """Save agent state to Firestore with timestamp"""
        try:
            state['last_updated'] = firestore.SERVER_TIMESTAMP
            state['agent_id'] = agent_id
            
            doc_ref = self.db.collection('agents').document(agent_id)
            doc_ref.set(state, merge=True)
            
            logger.debug("Agent state saved", agent_id=agent_id)
            return True
            
        except FirebaseError as e:
            logger.error("Failed to save agent state", agent_id=agent_id, error=str(e))
            return False
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent state from Firestore"""
        try:
            doc_ref = self.db.collection('agents').document(agent_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                logger.debug("Agent state retrieved", agent_id=agent_id)
                return data
            else:
                logger.warning("Agent state not found", agent_id=