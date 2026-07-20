"""
Common utilities for Digimon Deck Builder application
"""

import streamlit as st
import json
import os
import re
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

# Data loading functions
@st.cache_data
def load_card_data():
    """Load card data from JSON file"""
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open('digimon_cards_dict.json', 'r', encoding=encoding) as f:
                data = json.load(f)
                st.info(f"Successfully loaded card data with {encoding} encoding")
                return data
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            st.error("Card data file not found. Please ensure digimon_cards_dict.json exists.")
            return {}
        except json.JSONDecodeError as e:
            st.error(f"Error reading card data file: {e}")
            return {}
    
    st.error("Unable to read card data file with any supported encoding. File may be corrupted.")
    return {}

@st.cache_data
def load_image_mapping():
    """Create mapping of card numbers to image files"""
    image_mapping = {}
    card_images_dir = "card_images"
    
    # Check if card_images directory exists
    if os.path.exists(card_images_dir):
        for filename in os.listdir(card_images_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                # Extract card number from filename
                card_number = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename, flags=re.IGNORECASE)
                image_mapping[card_number] = os.path.join(card_images_dir, filename)
    
    return image_mapping

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load JSON file with multiple encoding attempts"""
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            st.error(f"File {filepath} not found.")
            return {}
        except json.JSONDecodeError as e:
            st.error(f"Error reading {filepath}: {e}")
            return {}
    
    st.error(f"Unable to read {filepath} with any supported encoding")
    return {}

# Card processing functions
def format_card_display(card: Dict[str, Any]) -> Dict[str, Any]:
    """Format card data for consistent display"""
    return {
        'name': card.get('name', 'Unknown'),
        'cardnumber': card.get('cardnumber', card.get('id', '')),
        'type': card.get('type', 'Unknown'),
        'color': card.get('color', 'Unknown'),
        'level': card.get('level', 'Unknown'),
        'play_cost': card.get('play_cost', 'Unknown'),
        'dp': card.get('dp', 'Unknown'),
        'rarity': card.get('rarity', 'Unknown'),
        'digi_type': card.get('digi_type', 'Unknown')
    }

def get_card_statistics(card_dict: Dict[str, Any]) -> Dict[str, int]:
    """Get statistics about card types in dictionary"""
    types = {}
    for card in card_dict.values():
        card_type = card.get('type', 'Unknown')
        types[card_type] = types.get(card_type, 0) + 1
    return types

# Deck validation functions
def validate_deck_rules(deck: List[Dict[str, Any]], egg_deck: List[Dict[str, Any]]) -> List[str]:
    """Validate deck according to Digimon TCG rules"""
    errors = []
    
    # Main deck rules
    if len(deck) != 50:
        errors.append(f"Main deck must have exactly 50 cards (has {len(deck)})")
    
    # Check card counts
    card_counts = {}
    for card in deck:
        card_number = card.get('cardnumber', '')
        if card_number:
            card_counts[card_number] = card_counts.get(card_number, 0) + 1
    
    for card_number, count in card_counts.items():
        if count > 4:
            errors.append(f"Card {card_number} has {count} copies (max 4 allowed)")
    
    # Check card types in main deck
    for card in deck:
        card_type = card.get('type', '')
        if card_type == 'Digi-Egg':
            errors.append("Digi-Egg cards not allowed in main deck")
    
    # Digi-Egg deck rules
    if len(egg_deck) > 5:
        errors.append(f"Digi-Egg deck can have maximum 5 cards (has {len(egg_deck)})")
    
    # Check Digi-Egg deck only contains Digi-Eggs
    for card in egg_deck:
        card_type = card.get('type', '')
        if card_type != 'Digi-Egg':
            errors.append("Only Digi-Egg cards allowed in Digi-Egg deck")
    
    return errors

def display_deck_statistics(deck: List[Dict[str, Any]]):
    """Display deck statistics"""
    if not deck:
        return
    
    # Calculate statistics
    types = {}
    colors = {}
    levels = {}
    
    for card in deck:
        # Type distribution
        card_type = card.get('type', 'Unknown')
        types[card_type] = types.get(card_type, 0) + 1
        
        # Color distribution
        color = card.get('color', 'Unknown')
        colors[color] = colors.get(color, 0) + 1
        
        # Level distribution
        level = str(card.get('level', 'Unknown'))
        levels[level] = levels.get(level, 0) + 1
    
    total = len(deck)
    
    # Display statistics
    col1s, col2s = st.columns(2)
    
    with col1s:
        st.write("**Card Types:**")
        for card_type, count in sorted(types.items()):
            percentage = (count / total) * 100
            st.write(f"• {card_type}: {count} ({percentage:.1f}%)")
    
    with col2s:
        st.write("**Colors:**")
        for color, count in sorted(colors.items()):
            percentage = (count / total) * 100
            st.write(f"• {color}: {count} ({percentage:.1f}%)")
    
    # Level distribution
    st.write("**Levels:**")
    for level, count in sorted(levels.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        percentage = (count / total) * 100
        st.write(f"• Level {level}: {count} ({percentage:.1f}%)")

# Session state management
def create_session_state_defaults():
    """Initialize default session state values"""
    defaults = {
        'current_deck': [],
        'digi_egg_deck': [],
        'deck_name': 'New Deck',
        'bookmarks': [],
        'search_history': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Deck management functions
def save_deck():
    """Save deck to session storage"""
    deck_data = {
        'deck_name': st.session_state.deck_name,
        'main_deck': st.session_state.current_deck,
        'digi_egg_deck': st.session_state.digi_egg_deck,
        'saved_at': pd.Timestamp.now().isoformat()
    }
    
    # Add to bookmarks (simplified - in real app would use proper storage)
    if 'saved_decks' not in st.session_state:
        st.session_state.saved_decks = []
    
    st.session_state.saved_decks.append(deck_data)
    st.success(f"Deck '{st.session_state.deck_name}' saved successfully!")

def export_deck():
    """Export deck as JSON"""
    deck_data = {
        'deck_name': st.session_state.deck_name,
        'main_deck': st.session_state.current_deck,
        'digi_egg_deck': st.session_state.digi_egg_deck
    }
    
    # Convert to JSON
    json_data = json.dumps(deck_data, indent=2, ensure_ascii=False)
    
    # Provide download
    st.download_button(
        label="📥 Download Deck JSON",
        data=json_data,
        file_name=f"{st.session_state.deck_name.replace(' ', '_')}_deck.json",
        mime="application/json"
    )

# Merge functions
def merge_card_data(main_dict: Dict[str, Any], new_cards: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, int]]:
    """Merge new cards into main dictionary, handling duplicates"""
    merged = main_dict.copy()
    duplicates = 0
    new_cards_added = 0
    updates = 0
    
    for card_number, card_data in new_cards.items():
        if card_number in merged:
            duplicates += 1
            # Compare data and update if new data is more complete
            existing_data = merged[card_number]
            
            # Check if new data has more fields
            new_fields = len([k for k in card_data.keys() if card_data[k] is not None and card_data[k] != ''])
            existing_fields = len([k for k in existing_data.keys() if existing_data[k] is not None and existing_data[k] != ''])
            
            if new_fields > existing_fields:
                merged[card_number] = card_data
                updates += 1
        else:
            merged[card_number] = card_data
            new_cards_added += 1
    
    # Sort dictionary by keys (card IDs) alphabetically
    sorted_merged = dict(sorted(merged.items()))
    
    return sorted_merged, {
        'new_cards_added': new_cards_added,
        'duplicates': duplicates,
        'updates': updates,
        'total_cards': len(sorted_merged)
    }

def save_merged_data(data: Dict[str, Any], filepath: str) -> str:
    """Save merged data with backup creation"""
    try:
        # Create backup of original file
        if os.path.exists(filepath):
            backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
            
            # Save merged data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return backup_path
        return None
    except Exception as e:
        st.error(f"Error saving merged data: {e}")
        return None

def get_card_statistics_for_merge(card_dict: Dict[str, Any]) -> Dict[str, int]:
    """Get statistics about card types in dictionary"""
    types = {}
    for card in card_dict.values():
        card_type = card.get('type', 'Unknown')
        types[card_type] = types.get(card_type, 0) + 1
    return types
