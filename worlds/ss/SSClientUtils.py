from typing import List, Optional

from NetUtils import HintStatus
BEEDLE_STAGE = "F002r"
# Location indices for Beedle checks (used for scouting their items)
BEEDLE_LEFTMOST_CHECKS = [41, 42, 43]
BEEDLE_LEFT_MIDDLE_CHECKS = [44, 45]
BEEDLE_RIGHT_MIDDLE_CHECKS = [46, 47, 48]
BEEDLE_RIGHTMOST_CHECKS = [49, 50]
BEEDLE_CHECKS = (
    BEEDLE_LEFTMOST_CHECKS,
    BEEDLE_LEFT_MIDDLE_CHECKS,
    BEEDLE_RIGHT_MIDDLE_CHECKS,
    BEEDLE_RIGHTMOST_CHECKS
)

CLIENT_TEXT_BUFFER_SIZE = 1000 # actually 1024 but the recv buffer isn't that big

# Time for a client message to disappear in-game (in seconds, not including stagger time for multiple lines in the queue)
CLIENT_TEXT_TIMEOUT = 10

# Max number of characters in a line for in-game client text
INGAME_LINE_LENGTH = 64

AP_VISITED_STAGE_NAMES_KEY_FORMAT = "ss_visited_stages_%i"

# Valid addresses for storyflags (ending in zero - final bit is added to this address)
VALID_STORYFLAG_ADDR = [
    0x805A9AD0,
    0x805A9AE0,
    0x805A9AF0,
    0x805A9B00,
    0x805A9B10,
    0x805A9B20,
    0x805A9B30,
]

# Addresses to the sceneflags saved on the current save file
STAGE_TO_SCENEFLAG_ADDR = {
    "Skyloft": 0x80956EC8,
    "Faron Woods": 0x80956ED8,
    "Lake Floria": 0x80956EE8,
    "Flooded Faron Woods": 0x80956EF8,
    "Eldin Volcano": 0x80956F08,
    "Boko Base/Volcano Summit": 0x80956F18,
    "Lanayru Desert": 0x80956F38,
    "Lanayru Sand Sea": 0x80956F48,
    "Lanayru Gorge": 0x80956F58,
    "Sealed Grounds": 0x80956F68,
    "Skyview": 0x80956F78,
    "Ancient Cistern": 0x80956F88,
    "Earth Temple": 0x80956FA8,
    "Fire Sanctuary": 0x80956FB8,
    "Lanayru Mining Facility": 0x80956FD8,
    "Sandship": 0x80956FE8,
    "Sky Keep": 0x80957008,
    "Sky": 0x80957018,
    "Faron Silent Realm": 0x80957028,
    "Eldin Silent Realm": 0x80957038,
    "Lanayru Silent Realm": 0x80957048,
    "Skyloft Silent Realm": 0x80957058,
}

# Used for batch lookup
STORYFLAG_START_ADDR = 0x805A9AD8
SCENEFLAG_START_ADDR = 0x80956EC8

# DME Connection Messages for the client
CONNECTION_REFUSED_GAME_STATUS = "Dolphin failed to connect. Please load a randomized ROM for Skyward Sword. Trying again in 5 seconds..."
CONNECTION_REFUSED_SAVE_STATUS = "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
CONNECTION_LOST_STATUS = "Dolphin connection was lost. Please restart your emulator and make sure Skyward Sword is running."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

CONSOLE_CONNECTED_STATUS = "Wii connected successfully."

COLOR_CONTROL_SEQUENCES = {
    # closest equivalents available in SS
    "black": "\x0e\x00\x03\x02\x0c",
    "red": "\x0e\x00\x03\x02\x01",
    "green": "\x0e\x00\x03\x02\x04",
    "yellow": "\x0e\x00\x03\x02\x0b",
    "blue": "\x0e\x00\x03\x02\x03",
    "magenta": "\x0e\x00\x03\x02\x29", # custom magenta added to the patcher
    "cyan": "\x0e\x00\x03\x02\x08",
    "slateblue": "\x0e\x00\x03\x02\x27", # custom slateblue added to the patcher
    "plum": "\x0e\x00\x03\x02\x06",
    "salmon": "\x0e\x00\x03\x02\x09",
    # "white": "\x0e\x00\x03\x02\x0a", # just ignore since text is already white by default
    "orange": "\x0e\x00\x03\x02\x02",
    # ">>": "\x0e\x00\x03\x02\uffff",  # end color
}

def _consume_control_sequence(text: str, index: int) -> Optional[str]:
    if index >= len(text) or text[index] != "\x0e":
        return None

    sequence_end = index + 5
    if sequence_end > len(text):
        return None

    return text[index:sequence_end]


def wrap_console_text(text: str, max_visible_chars: int = INGAME_LINE_LENGTH) -> List[str]:
    if max_visible_chars <= 0:
        return []

    wrapped_lines: List[str] = []
    current_line = ""
    visible_count = 0
    index = 0

    while index < len(text):
        sequence = _consume_control_sequence(text, index)
        if sequence is not None:
            current_line += sequence
            index += len(sequence)
            continue

        if visible_count >= max_visible_chars:
            wrapped_lines.append(current_line)
            current_line = ""
            visible_count = 0
            continue

        current_line += text[index]
        visible_count += 1
        index += 1

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines


def truncate_console_text(text: str, max_bytes: int) -> bytes:
    if max_bytes <= 0:
        return b""

    encoded_chunks: bytearray = bytearray()
    index = 0

    while index < len(text):
        sequence = _consume_control_sequence(text, index)
        if sequence is not None:
            encoded_sequence = sequence.encode("utf-8")
            if len(encoded_chunks) + len(encoded_sequence) > max_bytes:
                break

            encoded_chunks.extend(encoded_sequence)
            index += len(sequence)
            continue

        encoded_char = text[index].encode("utf-8")
        if len(encoded_chunks) + len(encoded_char) > max_bytes:
            break

        encoded_chunks.extend(encoded_char)
        index += 1

    return bytes(encoded_chunks)


class LocationForHint():
    """
    Docstring for LocationForHint
    """

    location: int
    player: int
    status: HintStatus

    def __init__(self, loc: int, plr: int, sts: int = 0):
        self.location = loc
        self.player = plr

        if sts == 0:
            self.status = HintStatus.HINT_UNSPECIFIED
        elif sts == 10:
            self.status = HintStatus.HINT_NO_PRIORITY
        elif sts == 20:
            self.status = HintStatus.HINT_AVOID
        elif sts == 30:
            self.status = HintStatus.HINT_PRIORITY
        else:
            self.status = HintStatus.HINT_UNSPECIFIED

    def __eq__(self, other):
        if not isinstance(other, LocationForHint):
            return False
        return self.location == other.location and self.player == other.player
    
    def __hash__(self):
        return hash((self.location, self.player))
