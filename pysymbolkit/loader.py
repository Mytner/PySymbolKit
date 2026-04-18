"""  
    PySymbolKit - A python package that semantically searches and displays Unicode symbols in various file types. 

    Copyright (C) 2026,  Abhishek Kumar

    email: abhishek.physics90@gmail.com
    website: https://mytner.github.io/Mesh-Writer-Support/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


    --------------------------------------------------------------------

    This project includes or depends on third-party components
    that are licensed separately:

    - emoji (BSD License)
    - Google Noto Fonts (Apache License 2.0)

    These components are not covered by the GPL license of Mesh Writer.
    See THIRD_PARTY_LICENSES.md for full license texts.

    --------------------------------------------------------------------


"""

"""
Info: Python file that handles loading and searching the emoji database from an external file.
It creates a cache to avoid reloading the database multiple times.
"""

# PyUniSymbols 


# CACHE VERSION OF THE DATABASE TO AVOID RELOADING MULTIPLE TIMES

import os
import json

# Cache for emoji database
# After the first load, the data is stored in the EMOJI_DATABASE_CACHE variable. 
# On subsequent calls, via other files/modules this cached data will be returned instead of reading the file again, 

_EMOJI_DATABASE_CACHE = None



# Excluding colored emojis (with skin tones), as they clutter the emojis results 
# and are not properly displayed in any emoji.
# See "P4 Colored emoji results" in problems.txt for more details
def is_colored_emoji(data):
    # Check for 'skin tone' in names or aliases
    for key in ("names", "aliases"):
        values = data.get(key)
        if values:
            if isinstance(values, dict):
                if any("skin tone" in v.lower() for v in values.values() if isinstance(v, str)):
                    return True
            elif isinstance(values, list):
                if any("skin tone" in v.lower() for v in values if isinstance(v, str)):
                    return True
    return False



def is_vs16_variant(emoji_key):
    # Exclude emoji keys that end with VS16 (U+FE0F)
    # Some emojis are getting represented twice in the UI either via search or through categories.
    # The cause: -->
    # For example emojis like 'coffin' or 'bed' are in two forms, one is uni-colored while the other is in color
    # But blender treats both the same, so I had to exclude the colored variant (with VS16)
    # See "P3 double results" in "problems.txt" for more details
    return emoji_key.endswith("\uFE0F")




def is_zwj_sequence(emoji_key):
        # Exclude emoji keys that contain ZWJ (U+200D)
        # Emojis like "Man in the lotus position" returns two emoji , the cause: it is a ZWJ sequence"
        # See "P5 Mixed symbols" in "problems.txt" for more details
        return "\u200D" in emoji_key


def load_emoji_database(category=None, exclude_colored_emojis=True, exclude_vs16_variant=True, exclude_zwj_sequences=True):
    """Load emoji data from external file, optionally filtered by category"""
    global _EMOJI_DATABASE_CACHE

    emoji_data = {}

    # If cache exists, use it instead of reloading
    if _EMOJI_DATABASE_CACHE is not None:
        all_emojis = _EMOJI_DATABASE_CACHE
    else:
        # Get addon directory path
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        database_path = os.path.join(addon_dir, "..", "data", "emoji_database.txt")

        try:
            with open(database_path, 'r', encoding='utf-8') as file:
                all_emojis = json.load(file)
                _EMOJI_DATABASE_CACHE = all_emojis  # Cache the data
        except FileNotFoundError:
            print(f"Warning: emoji_database.txt not found at {database_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}
        except Exception as e:
            print(f"Error loading emoji database: {e}")
            return {}

    # Now filter the emojis based on the provided parameters. 
    for emoji, data in all_emojis.items():
       
        if category and data.get("category") != category:
            continue
        if exclude_colored_emojis and is_colored_emoji(data):
            continue
        if exclude_vs16_variant and is_vs16_variant(emoji):
            continue
        if exclude_zwj_sequences and is_zwj_sequence(emoji):
            continue
        emoji_data[emoji] = data

    return emoji_data
