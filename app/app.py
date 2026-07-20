import streamlit as st
import json
import pandas as pd
from typing import List, Dict, Any
import requests
import os
import re
import time
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Digimon Deck Builder",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load card data
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
            return []
        except json.JSONDecodeError as e:
            st.error(f"Error reading card data file: {e}")
            return []
    
    st.error("Unable to read card data file with any supported encoding. File may be corrupted.")
    return []

# Load card image mapping
@st.cache_data
def load_image_mapping():
    """Create mapping of card numbers to image files"""
    image_mapping = {}
    card_images_dir = "card_images"
    
    # Check if card_images directory exists
    if not os.path.exists(card_images_dir):
        st.warning(f"Card images directory '{card_images_dir}' not found.")
        return image_mapping
    
    # Load card data to get all card numbers
    try:
        with open('digimon_cards_dict.json', 'r', encoding='utf-8') as f:
            cards_dict = json.load(f)
    except Exception as e:
        st.error(f"Error loading card data for image mapping: {e}")
        return image_mapping
    
    # Create mapping
    total_cards = len(cards_dict)
    found_images = 0
    
    for card_number in cards_dict.keys():
        image_path = os.path.join(card_images_dir, f"{card_number}.jpg")
        if os.path.exists(image_path):
            image_mapping[card_number] = image_path
            found_images += 1
    
    # Debug information
    st.info(f"Image mapping: {found_images}/{total_cards} cards have images")
    
    return image_mapping

# Fetch detailed card information from API
def fetch_card_details(card_number: str) -> List[Dict[str, Any]]:
    """Fetch detailed information for a specific card by card number"""
    url = f"https://digimoncard.io/api-public/search?card={card_number}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching details for card {card_number}: {e}")
        return []

def fetch_cards(key) -> List[Dict[str, Any]]:
    """Fetch detailed information for Key cards only"""
    with st.spinner(f'Fetching {key} card data...'):
        # First get all basic cards to find cards
        basic_cards_url = "https://digimoncard.io/api-public/getAllCards"
        
        try:
            response = requests.get(basic_cards_url)
            response.raise_for_status()
            basic_cards = response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching basic cards: {e}")
            return []
        
        # Filter for key cards only
        key_cards = []
        for card in basic_cards:
            card_number = card.get('cardnumber', '')
            if card_number.startswith(key):
                key_cards.append(card)
        
        st.info(f"Found {len(key_cards)} {key} cards")
        
        # Fetch detailed information for cards
        detailed_key_cards = []
        total_key = len(key_cards)
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, card in enumerate(key_cards):
            card_number = card.get('cardnumber')
            if not card_number:
                continue
                
            # Update progress
            progress = (i + 1) / total_key
            progress_bar.progress(progress)
            status_text.text(f"Processing {i+1}/{total_key}: {card_number} - {card.get('name', 'Unknown')}")
            
            # Fetch detailed card information
            detailed_info = fetch_card_details(card_number)
            
            if detailed_info:
                # Add all variants of this card
                for variant in detailed_info:
                    detailed_key_cards.append(variant)
            
            # Rate limiting
            if i % 5 == 0:
                time.sleep(2)
            else:
                time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return detailed_key_cards

def create_download_json(selected_cards: List[Dict[str, Any]]) -> str:
    """Create JSON string for download"""
    # Create a dictionary with card numbers as keys for consistency with main data
    cards_dict = {}
    for card in selected_cards:
        card_number = card.get('cardnumber', card.get('id', str(len(cards_dict))))
        cards_dict[card_number] = card
    
    return json.dumps(cards_dict, ensure_ascii=False, indent=2)

# Sidebar navigation
def sidebar():
    """Create sidebar navigation"""
    st.sidebar.title("🎴 Digimon Deck Builder")
    
    # Navigation options
    page = st.sidebar.radio(
        "Choose a page:",
        [
            "🔍 Card Lookup",
            "📚 Bookmarks",
            "📊 Deck Analysis",
            "🎯 Deck Builder",
            "🌐 Data Fetcher",
            "🔀 Data Merger",
            "⚙️ Settings"
        ]
    )
    
    return page

# Card Lookup Page
def card_lookup_page(cards_data: Dict[str, Dict[str, Any]], image_mapping: Dict[str, str]):
    """Display card lookup page"""
    st.header("🔍 Card Lookup")
    # Search options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("Search by name:", placeholder="Enter card name...")
    
    with col2:
        search_type = st.selectbox("Search type:", ["Contains", "Exact Match"])
    
    with col3:
        set_search = st.text_input("Search by set:", placeholder="e.g., BT5, EX1")
    
    # Additional filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_filter = st.selectbox("Filter by color:", ["All", "Red", "Blue", "Green", "Yellow", "Black", "Purple", "White"])
    
    with col2:
        type_filter = st.selectbox("Filter by type:", ["All", "Digimon", "Tamer", "Option"])
    
    with col3:
        rarity_filter = st.selectbox("Filter by rarity:", ["All", "C", "U", "R", "SR", "SEC", "PR"])
    
    # Search button
    search_button = st.button("🔍 Search Cards")
    
    if search_button or search_term or set_search:
        # Filter cards based on search criteria
        filtered_cards = []
        
        for card_number, card in cards_data.items():
            card_name = card.get('name', '').lower()
            search_lower = search_term.lower()
            set_search_lower = set_search.lower()
            
            # Name search (only if search term is provided)
            if search_term:
                if search_type == "Contains":
                    name_match = search_lower in card_name
                else:
                    name_match = card_name == search_lower
                
                if not name_match:
                    continue
            
            # Set search (only if set search is provided)
            if set_search:
                # Extract set abbreviation from card number
                if '-' in card_number:
                    card_set = card_number.split('-')[0].lower()
                    if set_search_lower != card_set:
                        continue
                else:
                    continue
            
            # Apply filters
            if color_filter != "All":
                if card.get('color', '').lower() != color_filter.lower():
                    continue
            
            if type_filter != "All":
                if card.get('type', '').lower() != type_filter.lower():
                    continue
            
            if rarity_filter != "All":
                if card.get('rarity', '').lower() != rarity_filter.lower():
                    continue
            
            # Add card_number to card info for display
            card_with_number = card.copy()
            card_with_number['cardnumber'] = card_number
            filtered_cards.append(card_with_number)
        
        # Display results
        if filtered_cards:
            st.success(f"Found {len(filtered_cards)} cards")
            
            # Create DataFrame for display
            df_data = []
            for card in filtered_cards:
                df_data.append({
                    'Name': card.get('name', 'N/A'),
                    'Card Number': card.get('cardnumber', 'N/A'),
                    'Type': card.get('type', 'N/A'),
                    'Color': card.get('color', 'N/A'),
                    'Level': card.get('level', 'N/A'),
                    'Play Cost': card.get('play_cost', 'N/A'),
                    'Evolution Cost': card.get('evolution_cost', 'N/A'),
                    'Rarity': card.get('rarity', 'N/A'),
                    'DP': card.get('dp', 'N/A'),
                    'Attribute': card.get('attribute', 'N/A'),
                    'Form': card.get('form', 'N/A'),
                    'Stage': card.get('stage', 'N/A')
                })
            
            df = pd.DataFrame(df_data)
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # Card details section
            st.subheader("Card Details")
            # Create unique options for multiselect
            card_options = []
            for card in filtered_cards:
                card_options.append({
                    'display_name': f"{card['name']} ({card['cardnumber']})",
                    'name': card['name'],
                    'cardnumber': card['cardnumber']
                })
            
            selected_card_names = st.multiselect(
                "Select cards to view details:",
                options=[card['display_name'] for card in card_options],
                default=[card['display_name'] for card in card_options]
            )
            
            if selected_card_names:
                # Find the selected cards (ensure no duplicates)
                selected_cards = []
                seen_display_names = set()
                
                for card in filtered_cards:
                    display_name = f"{card['name']} ({card['cardnumber']})"
                    if display_name in selected_card_names and display_name not in seen_display_names:
                        selected_cards.append(card)
                        seen_display_names.add(display_name)
                
                # Display each selected card
                for i, selected_card in enumerate(selected_cards, 1):
                    display_card_details(selected_card, image_mapping, show_bookmark=True)
        else:
            st.warning("No cards found matching your criteria.")

# Bookmarks Page
def bookmarks_page(cards_data: Dict[str, Dict[str, Any]], image_mapping: Dict[str, str]):
    """Display bookmarks page"""
    st.header("📚 Bookmarks")
    
    # Initialize session state for bookmarks
    if 'bookmarked_cards' not in st.session_state:
        st.session_state.bookmarked_cards = []
    
    # Display bookmarked cards
    if st.session_state.bookmarked_cards:
        st.success(f"You have {len(st.session_state.bookmarked_cards)} bookmarked cards")
        
        # Create expandable sections for each bookmarked card
        for i, card_number in enumerate(st.session_state.bookmarked_cards, 1):
            with st.expander(f"Card {i}: {card_number}", expanded=False):
                if card_number in cards_data:
                    card = cards_data[card_number].copy()
                    card['cardnumber'] = card_number
                    display_card_details(card, image_mapping, show_bookmark=False)
                    
                    # Remove bookmark button
                    if st.button(f"🗑️ Remove Bookmark", key=f"remove_{card_number}"):
                        st.session_state.bookmarked_cards.remove(card_number)
                        st.rerun()
                else:
                    st.warning(f"Card {card_number} not found in database")
    else:
        st.info("No bookmarked cards yet. Use the Card Lookup page to bookmark cards.")
    
    # Clear all bookmarks button
    if st.session_state.bookmarked_cards:
        if st.button("🗑️ Clear All Bookmarks", type="secondary"):
            st.session_state.bookmarked_cards = []
            st.rerun()

def display_card_details(card: Dict[str, Any], image_mapping: Dict[str, str], show_bookmark: bool = True):
    """Display detailed card information"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display card image if available
        card_number = card.get('cardnumber', '')
        if card_number and card_number in image_mapping:
            image_path = image_mapping[card_number]
            try:
                # Check if file exists before attempting to load
                if os.path.exists(image_path):
                    st.image(image_path, caption=f"{card.get('name', 'Unknown Card')}", width='content')
                else:
                    st.warning(f"Image file not found: {image_path}")
            except Exception as e:
                st.warning(f"Unable to load image for {card_number}: {str(e)}")
        else:
            st.info(f"No image available for card {card_number}")
    
    with col2:
        
        
        # Card classification and restrictions
        if card.get('card_text'):
            st.write(f"**Card Text:** {card.get('card_text', 'N/A')}")
        if card.get('restriction'):
            st.write(f"**Restriction:** {card.get('restriction', 'N/A')}")
        if card.get('security_effect'):
            st.write(f"**Security Effect:** {card.get('security_effect', 'N/A')}")
        
        # Database and external references
        if card.get('card_id'):
            st.write(f"**Card ID:** {card.get('card_id', 'N/A')}")
        if card.get('group'):
            st.write(f"**Group:** {card.get('group', 'N/A')}")
        if card.get('version'):
            st.write(f"**Version:** {card.get('version', 'N/A')}")
        
        # Special properties
        if card.get('special_property'):
            st.write(f"**Special Property:** {card.get('special_property', 'N/A')}")
        if card.get('ability'):
            st.write(f"**Ability:** {card.get('ability', 'N/A')}")
        if card.get('burst'):
            st.write(f"**Burst:** {card.get('burst', 'N/A')}")
        
        
        
    # Bookmark button (only show in card lookup page)
    if show_bookmark and card.get('cardnumber'):
        card_number = card.get('cardnumber')
        is_bookmarked = 'bookmarked_cards' in st.session_state and card_number in st.session_state.bookmarked_cards
        
        if is_bookmarked:
            if st.button("🔖 Bookmarked", key=f"bookmark_{card_number}", disabled=True):
                pass
        else:
            if st.button("🔖 Bookmark Card", key=f"bookmark_{card_number}"):
                if 'bookmarked_cards' not in st.session_state:
                    st.session_state.bookmarked_cards = []
                
                if card_number not in st.session_state.bookmarked_cards:
                    st.session_state.bookmarked_cards.append(card_number)
                    st.success(f"Bookmarked {card.get('name', 'Unknown Card')}")
                    st.rerun()
        
        # Card classification and restrictions
        if card.get('card_text'):
            st.write(f"**Card Text:** {card.get('card_text', 'N/A')}")
        if card.get('restriction'):
            st.write(f"**Restriction:** {card.get('restriction', 'N/A')}")
        if card.get('security_effect'):
            st.write(f"**Security Effect:** {card.get('security_effect', 'N/A')}")
        
        # Database and external references
        if card.get('card_id'):
            st.write(f"**Card ID:** {card.get('card_id', 'N/A')}")
        if card.get('group'):
            st.write(f"**Group:** {card.get('group', 'N/A')}")
        if card.get('version'):
            st.write(f"**Version:** {card.get('version', 'N/A')}")
        
        # Special properties
        if card.get('special_property'):
            st.write(f"**Special Property:** {card.get('special_property', 'N/A')}")
        if card.get('ability'):
            st.write(f"**Ability:** {card.get('ability', 'N/A')}")
        if card.get('burst'):
            st.write(f"**Burst:** {card.get('burst', 'N/A')}")
        
        # Additional basic fields that might be available
        if card.get('id') and card.get('id') != card.get('cardnumber'):
            st.write(f"**ID:** {card.get('id', 'N/A')}")
        if card.get('set_name'):
            if isinstance(card['set_name'], list):
                sets = ', '.join(card['set_name'][:3])  # Show first 3 sets
                if len(card['set_name']) > 3:
                    sets += f" (+{len(card['set_name']) - 3} more)"
        if card.get('link_requirements'):
            st.write(f"**Link Requirements:** {card.get('link_requirements', 'N/A')}")
        if card.get('link_dp'):
            st.write(f"**Link DP:** {card.get('link_dp', 'N/A')}")
    
    with col2:
        st.subheader("📜 Card Effects")
        
        # Main Effect
        main_effect = card.get('main_effect', '')
        if main_effect:
            with st.expander("**Main Effect**", expanded=True):
                # Format text within brackets with color but keep brackets
                formatted_effect = main_effect.replace('\r\n', '\n')
                # Add orange color to text within square brackets
                formatted_effect = re.sub(r'\[([^\]]+)\]', r'<font color="#FF6B35"><b>[\1]</b></font>', formatted_effect)
                # Add blue color to text within angle brackets
               
                st.markdown(formatted_effect, unsafe_allow_html=True)
        
        # Source Effect
        source_effect = card.get('source_effect', '')
        if source_effect:
            with st.expander("📚 Source Effect", expanded=False):
                formatted_effect = source_effect.replace('\r\n', '\n')
                formatted_effect = re.sub(r'\[([^\]]+)\]', r'<font color="#FF6B35"><b>[\1]</b></font>', formatted_effect)
                st.markdown(formatted_effect, unsafe_allow_html=True)
        
        # Alternative Effect
        alt_effect = card.get('alt_effect', '')
        if alt_effect:
            with st.expander("🔄 Alternative Effect", expanded=False):
                formatted_effect = alt_effect.replace('\r\n', '\n')
                formatted_effect = re.sub(r'\[([^\]]+)\]', r'<font color="#FF6B35"><b>[\1]</b></font>', formatted_effect)
                formatted_effect = re.sub(r'<([^>]+)>', r'<font color="#1E88E5"><b><\1></b></font>', formatted_effect)
                st.markdown(formatted_effect, unsafe_allow_html=True)
        
    # Digimon-specific information
        if card.get('type') == 'Digimon':
            st.subheader("⚔️ Digimon Stats")
            with st.expander("Show Digimon Stats"):
                # Core Digimon stats
                col1_digi, col2_digi = st.columns(2)
                with col1_digi:
                    st.write(f"**Level:** {card.get('level', 'N/A')}")
                    st.write(f"**Form:** {card.get('form', 'N/A')}")
                    st.write(f"**Attribute:** {card.get('attribute', 'N/A')}")
                    st.write(f"**DP:** {card.get('dp', 'N/A')}")

                with col2_digi:
                    st.write(f"**Play Cost:** {card.get('play_cost', 'N/A')}")
                    st.write(f"**Evolution Cost:** {card.get('evolution_cost', 'N/A')}")
                    if card.get('color2'):
                        st.write(f"**Color 2:** {card.get('color2', 'N/A')}")

                    # Card rarity indicator
                    rarity = card.get('rarity', '').upper()
                    if rarity:
                        rarity_colors = {
                            'C': '🟢 Common', 'U': '🔵 Uncommon', 
                            'R': '🔴 Rare', 'SR': '🟠 Super Rare', 
                            'SEC': '🟣 Secret Rare', 'PR': '🟣 Promo Rare'
                        }
                        st.write(f"**Rarity:** {rarity_colors.get(rarity, rarity)}")

                    # Digi-Types section
                    digi_types = []
                    for i in range(1, 5):
                        digi_type_key = f'digi_type{i}'
                        if card.get(digi_type_key):
                            digi_types.append(card.get(digi_type_key))

                    if digi_types:
                        st.write(f"**Digi-Types:** {', '.join(digi_types)}")

                    # Evolution requirements
                    evo_reqs = []
                    if card.get('evolution_color'):
                        evo_reqs.append(f"Color: {card.get('evolution_color')}")
                    if card.get('evolution_level'):
                        evo_reqs.append(f"Level: {card.get('evolution_level')}")
                    if card.get('xros_req'):
                        evo_reqs.append(f"Xros: {card.get('xros_req')}")

                    if evo_reqs:
                        st.write(f"**Evolution Requirements:** {', '.join(evo_reqs)}")
        

# Data Fetcher Page
def data_fetcher_page():
    """Display card fetcher page with download functionality"""
    st.header("Card Fetcher")
    
    st.write("Fetch and download card data from the digimoncard.io API")
    
    # Initialize session state for BT5 cards
    if 'fetch_cards' not in st.session_state:
        st.session_state.fetch_cards = []
    
    # Fetch BT5 cards button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        key = st.text_input("Key","BT5-")
        if st.button("Fetch Cards", type="primary"):
            key_cards = fetch_cards(key)
            if key_cards:
                st.session_state.fetch_cards = key_cards
                st.success(f"Successfully fetched {len(key_cards)} {key} cards!")
                st.rerun()
    
    with col2:
        if st.session_state.fetch_cards:
            st.info(f"Current {key} cards: {len(st.session_state.fetch_cards)}")
    
    # Display and select cards if available
    if st.session_state.fetch_cards:
        st.subheader("Select Cards for Download")
        
        # Create selection interface
        col_select, col_info = st.columns([2, 1])
        
        with col_select:
            # Create card options for selection
            card_options = []
            for card in st.session_state.fetch_cards:
                card_number = card.get('cardnumber', 'Unknown')
                card_name = card.get('name', 'Unknown Card')
                card_options.append(f"{card_name} ({card_number})")
            
            selected_indices = st.multiselect(
                "Select cards to download:",
                options=card_options,
                default=[],
                help="Choose which cards you want to download as JSON"
            )
        
        with col_info:
            st.write("**Selection Info**")
            st.write(f"Selected: {len(selected_indices)} cards")
            
            # Quick selection buttons
            if st.button("Select All"):
                # This will be handled via session state
                st.session_state.select_all = True
                st.rerun()
            
            if st.button("Clear Selection"):
                st.session_state.select_all = False
                st.session_state.selected_indices = []
                st.rerun()
        
        # Handle select all functionality
        if 'select_all' in st.session_state and st.session_state.select_all:
            selected_indices = card_options
            st.session_state.select_all = False
        
        # Display selected cards preview
        if selected_indices:
            st.subheader("Selected Cards Preview")
            
            # Get the actual card objects for selected indices
            selected_cards = []
            for i, option in enumerate(card_options):
                if option in selected_indices:
                    selected_cards.append(st.session_state.fetch_cards[i])
            
            # Create preview DataFrame
            preview_data = []
            for card in selected_cards:
                preview_data.append({
                    'Name': card.get('name', 'N/A'),
                    'Card Number': card.get('cardnumber', 'N/A'),
                    'Type': card.get('type', 'N/A'),
                    'Color': card.get('color', 'N/A'),
                    'Rarity': card.get('rarity', 'N/A')
                })
            
            preview_df = pd.DataFrame(preview_data)
            st.dataframe(preview_df, use_container_width=True)
            
            # Download section
            st.subheader("Download Options")
            
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                # Download as JSON
                json_data = create_download_json(selected_cards)
                st.download_button(
                    label="Download as JSON",
                    data=json_data,
                    file_name=f"{key}_selected_cards_{len(selected_cards)}_cards.json",
                    mime="application/json",
                    type="primary"
                )
            
            with col_download2:
                # Download as CSV
                csv_data = io.StringIO()
                preview_df.to_csv(csv_data, index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv_data.getvalue(),
                    file_name=f"bt5_selected_cards_{len(selected_indices)}_cards.csv",
                    mime="text/csv"
                )
            
            # Statistics for selected cards
            st.subheader("Selected Cards Statistics")
            
            types = {}
            colors = {}
            rarities = {}
            
            for card in selected_cards:
                card_type = card.get('type', 'Unknown')
                types[card_type] = types.get(card_type, 0) + 1
                
                color = card.get('color', 'Unknown')
                colors[color] = colors.get(color, 0) + 1
                
                rarity = card.get('rarity', 'Unknown')
                rarities[rarity] = rarities.get(rarity, 0) + 1
            
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.write("**By Type:**")
                for card_type, count in sorted(types.items()):
                    st.write(f"  {card_type}: {count}")
            
            with col_stats2:
                st.write("**By Color:**")
                for color, count in sorted(colors.items()):
                    st.write(f"  {color}: {count}")
            
            with col_stats3:
                st.write("**By Rarity:**")
                for rarity, count in sorted(rarities.items()):
                    st.write(f"  {rarity}: {count}")
        else:
            st.info("No cards selected. Please select cards from the list above to enable download.")
    
    else:
        st.info("No cards loaded yet. Click 'Fetch Cards' to get started.")

# Deck Analysis Page (placeholder)
def deck_analysis_page():
    """Display deck analysis page"""
    st.header("📊 Deck Analysis")
    st.info("Deck analysis functionality coming soon!")

# Deck Builder Page
def deck_builder_page():
    """Display comprehensive deck builder page"""
    st.header("🎯 Deck Builder")
    
    # Initialize session state for deck building
    if 'current_deck' not in st.session_state:
        st.session_state.current_deck = []
    if 'deck_name' not in st.session_state:
        st.session_state.deck_name = "New Deck"
    if 'saved_decks' not in st.session_state:
        st.session_state.saved_decks = {}
    if 'digi_egg_deck' not in st.session_state:
        st.session_state.digi_egg_deck = []
    
    # Load card data for deck builder
    cards_data = load_card_data()
    image_mapping = load_image_mapping()
    
    # Main deck builder interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔍 Card Selection")
        
        # Search interface
        search_term = st.text_input("Search cards:", placeholder="Enter card name...")
        
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            color_filter = st.selectbox("Color:", ["All", "Red", "Blue", "Green", "Yellow", "Black", "Purple", "White"])
        
        with col_filter2:
            type_filter = st.selectbox("Type:", ["All", "Digimon", "Tamer", "Option"])
        
        with col_filter3:
            level_filter = st.selectbox("Level:", ["All", "2", "3", "4", "5", "6", "7"])
        
        # Filter and display cards
        available_cards = []
        for card_number, card in cards_data.items():
            card_name = card.get('name', '').lower()
            search_lower = search_term.lower()
            
            # Apply search filter
            if search_term and search_lower not in card_name:
                continue
            
            # Apply other filters
            if color_filter != "All" and card.get('color', '').lower() != color_filter.lower():
                continue
            
            if type_filter != "All" and card.get('type', '').lower() != type_filter.lower():
                continue
            
            if level_filter != "All" and card.get('level', '') != level_filter:
                continue
            
            # Add card_number to card info
            card_with_number = card.copy()
            card_with_number['cardnumber'] = card_number
            available_cards.append(card_with_number)
        
        # Display available cards
        if available_cards:
            st.success(f"Found {len(available_cards)} cards")
            
            # Create card options for selection
            card_options = {}
            for card in available_cards:
                display_name = f"{card.get('name', 'Unknown')} ({card.get('cardnumber', 'N/A')})"
                card_options[display_name] = card
            
            selected_card_name = st.selectbox("Select a card to add:", list(card_options.keys()))
            
            # Show preview of selected card and allow quantity selection
            if selected_card_name:
                selected_card = card_options[selected_card_name]
                
                # Display card preview in a dedicated section
                st.subheader("Card Preview")
                col_preview1, col_preview2 = st.columns([1, 2])
                
                with col_preview1:
                    # Display card image if available
                    image_mapping = load_image_mapping()
                    card_number = selected_card.get('cardnumber', '')
                    if card_number in image_mapping:
                        st.image(image_mapping[card_number], width=150)
                    else:
                        st.write("🎴 No Image")
                
                with col_preview2:
                    st.write(f"**{selected_card.get('name', 'Unknown')}**")
                    st.write(f"**Type:** {selected_card.get('type', 'Unknown')}")
                    st.write(f"**Color:** {selected_card.get('color', 'Unknown')}")
                    st.write(f"**Level:** {selected_card.get('level', 'Unknown')}")
                    st.write(f"**Cost:** {selected_card.get('play_cost', 'Unknown')}")
                    st.write(f"**DP:** {selected_card.get('dp', 'Unknown')}")
                    st.write(f"**Rarity:** {selected_card.get('rarity', 'Unknown')}")
                    
                    # Add main effects
                    if selected_card.get('main_effect'):
                        st.write("**Main Effect:**")
                        st.write(selected_card.get('main_effect', ''))
                    
                    # Add inherited effects
                    if selected_card.get('inherited_effect'):
                        st.write("**Inherited Effect:**")
                        st.write(selected_card.get('inherited_effect', ''))
                    
                    # Add source effect if available
                    if selected_card.get('source_effect'):
                        st.write("**Source Effect:**")
                        st.write(selected_card.get('source_effect', ''))
                    

                if "current_count" not in st.session_state:
                    st.session_state.current_count = {card_number: 0}

                if card_number not in st.session_state.current_count:
                    st.session_state.current_count[card_number] = 0

                # Quantity selection (moved to second column)
                with col_preview2:
                    st.write("**Add Quantity:**")
                    quantity = st.number_input(
                        "Number to add:",
                        min_value=0,
                        max_value=4,
                        value=1,
                        step=1
                    )
                
                # Add to Deck button (moved to third column)
                with col_preview2:
                    if st.button("➕ Add to Deck", type="primary"):
                        add_card_to_deck(selected_card, quantity)
        else:
            st.warning("No cards found matching your criteria.")
    
    with col2:
        st.subheader("📋 Current Deck")
        
        # Deck name input
        new_deck_name = st.text_input("Deck Name:", value=st.session_state.deck_name)
        if new_deck_name != st.session_state.deck_name:
            st.session_state.deck_name = new_deck_name
        
        # Deck validation
        validation_result = validate_deck(st.session_state.current_deck)
        
        if validation_result['valid']:
            st.success("✅ Deck is Valid!")
        else:
            st.error("❌ Deck has Issues:")
            for issue in validation_result['issues']:
                st.write(f"• {issue}")
        
        # Deck statistics
        display_deck_statistics(st.session_state.current_deck)
        
        # Current deck list
        st.subheader("Deck Cards")
        if st.session_state.current_deck:
            # Group cards by name for display
            deck_counts = {}
            for card in st.session_state.current_deck:
                card_name = card.get('name', 'Unknown')
                card_number = card.get('cardnumber', 'N/A')
                key = f"{card_name} ({card_number})"
                if key not in deck_counts:
                    deck_counts[key] = {'card': card, 'count': 0}
                deck_counts[key]['count'] += 1
            
            # Display cards with remove buttons
            for i, (card_key, card_info) in enumerate(deck_counts.items()):
                col_card, col_count, col_remove = st.columns([2, 1, 1])
                
                with col_card:
                    # Display card image if available
                    card_number = card_info['card'].get('cardnumber', '')
                    if card_number in image_mapping:
                        st.image(image_mapping[card_number], width=80)
                    else:
                        st.write("🎴")
                
                with col_card:
                    st.write(f"**{card_key}**")
                
                with col_count:
                    st.write(f"x{card_info['count']}")
                
                with col_remove:
                    if st.button("🗑️", key=f"remove_{i}"):
                        remove_card_from_deck(card_info['card'])
            
            # Clear deck button
            if st.button("🗑️ Clear Deck", type="secondary"):
                st.session_state.current_deck = []
                st.rerun()
        else:
            st.info("Deck is empty. Add cards from the left panel.")
        
        # Save/Load deck section
        st.subheader("💾 Deck Management")
        col_save, col_load = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Deck", type="primary"):
                save_deck()
        
        with col_load:
            if st.session_state.saved_decks:
                deck_to_load = st.selectbox("Load deck:", list(st.session_state.saved_decks.keys()))
                if st.button("📂 Load"):
                    load_deck(deck_to_load)
        
        # Export/Import section
        st.subheader("📤 Export/Import")
        col_export, col_import = st.columns(2)
        
        with col_export:
            if st.button("📤 Export Deck"):
                export_deck()
        
        with col_import:
            uploaded_file = st.file_uploader("📥 Import Deck", type=['json'])
            if uploaded_file:
                import_deck(uploaded_file)
    
    # Digi-Egg deck section
    st.subheader("🥚 Digi-Egg Deck (0-5 cards)")
    col_egg1, col_egg2 = st.columns([2, 1])
    
    with col_egg1:
        # Filter for Digi-Egg cards only
        digi_egg_cards = []
        for card_number, card in cards_data.items():
            if card.get('type') == 'Digi-Egg':
                card_with_number = card.copy()
                card_with_number['cardnumber'] = card_number
                digi_egg_cards.append(card_with_number)
        
        if digi_egg_cards:
            egg_options = {f"{card.get('name', 'Unknown')} ({card.get('cardnumber', 'N/A')})": card 
                          for card in digi_egg_cards}
            selected_egg = st.selectbox("Select Digi-Egg:", list(egg_options.keys()))
            
            if selected_egg and st.button("➕ Add Digi-Egg"):
                if len(st.session_state.digi_egg_deck) < 5:
                    st.session_state.digi_egg_deck.append(egg_options[selected_egg])
                    st.rerun()
                else:
                    st.error("Digi-Egg deck can have maximum 5 cards")
        else:
            st.info("No Digi-Egg cards found in database.")
    
    with col_egg2:
        st.write(f"Current: {len(st.session_state.digi_egg_deck)}/5")
        
        # Display current Digi-Egg deck
        for i, egg_card in enumerate(st.session_state.digi_egg_deck):
            col_egg_name, col_egg_remove = st.columns([3, 1])
            with col_egg_name:
                st.write(f"**{egg_card.get('name', 'Unknown')}**")
            with col_egg_remove:
                if st.button("🗑️", key=f"remove_egg_{i}"):
                    st.session_state.digi_egg_deck.pop(i)
                    st.rerun()
        
        if st.button("🗑️ Clear Digi-Eggs"):
            st.session_state.digi_egg_deck = []
            st.rerun()

def add_card_to_deck(card , value_to_add):
    """Add a card to the current deck"""
    # Check if deck already has 50 cards
    if len(st.session_state.current_deck) >= 50:
        st.error("Deck cannot have more than 50 cards!")
        return
    
    # Check card copy limit
    card_number = card.get('cardnumber', '')
    check_count = value_to_add + st.session_state.current_count[card_number]
    
    if check_count > 4:
        st.error(f"Cannot add more than 4 copies of {card.get('name', 'Unknown')}!")
        return
    
    # Add card to deck
    # Calculate current count of this card in deck
    st.session_state.current_count[card_number] = sum(1 for c in st.session_state.current_deck 
                       if c.get('cardnumber', '') == card_number)
    
    for _ in range(value_to_add):
        st.session_state.current_deck.append(card)
    st.success(f"Added {card.get('name', 'Unknown')} to deck!")
    st.rerun()

def remove_card_from_deck(card):
    """Remove one copy of a card from the deck"""
    card_number = card.get('cardnumber', '')
    for i, deck_card in enumerate(st.session_state.current_deck):
        if deck_card.get('cardnumber', '') == card_number:
            st.session_state.current_deck.pop(i)
            st.success(f"Removed {card.get('name', 'Unknown')} from deck!")
            st.rerun()
            break

def validate_deck(deck):
    """Validate deck according to Digimon TCG rules"""
    issues = []
    
    # Check deck size
    if len(deck) != 50:
        if len(deck) < 50:
            issues.append(f"Deck has {len(deck)} cards (needs exactly 50)")
        else:
            issues.append(f"Deck has {len(deck)} cards (maximum 50)")
    
    # Check card copy limits
    card_counts = {}
    for card in deck:
        card_number = card.get('cardnumber', '')
        card_counts[card_number] = card_counts.get(card_number, 0) + 1
    
    for card_number, count in card_counts.items():
        if count > 4:
            # Find card name for display
            card_name = "Unknown"
            for card in deck:
                if card.get('cardnumber', '') == card_number:
                    card_name = card.get('name', 'Unknown')
                    break
            issues.append(f"{card_name} has {count} copies (maximum 4)")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }

def display_deck_statistics(deck):
    """Display detailed deck statistics"""
    if not deck:
        st.info("No cards in deck")
        return
    
    # Calculate statistics
    total_cards = len(deck)
    card_types = {}
    colors = {}
    levels = {}
    rarities = {}
    
    for card in deck:
        # Type distribution
        card_type = card.get('type', 'Unknown')
        card_types[card_type] = card_types.get(card_type, 0) + 1
        
        # Color distribution
        color = card.get('color', 'Unknown')
        colors[color] = colors.get(color, 0) + 1
        
        # Level distribution (for Digimon)
        level = card.get('level', 'N/A')
        if level != 'N/A':
            levels[level] = levels.get(level, 0) + 1
        
        # Rarity distribution
        rarity = card.get('rarity', 'Unknown')
        rarities[rarity] = rarities.get(rarity, 0) + 1
    
    # Display statistics
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.write("**Card Types:**")
        for card_type, count in sorted(card_types.items()):
            percentage = (count / total_cards) * 100
            st.write(f"  {card_type}: {count} ({percentage:.1f}%)")
    
    with col_stats2:
        st.write("**Colors:**")
        for color, count in sorted(colors.items()):
            percentage = (count / total_cards) * 100
            st.write(f"  {color}: {count} ({percentage:.1f}%)")
    
    with col_stats3:
        st.write("**Levels:**")
        for level, count in sorted(levels.items()):
            percentage = (count / total_cards) * 100
            st.write(f"  Lv.{level}: {count} ({percentage:.1f}%)")
    
    # Progress bar for deck completion
    progress = total_cards / 50
    st.progress(progress)
    st.write(f"Deck Progress: {total_cards}/50 cards ({progress*100:.1f}%)")

def save_deck():
    """Save current deck to session state"""
    if not st.session_state.deck_name:
        st.error("Please enter a deck name!")
        return
    
    validation_result = validate_deck(st.session_state.current_deck)
    if not validation_result['valid']:
        st.error("Cannot save invalid deck!")
        return
    
    # Create deck data
    deck_data = {
        'name': st.session_state.deck_name,
        'main_deck': st.session_state.current_deck,
        'digi_egg_deck': st.session_state.digi_egg_deck,
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    # Save to session state
    st.session_state.saved_decks[st.session_state.deck_name] = deck_data
    st.success(f"Deck '{st.session_state.deck_name}' saved successfully!")

def load_deck(deck_name):
    """Load a saved deck"""
    if deck_name in st.session_state.saved_decks:
        deck_data = st.session_state.saved_decks[deck_name]
        st.session_state.deck_name = deck_data['name']
        st.session_state.current_deck = deck_data['main_deck']
        st.session_state.digi_egg_deck = deck_data.get('digi_egg_deck', [])
        st.success(f"Loaded deck '{deck_name}'!")
        st.rerun()
    else:
        st.error(f"Deck '{deck_name}' not found!")

def export_deck():
    """Export current deck as JSON file"""
    if not st.session_state.current_deck:
        st.error("No deck to export!")
        return
    
    # Create export data
    export_data = {
        'deck_name': st.session_state.deck_name,
        'version': '1.0',
        'format': 'digimon_tcg_deck',
        'main_deck': [],
        'digi_egg_deck': st.session_state.digi_egg_deck,
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    # Add main deck cards with counts
    card_counts = {}
    for card in st.session_state.current_deck:
        card_number = card.get('cardnumber', '')
        if card_number not in card_counts:
            card_counts[card_number] = {
                'card_number': card_number,
                'name': card.get('name', 'Unknown'),
                'count': 0,
                'type': card.get('type', 'Unknown'),
                'color': card.get('color', 'Unknown')
            }
        card_counts[card_number]['count'] += 1
    
    export_data['main_deck'] = list(card_counts.values())
    
    # Convert to JSON
    json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    # Create download
    st.download_button(
        label=f"📥 Download {st.session_state.deck_name}.json",
        data=json_data,
        file_name=f"{st.session_state.deck_name.replace(' ', '_')}_deck.json",
        mime="application/json"
    )

def import_deck(uploaded_file):
    """Import deck from JSON file"""
    try:
        # Read uploaded file
        content = uploaded_file.read().decode('utf-8')
        deck_data = json.loads(content)
        
        # Validate format
        if 'main_deck' not in deck_data:
            st.error("Invalid deck file format!")
            return
        
        # Load cards data for validation
        cards_data = load_card_data()
        
        # Import main deck
        imported_deck = []
        for card_entry in deck_data['main_deck']:
            card_number = card_entry.get('card_number', '')
            count = card_entry.get('count', 1)
            
            if card_number in cards_data:
                card = cards_data[card_number].copy()
                card['cardnumber'] = card_number
                
                # Add the specified number of copies
                for _ in range(min(count, 4)):  # Enforce 4-copy limit
                    imported_deck.append(card)
        
        # Import Digi-Egg deck if present
        imported_egg_deck = []
        if 'digi_egg_deck' in deck_data:
            for egg_card in deck_data['digi_egg_deck']:
                if isinstance(egg_card, dict):
                    card_number = egg_card.get('card_number', '')
                else:
                    card_number = str(egg_card)
                
                if card_number in cards_data and cards_data[card_number].get('type') == 'Digi-Egg':
                    card = cards_data[card_number].copy()
                    card['cardnumber'] = card_number
                    imported_egg_deck.append(card)
        
        # Set the imported deck
        st.session_state.current_deck = imported_deck
        st.session_state.digi_egg_deck = imported_egg_deck
        st.session_state.deck_name = deck_data.get('deck_name', 'Imported Deck')
        
        st.success(f"Successfully imported deck '{st.session_state.deck_name}' with {len(imported_deck)} cards!")
        st.rerun()
        
    except json.JSONDecodeError:
        st.error("Invalid JSON file!")
    except Exception as e:
        st.error(f"Error importing deck: {str(e)}")

# Data Merger Functions
def load_json_for_merge(filepath: str) -> Dict[str, Any]:
    """Load JSON file with multiple encoding attempts for merge"""
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            st.error(f"Error reading {filepath}: Invalid JSON format")
            return {}
    
    st.error(f"Unable to read {filepath} with any supported encoding")
    return {}

def merge_card_data_in_app(main_dict: Dict[str, Any], new_cards: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, int]]:
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

# Data Merger Page
def data_merger_page():
    """Display data merger page"""
    st.header("🔀 Data Merger")
    st.markdown("Merge new Digimon card data into the main dictionary.")
    
    # File selection section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 File Selection")
        
        # Main file (fixed)
        main_file = "digimon_cards_dict.json"
        st.info(f"Main Dictionary: `{main_file}`")
        
        # Input file selection
        input_method = st.radio(
            "Input Method",
            ["Select Existing File", "Upload New File"],
            horizontal=True
        )
        
        input_file = None
        
        if input_method == "Select Existing File":
            # List available JSON files (excluding main file)
            json_files = [f for f in os.listdir('.') if f.endswith('.json') and f != main_file]
            if json_files:
                input_file = st.selectbox(
                    "Select JSON File to Merge",
                    options=json_files,
                    help="Choose JSON file containing new card data"
                )
            else:
                st.warning("No JSON files found in current directory")
        
        else:  # Upload New File
            uploaded_file = st.file_uploader(
                "Upload JSON File",
                type=['json'],
                help="Upload a JSON file containing Digimon card data"
            )
            if uploaded_file is not None:
                # Save uploaded file temporarily
                temp_path = f"temp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(uploaded_file.getvalue().decode('utf-8'))
                input_file = temp_path
                st.success(f"File uploaded: {uploaded_file.name}")
    
    with col2:
        st.subheader("📊 Current Status")
        
        # Show main file info
        if os.path.exists(main_file):
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    main_data = json.load(f)
                st.metric("Main Cards", len(main_data))
                
                # Show card type distribution
                main_stats = get_card_statistics_for_merge(main_data)
                for card_type, count in sorted(main_stats.items())[:5]:  # Show top 5
                    st.write(f"• {card_type}: {count}")
            except:
                st.error("Unable to read main file")
        else:
            st.error("Main file not found")
    
    # Merge section
    if input_file and os.path.exists(main_file):
        st.subheader("🔄 Merge Operations")
        
        # Load files and show preview
        with st.spinner("Loading files..."):
            main_dict = load_json_for_merge(main_file)
            new_cards = load_json_for_merge(input_file)
        
        if main_dict and new_cards:
            # Preview section
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🆕 New Cards Preview**")
                st.metric("Cards to Merge", len(new_cards))
                
                # Show sample cards
                sample_cards = list(new_cards.items())[:3]
                for card_id, card_data in sample_cards:
                    with st.expander(f"{card_id} - {card_data.get('name', 'Unknown')}"):
                        st.write(f"Type: {card_data.get('type', 'Unknown')}")
                        st.write(f"Color: {card_data.get('color', 'Unknown')}")
                        st.write(f"Level: {card_data.get('level', 'Unknown')}")
            
            with col2:
                st.write("**📈 Merge Impact**")
                
                # Calculate potential merge stats
                potential_new = len([cid for cid in new_cards.keys() if cid not in main_dict])
                potential_duplicates = len([cid for cid in new_cards.keys() if cid in main_dict])
                
                st.metric("Potential New Cards", potential_new)
                st.metric("Potential Duplicates", potential_duplicates)
                
                # Show card type distribution for new cards
                new_stats = get_card_statistics_for_merge(new_cards)
                st.write("**New Card Types:**")
                for card_type, count in sorted(new_stats.items()):
                    st.write(f"• {card_type}: {count}")
            
            # Merge button
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Perform Merge", type="primary", use_container_width=True):
                    with st.spinner("Merging cards..."):
                        merged_dict, merge_stats = merge_card_data_in_app(main_dict, new_cards)
                        
                        # Save merged data
                        backup_path = save_merged_data(merged_dict, main_file)
                        
                        if backup_path:
                            st.success("✅ Merge completed successfully!")
                            
                            # Show results
                            st.subheader("📈 Merge Results")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("New Cards Added", merge_stats['new_cards_added'])
                            with col2:
                                st.metric("Duplicates Found", merge_stats['duplicates'])
                            with col3:
                                st.metric("Updates Made", merge_stats['updates'])
                            with col4:
                                st.metric("Total Cards", merge_stats['total_cards'])
                            
                            st.info(f"📁 Backup created: `{backup_path}`")
                            
                            # Show final statistics
                            final_stats = get_card_statistics_for_merge(merged_dict)
                            st.subheader("📊 Final Card Distribution")
                            
                            # Create a nice table for statistics
                            stats_df = pd.DataFrame([
                                {'Card Type': card_type, 'Count': count}
                                for card_type, count in sorted(final_stats.items())
                            ])
                            st.dataframe(stats_df, use_container_width=True)
                            
                            # Reload card data cache
                            st.cache_data.clear()
                            st.info("🔄 Card data cache cleared. Please refresh the page to see updated data.")
                            
                        else:
                            st.error("❌ Failed to create backup. Merge aborted.")
        else:
            st.error("❌ Failed to load one or both files. Please check file paths and formats.")
    else:
        st.info("👈 Please select files to begin the merge process.")
    
    # Cleanup temporary files
    if input_method == "Upload New File" and input_file and input_file.startswith("temp_upload_"):
        if os.path.exists(input_file):
            os.remove(input_file)

# Settings Page (placeholder)
def settings_page():
    """Display settings page"""
    st.header("⚙️ Settings")
    st.info("Settings functionality coming soon!")

# Main application
def main():
    """Main application function"""
    # Load card data
    cards_data = load_card_data()
    
    if not cards_data:
        st.error("Unable to load card data. Please check your data files.")
        return
    
    # Load image mapping
    image_mapping = load_image_mapping()
    
    # Get selected page from sidebar
    page = sidebar()
    
    # Display selected page
    if page == "🔍 Card Lookup":
        card_lookup_page(cards_data, image_mapping)
    elif page == "📚 Bookmarks":
        bookmarks_page(cards_data, image_mapping)
    elif page == "📊 Deck Analysis":
        deck_analysis_page()
    elif page == "🎯 Deck Builder":
        deck_builder_page()
    elif page == "🌐 Data Fetcher":
        data_fetcher_page()
    elif page == "🔀 Data Merger":
        data_merger_page()
    elif page == "⚙️ Settings":
        settings_page()

if __name__ == "__main__":
    main()
