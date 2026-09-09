import asyncio
import copy
from dataclasses import dataclass
from enum import IntEnum
import time
import traceback
import textwrap
import socket
import struct
import threading
from typing import TYPE_CHECKING, Any, List, Optional
import typing

import Utils
from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from NetUtils import ClientStatus, NetworkItem, JSONtoTextParser, HintStatus

from .Items import ITEM_TABLE, LOOKUP_ID_TO_NAME
from .Locations import LOCATION_TABLE, SSLocation, SSLocFlag, SSLocType, SSLocCheckedFlag
from .Hints import HINT_TABLE, SSHint
from .Cubes import cubes_table
from .SSClientUtils import *

LOCALHOST_IP = "127.0.0.1"

class VerbosityLevel(IntEnum):
    Nothing = 0
    Items = 1
    ItemsChat = 2
    ItemsChatJoins = 3
    All = 4

if TYPE_CHECKING:
    import kvui

class APStatusReport:
    def __init__(self, stage_name: bytes = b'', last_received_item: int = 0, link_exists: bool = False,
                 is_on_title_screen: bool = False, is_dead: bool = False, is_out_of_stamina: bool = False):
        self.stage_name = (stage_name if len(stage_name) == 16 else stage_name.ljust(16, b'\x00')[:16])
        self.last_received_item = last_received_item
        self.link_exists = link_exists
        self.is_on_title_screen = is_on_title_screen
        self.is_dead = is_dead
        self.is_out_of_stamina = is_out_of_stamina
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'APStatusReport':
        """Create APStatusReport from bytes (big endian)"""
        if len(data) < 22:
            raise ValueError(f"Expected at least 22 bytes, got {len(data)}")
        
        stage_name = data[0:16]
        last_received_item, = struct.unpack('>H', data[16:18])
        link_exists = bool(data[18])
        is_on_title_screen = bool(data[19])
        is_dead = bool(data[20])
        is_out_of_stamina = bool(data[21])
        
        return cls(stage_name, last_received_item, link_exists, is_on_title_screen, is_dead, is_out_of_stamina)

class AsyncUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, client):
        self.client: AsyncWiiMemoryClient = client
        
    def datagram_received(self, data, addr):
        self.client.handle_response(data)
    
    def error_received(self, exc):
        print(f"UDP error: {exc}")
        self.client.established = False

class CommandRequest:
    def __init__(self, payload: bytes, timeout: float = 10.0, retries: int = 2):
        self.payload = payload
        self.timeout = timeout
        self.retries = retries
        self.future = asyncio.Future()
        self.timestamp = time.time()
        self.seq: Optional[int] = None

class AsyncWiiMemoryClient:
    def __init__(self, wii_ip, port=43673):
        self.wii_ip = wii_ip
        self.port = port
        self.transport = None
        self.protocol = None
        self.established = False
        # Number of additional attempts after the first try (total attempts = retry_count + 1)
        self.retry_count: int = 2
        # Base backoff in seconds; exponential backoff will be applied between retries
        self.retry_backoff: float = 0.2

        # Queue for UDP queries to the wii
        self.command_queue: asyncio.Queue[CommandRequest] = asyncio.Queue()
        self.pending_requests: dict[int, CommandRequest] = {}
        self.next_seq: int = 0
        self.current_request: Optional[CommandRequest] = None
        self.queue_processor_task = None
        
    async def connect(self):
        """Establish connection to Wii"""
        try:
            loop = asyncio.get_event_loop()
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: AsyncUDPProtocol(self),
                remote_addr=(self.wii_ip, self.port)
            )
            sock = self.transport.get_extra_info('socket')
            self.my_ip = sock.getsockname()[0]
            self.my_port = sock.getsockname()[1]

            self.queue_processor_task = asyncio.create_task(self._process_command_queue())
            
            # Send IP / port info so the Wii can write back
            try:
                await self.establish_connection()
                self.established = True
                return True
            except asyncio.TimeoutError:
                self.established = False
                return False
                
        except Exception as e:
            print(f"Connection failed: {e}")
            self.established = False
            return False

    async def disconnect(self):
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
            try:
                await self.queue_processor_task
            except asyncio.CancelledError:
                pass

        for request in list(self.pending_requests.values()):
            if not request.future.done():
                request.future.set_exception(asyncio.CancelledError())
        self.pending_requests.clear()
        self.current_request = None
        
        if self.transport:
            self.transport.close()
            
        self.established = False

    async def establish_connection(self, timeout=1):
        """Try to send a packet with IP and Port to establish connection to Wii server"""
        payload = b'\x00' + socket.inet_aton(self.my_ip) + struct.pack('>H', self.my_port)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return True
        else:
            raise Exception(f"Establishing UDP connection failed")
    
    async def _send_command_queued(self, payload: bytes, timeout=2, retries: Optional[int] = None) -> bytes:
        if retries is None:
            retries = self.retry_count

        request = CommandRequest(payload, timeout, retries)
        await self.command_queue.put(request)
        # once the command queue process this, return the result
        return await request.future

    def _next_seq(self) -> int:
        seq = self.next_seq
        self.next_seq = (self.next_seq + 1) & 0xFFFF
        return seq

    def _build_packet(self, seq: int, payload: bytes) -> bytes:
        packet = struct.pack('>H', seq) + payload
        return packet

    def _parse_response(self, data: bytes) -> tuple[int, bytes]:
        if len(data) < 3:
            raise ValueError(f"Response too short to contain sequence and payload ({len(data)} bytes)")
        seq, = struct.unpack('>H', data[:2])
        return seq, data[2:]

    async def _process_command_queue(self):
        while True:
            try:
                request = await self.command_queue.get()
                if request.future.cancelled():
                    continue

                request.seq = self._next_seq()
                self.pending_requests[request.seq] = request
                success = False
                for attempt in range(request.retries + 1):
                    if request.future.cancelled():
                        break

                    self.current_request = request
                    packet = self._build_packet(request.seq, request.payload)
                    self.transport.sendto(packet)

                    try:
                        # Wait for handle_response to fire
                        await asyncio.wait_for(
                            asyncio.shield(request.future), 
                            timeout=request.timeout
                        )
                        success = True
                        break
                    except asyncio.TimeoutError:
                        if request.future.done():
                            success = True
                            break
                        self.current_request = None
                        if attempt < request.retries:
                            backoff = self.retry_backoff * (2 ** attempt)
                            print(f"Timeout attempt {attempt+1}, retrying in {backoff}s")
                            await asyncio.sleep(backoff)

                self.pending_requests.pop(request.seq, None)
                self.current_request = None

                if not success and not request.future.done():
                    request.future.set_exception(asyncio.TimeoutError())

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.current_request and not self.current_request.future.done():
                    self.current_request.future.set_exception(e)

    def handle_response(self, data):
        """Handle incoming UDP response"""
        try:
            seq, payload = self._parse_response(data)
        except ValueError:
            print(f"Received malformed UDP response: {data}")
            return

        request = self.pending_requests.pop(seq, None)
        if request is not None and not request.future.done():
            request.future.set_result(payload)
            if request is self.current_request:
                self.current_request = None
        else:
            print(f"Received unexpected response seq={seq}: {payload}")
    
    async def req_scene_flags(self, timeout=2) -> bytes:
        """Request the scene flag array from the Wii."""
        payload = struct.pack('>B', 0x03)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) == 416:
            return response
        else:
            raise Exception(f"Reading scene flags failed.")
    
    async def req_story_flags(self, timeout=2) -> bytes:
        """Request the story flag array from the Wii."""
        payload = struct.pack('>B', 0x04)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) == 256:
            return response
        else:
            raise Exception(f"Reading story flags failed.")
    
    async def signal_dc(self, timeout=2) -> bytes:
        """Send a signal to the Wii that the client lost connection"""
        payload = struct.pack('>B', 0x05)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return response
        else:
            raise Exception(f"Read failed at address")

    async def req_slot_name(self, timeout=2) -> str:
        """Request the AP slot name from the Wii."""
        payload = struct.pack('>B', 0x06)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            slot_bytes = response.replace(b"\xFF", b"")
            return slot_bytes.decode('utf-8').rstrip("\x00")
        else:
            raise Exception(f"Slot read failed.")
        
    async def req_status(self, timeout=2) -> APStatusReport:
        """Request some player status info from the Wii."""
        payload = struct.pack('>B', 0x07)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return APStatusReport.from_bytes(response)
        else:
            raise Exception(f"Slot read failed.")
    
    async def give_item(self, item_id, timeout=2) -> APStatusReport:
        """(Try to) tell the Wii to give the player an item (& recv new status report)."""
        payload = struct.pack('>BB', 0x08, item_id)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return APStatusReport.from_bytes(response)
        else:
            raise Exception(f"Item give failed.")
    
    async def kill_link(self, timeout=2) -> bool:
        """Tell the Wii that it should kill Link."""
        payload = struct.pack('>B', 0x09)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return response[0] == 1
        else:
            raise Exception(f"Kill Link failed.")
    
    async def deplete_stamina(self, timeout=2) -> bool:
        """Tell the Wii that it should deplete Link's stamina."""
        payload = struct.pack('>B', 0x0a)
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return response[0] == 1
        else:
            raise Exception(f"Deplete stamina failed.")
    
    async def write_to_text_buffer(self, text: bytes, timeout=2) -> bool:
        """Write to the in-game text buffer on the Wii."""
        payload = struct.pack('>B', 0x0b) + text
        
        response = await self._send_command_queued(payload, timeout)
        
        if len(response) > 0:
            return response[0] == 0x0b
        else:
            raise Exception(f"Write to text buffer failed.")
    
    def close(self):
        """Close connection"""
        self.established = False
        if self.transport:
            self.transport.close()
            self.transport = None

@dataclass
class BatchFlagHandler:
    flags: bytes
    base_addr: int
    def lookup_byte(self, addr: int) -> int:
        offset = addr - self.base_addr
        assert(offset >= 0)
        return self.flags[offset]

    def lookup_long(self, addr: int) -> int:
        offset = addr - self.base_addr
        assert(offset >= 0)
        return (self.flags[offset + 3]) + \
            (self.flags[offset + 2] << 8) + \
            (self.flags[offset + 1] << 16) + \
            (self.flags[offset] << 24)

class SSIngameJSONParser(JSONtoTextParser):
    def _handle_color(self, node):
        codes = node["color"].split(";")
        buffer = "".join(COLOR_CONTROL_SEQUENCES[code] for code in codes if code in COLOR_CONTROL_SEQUENCES)
        return buffer + self._handle_text(node) + "\x0e\x00\x03\x02\uffff"

class SSCommandProcessor(ClientCommandProcessor):
    """
    Command Processor for SS client commands.
    """

    def __init__(self, ctx: CommonContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)
    
    def _cmd_console(self, ip_addr: str) -> None:
        """
        Connect to a console, using the IP address shown in-game (must be on the same network).
        """
        if isinstance(self.ctx, SSContext):
            logger.info(f"Starting up a Wii client...")
            self.ctx.wii_ip = ip_addr
            self.ctx.store_ip_in_cache()
            self.ctx.start_wii_client(ip_addr)
    
    def _cmd_emulator(self) -> None:
        """
        Alias for /console 127.0.0.1; connects to localhost.
        """
        if isinstance(self.ctx, SSContext):
            logger.info(f"Starting up a Wii client...")
            self.ctx.wii_ip = LOCALHOST_IP
            self.ctx.store_ip_in_cache()
            self.ctx.start_wii_client(LOCALHOST_IP)
            
    def _cmd_deathlink(self) -> None:
        """Toggle DeathLink."""
        if isinstance(self.ctx, SSContext):
            if "DeathLink" in self.ctx.tags:
                Utils.async_start(self.ctx.update_death_link(False))
                logger.info("Deathlink disabled.")
            else:
                Utils.async_start(self.ctx.update_death_link(True))
                logger.info("Deathlink enabled.")
    
    def _cmd_breathlink(self) -> None:
        """Toggle BreathLink."""
        if isinstance(self.ctx, SSContext):
            if "BreathLink" in self.ctx.tags:
                Utils.async_start(self.ctx.update_breath_link(False))
                logger.info("Breathlink disabled.")
            else:
                Utils.async_start(self.ctx.update_breath_link(True))
                logger.info("Breathlink enabled.")

    def _cmd_msg_forwarding(self, verbosity_level: str) -> None:
        """
        Specify what kinds of messages should be displayed in-game.
        None - No client messages
        Low - Items sent to/received from this slot
        Medium - Chat messages & items sent to/received from this slot
        High - Chat messages, items sent to/received from this slot, & players joining/leaving
        All - All client messages
        """
        if isinstance(self.ctx, SSContext):
            lvl = verbosity_level.strip().lower()
            verbosity = None
            if lvl == "none":
                verbosity = VerbosityLevel.Nothing
                logger.info("No client messages will appear in-game.")
            elif lvl == "low":
                verbosity = VerbosityLevel.Items
                logger.info("Items sent to/received from this slot will appear in-game.")
            elif lvl == "medium":
                verbosity = VerbosityLevel.ItemsChat
                logger.info("Chat messages & items sent to/received from this slot will appear in-game.")
            elif lvl == "high":
                verbosity = VerbosityLevel.ItemsChatJoins
                logger.info("Chat messages, items sent to/received from this slot, & players joining/leaving will appear in-game.")
            elif lvl == "all":
                verbosity = VerbosityLevel.All
                logger.info("All client messages will appear in-game.")

            if verbosity is None:
                logger.error("Error - Please select a verbosity level: none, low, medium, high, or all.")
            else:
                self.ctx.ingame_verbosity = verbosity
                self.ctx.store_message_level_in_cache()

    def _cmd_clear_msgs(self) -> None:
        """
        Clears out the in-game client message buffer. Might be useful in case of a release that causes a lot of text to block the screen.
        """
        if isinstance(self.ctx, SSContext):
            self.ctx.ingame_client_messages.clear()
            self.ctx.clear_buffer()
            logger.info("Cleared out the in-game message buffer.")


class SSContext(CommonContext):
    """
    The context for the SS client.

    Manages the connection between the server and the game.
    """

    command_processor = SSCommandProcessor
    game: str = "Skyward Sword"
    items_handling: int = 0b001

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the SS context.

        :param server_address: Address of the Archipelago server.
        :param password: Password for server authentication.
        """

        super().__init__(server_address, password)
        self.items_rcvd: list[tuple[NetworkItem, int]] = []
        self.sync_task: Optional[asyncio.Task[None]] = None
        self.awaiting_rom: bool = False
        self.last_rcvd_index: int = -1
        self.has_send_death: bool = False
        self.last_breath_link: float = time.time()  # last send/received breath link on AP layer
        self.has_send_breath: bool = False
        self.locations_for_hint: dict[str, list] = {}

        self.hints_checked = set()  # local variable
        self.checked_hints = set()  # server variable
        self.beedle_items_purchased = [0, 0, 0, 0]  # slots from left to right
        self.cubes_checked = set() #local variable
        
        self.ingame_client_messages: list[tuple[float, str]] = []
        self.ingame_verbosity: VerbosityLevel = self.load_message_level_from_cache() # what kind of messages to forward to the game
        self.wii_memory_client: AsyncWiiMemoryClient = None
        self.wii_ip: str = self.load_ip_from_cache()
        self.socket = None # Server socket
        self.client_socket = None # Connection from Wii
        self.ingame_json_parser = SSIngameJSONParser(self)
        self.is_text_buffer_empty = True
        self.status_report = APStatusReport()

        # Name of the current stage as read from the game's memory. Sent to trackers whenever its value changes to
        # facilitate automatically switching to the map of the current stage.
        self.current_stage_name: str = ""

        # Set of visited stages. A dictionary (used as a set) of all visited stages is set in the server's data storage
        # and updated when the player visits a new stage for the first time. To track which stages are new and need to
        # cause the server's data storage to update, the TWW AP Client keeps track of the visited stages in a set.
        # Trackers can request the dictionary from data storage to see which stages the player has visited.
        # It starts as `None` until it has been read from the server.
        self.visited_stage_names: Optional[set[str]] = None

        self.len_item_buffer = 14 # length of the item ring buffer in-game

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        """
        Disconnect the client from the server and reset game state variables.

        :param allow_autoreconnect: Allow the client to auto-reconnect to the server. Defaults to `False`.

        """
        self.auth = None
        self.salvage_locations_map = {}
        self.current_stage_name = ""
        self.visited_stage_names = None
        await super().disconnect(allow_autoreconnect)

    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        :param password_requested: Whether the server requires a password. Defaults to `False`.
        """
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        if not self.auth:
            if self.awaiting_rom:
                return
            self.awaiting_rom = True
            logger.info("Awaiting connection to the game to get player information.")
            return
        await self.send_connect()
    
    async def update_breath_link(self, breath_link: bool):
        """Helper function to set Breath Link connection tag on/off and update the connection if already connected."""
        old_tags = self.tags.copy()
        if breath_link:
            self.tags.add("BreathLink")
        else:
            self.tags -= {"BreathLink"}
        if old_tags != self.tags and self.server and not self.server.socket.closed:
            await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        """
        Handle incoming packages from the server.

        :param cmd: The command received from the server.
        :param args: The command arguments.
        """
        if cmd == "Connected":
            self.items_rcvd = []
            self.last_rcvd_index = -1
            self.locations_for_hint = args["slot_data"]["locations_for_hint"]
            if "death_link" in args["slot_data"]:
                Utils.async_start(
                    self.update_death_link(bool(args["slot_data"]["death_link"]))
                )
            if "breath_link" in args["slot_data"]:
                Utils.async_start(
                    self.update_breath_link(bool(args["slot_data"]["breath_link"]))
                )
            # Request the connected slot's dictionary (used as a set) of visited stages.
            visited_stages_key = AP_VISITED_STAGE_NAMES_KEY_FORMAT % self.slot
            Utils.async_start(
                self.send_msgs([{"cmd": "Get", "keys": [visited_stages_key]}])
            )
        elif cmd == "ReceivedItems":
            if args["index"] >= self.last_rcvd_index:
                self.last_rcvd_index = args["index"]
                for item in args["items"]:
                    self.items_rcvd.append((item, self.last_rcvd_index))
                    self.last_rcvd_index += 1
            self.items_rcvd.sort(key=lambda v: v[1])
        elif cmd == "Retrieved":
            requested_keys_dict = args["keys"]
            # Read the connected slot's dictionary (used as a set) of visited stages.
            if self.slot is not None:
                visited_stages_key = AP_VISITED_STAGE_NAMES_KEY_FORMAT % self.slot
                if visited_stages_key in requested_keys_dict:
                    visited_stages = requested_keys_dict[visited_stages_key]
                    # If it has not been set before, the value in the response will be `None`.
                    visited_stage_names = (
                        set() if visited_stages is None else set(visited_stages.keys())
                    )
                    # If the current stage name is not in the set, send a message to update the dictionary on the
                    # server.
                    current_stage_name = self.current_stage_name
                    if (
                        current_stage_name
                        and current_stage_name not in visited_stage_names
                    ):
                        visited_stage_names.add(current_stage_name)
                        Utils.async_start(
                            self.update_visited_stages(current_stage_name)
                        )
                    self.visited_stage_names = visited_stage_names
        elif cmd == "Bounced":
            tags = args.get("tags", [])
            # we can skip checking "DeathLink" in ctx.tags, as otherwise we wouldn't have been send this
            if "BreathLink" in tags and self.last_breath_link != args["data"]["time"]:
                self.on_breathlink(args["data"])
    
    def on_breathlink(self, data: typing.Dict[str, typing.Any]) -> None:
        """Gets dispatched when a new BreathLink is triggered by another linked player."""
        self.last_breath_link = max(data["time"], self.last_breath_link)
        text = data.get("cause", "")
        if text:
            logger.info(f"BreathLink: {text}")
        else:
            logger.info(f"BreathLink: Received from {data['source']}")
        
        asyncio.create_task(self._deplete_stamina())

    async def send_breath(self, breath_text: str = ""):
        """Helper function to send a breathlink using breath_text as the unique breath cause string."""
        if self.server and self.server.socket:
            logger.info("BreathLink: Taking your friends' breath away...")
            self.last_breath_link = time.time()
            await self.send_msgs([{
                "cmd": "Bounce", "tags": ["BreathLink"],
                "data": {
                    "time": self.last_breath_link,
                    "source": self.player_names[self.slot],
                    "cause": breath_text
                }
            }])
    
    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.

        :param data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        asyncio.create_task(self._give_death())

    def make_gui(self) -> type["kvui.GameManager"]:
        """
        Initialize the GUI for SS client.

        :return: The client's GUI.
        """
        ui = super().make_gui()
        ui.base_title = "Archipelago Skyward Sword Client"
        return ui

    async def update_visited_stages(self, newly_visited_stage_name: str) -> None:
        """
        Update the server's data storage of the visited stage names to include the newly visited stage name.

        :param newly_visited_stage_name: The name of the stage recently visited.
        """
        if self.slot is not None:
            visited_stages_key = AP_VISITED_STAGE_NAMES_KEY_FORMAT % self.slot
            await self.send_msgs(
                [
                    {
                        "cmd": "Set",
                        "key": visited_stages_key,
                        "default": {},
                        "want_reply": False,
                        "operations": [
                            {
                                "operation": "update",
                                "value": {newly_visited_stage_name: True},
                            }
                        ],
                    }
                ]
            )

    def forward_client_message(self, msg: str):
        lines = []
        for raw_line in msg.split("\n"):
            lines.extend(
                wrap_console_text(
                    raw_line,
                    INGAME_LINE_LENGTH,
                )
            )

        timestamp = time.time()
        # We want to stagger the messages so large amounts of text can "scroll"
        # if they go over the character limit
        for line in lines:
            self.ingame_client_messages.append(
                (timestamp + len(self.ingame_client_messages) * 0.5, line)
            )

    async def show_messages_ingame(self) -> None:
        # Filter out old messages
        line_list = []
        filtered_msgs = []
        curr_timestamp = time.time()
        for tup in self.ingame_client_messages:
            if curr_timestamp - tup[0] > CLIENT_TEXT_TIMEOUT:
                continue

            filtered_msgs.append(tup)
            line_list.append(tup[1])

        self.ingame_client_messages = filtered_msgs

        if len(line_list) == 0:
            await self.clear_buffer()
        else:
            # Want to cap it at 16 lines so the text doesn't get too obtrusive
            # (which could happen if each line is quite short)
            await self.write_string_to_buffer("\n".join(line_list[:16]))

    def on_print_json(self, args: dict):
        should_forward = self.ingame_verbosity == VerbosityLevel.All
        if self.ingame_verbosity == VerbosityLevel.ItemsChatJoins and \
            not self.is_uninteresting_item_send(args):
            should_forward = True
        if self.ingame_verbosity == VerbosityLevel.ItemsChat and \
            not self.is_uninteresting_item_send(args) and \
            not self.is_connection_change(args):
            should_forward = True
        if self.ingame_verbosity == VerbosityLevel.Items and \
            not self.is_uninteresting_item_send(args) and \
            args.get("type", "") == "ItemSend":
            should_forward = True

        if should_forward:
            self.forward_client_message(self.ingame_json_parser(copy.deepcopy(args["data"])))       

        super().on_print_json(args)
    
    async def write_string_to_buffer(self, text: str):
        text_bytes = truncate_console_text(text, CLIENT_TEXT_BUFFER_SIZE)
        await self.wii_memory_client.write_to_text_buffer(text_bytes + b'\x00')
        self.is_text_buffer_empty = False
    
    async def clear_buffer(self):
        if self.is_text_buffer_empty:
            return
        
        await self.wii_memory_client.write_to_text_buffer(b"\x00")
        self.is_text_buffer_empty = True

    
    def start_wii_client(self, ip):
        """Initialize the async Wii client"""
        if self.wii_memory_client:
            self.wii_memory_client.close()
        self.wii_memory_client = AsyncWiiMemoryClient(ip)
    
    async def close_wii_client(self):
        """Close Wii client connection"""
        if self.wii_memory_client:
            # if self.wii_memory_client.established:
            #    await self.wii_memory_client.signal_dc()
            self.wii_memory_client.close()
            self.wii_memory_client = None
    
    def is_hooked(self):
        return self.wii_memory_client and self.wii_memory_client.established

    async def _give_death(self) -> None:
        """
        Trigger the player's death in-game by setting their current health to zero.
        """
        if (
            self.slot is not None
            and self.is_hooked()
            and self.status_report.link_exists
            # and not await self.check_in_minigame()
        ):
            await self.wii_memory_client.kill_link()
            self.has_send_death = True
    
    async def _deplete_stamina(self) -> None:
        """
        Deplete the player's stamina in-game by setting their current stamina to zero.
        """
        if (
            self.slot is not None
            and self.is_hooked()
            and self.status_report.link_exists
        ):
            await self.wii_memory_client.deplete_stamina()
            self.has_send_breath = True


    async def _give_item(self, item_name: str) -> bool:
        """
        Give an item to the player in-game.

        :param ctx: The SS client context.
        :param item_name: Name of the item to give.
        :return: Whether the item was successfully given.
        """
        if not self.can_receive_items():
            return False
        
        curr_expected = self.status_report.last_received_item

        item_id = ITEM_TABLE[item_name].item_id  # In game item ID

        # Read the item slot, and place the item here if the slot is empty.
        # When the game confirms the player received the item, it'll clear out this slot again.
        self.status_report = await self.wii_memory_client.give_item(item_id)

        # If unable to give the item, then the last received item would have changed.
        return self.status_report.last_received_item > curr_expected


    async def give_items(self) -> None:
        """
        Give the player all outstanding items they have yet to receive.

        :param ctx: The SS client context.
        """
        if self.can_receive_items():
            # Read the expected index of the player, which is the index of the latest item they've received.

            # Loop through items to give.
            for item, idx in self.items_rcvd:
                # If the item's index is greater than the player's expected index, give the player the item.
                if self.status_report.last_received_item <= idx:
                    # Attempt to give the item and increment the expected index
                    # if we can't receive items right now, just return and move on so the rest of the process
                    # doesn't get stuck
                    if not await self._give_item(LOOKUP_ID_TO_NAME[item.item]):
                        return

    async def check_locations(self) -> None:
        """
        Loops through all locations and checks the sceneflag/storyflag(s) associated with the location in the location table.

        If Hylia's Realm - Defeat Demise is checked, update the server that this player has beaten the game.
        Otherwise, send the list of checked locations to the server.

        :param ctx: The SS client context.
        """
        # Don't send locations from the title screen (BiT)
        if self.can_send_items():
            storyflags = BatchFlagHandler(await self.wii_memory_client.req_story_flags(), STORYFLAG_START_ADDR)
            sceneflags = BatchFlagHandler(await self.wii_memory_client.req_scene_flags(), SCENEFLAG_START_ADDR)
            # Loop through all locations to see if each has been checked.
            for location, data in LOCATION_TABLE.items():
                checked = False
                [flag_type, flag_bit, flag_value, addr] = data.checked_flag
                if flag_type == SSLocCheckedFlag.STORY:
                    flag = storyflags.lookup_byte(addr + flag_bit)
                    checked = bool(flag & flag_value)
                elif flag_type == SSLocCheckedFlag.SCENE:
                    flag = sceneflags.lookup_byte(STAGE_TO_SCENEFLAG_ADDR[addr] + flag_bit)
                    checked = bool(flag & flag_value)
                elif flag_type == SSLocCheckedFlag.SPECL:
                    if location == "Upper Skyloft - Ghost/Pipit's Crystals":
                        byte = storyflags.lookup_byte(0x805A9B16)
                        flag1 = bool(byte & 0x80)  # 5 crystals from Pipit
                        flag2 = bool(byte & 0x04)  # 5 crystals from Ghost
                        checked = flag1 or flag2
                    if location == "Central Skyloft - Peater/Peatrice's Crystals":
                        bytelong = storyflags.lookup_long(0x805A9B1A)
                        flag1 = bool(
                            bytelong & 0x40000000
                        )  # 5 crystals from Peatrice
                        flag2 = bool(bytelong & 0x02)  # 5 crystals from Peater
                        checked = flag1 or flag2

                if checked:
                    if data.code is None:  # Defeat Demise
                        if not self.finished_game:
                            await self.send_msgs(
                                [{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]
                            )
                            self.finished_game = True
                    else:
                        self.locations_checked.add(SSLocation.get_apid(data.code))
                        for slot, checks in enumerate(BEEDLE_CHECKS):
                            if self.beedle_items_purchased[slot] < len(BEEDLE_CHECKS[slot]) - 1:
                                self.beedle_items_purchased[slot] += (data.code == checks[self.beedle_items_purchased[slot]])
                                
            
            for hint, data in HINT_TABLE.items():
                [flag_bit, flag_value, addr] = data.checked_flag
                # All hint flags are story flags
                flag = storyflags.lookup_byte(addr + flag_bit)
                checked = bool(flag & flag_value)

                if checked or self.finished_game:
                    for loc, plr, sts in self.locations_for_hint.get(hint, []):
                        self.hints_checked.add(LocationForHint(loc, plr, sts))

            for i, (name, (flag_bit, flag_value, addr)) in enumerate(cubes_table):
                flag = storyflags.lookup_byte(addr + flag_bit)
                checked = bool(flag & flag_value)

                if checked and i not in self.cubes_checked:
                    self.cubes_checked.add(i)

                    bit = 1 << i
                    await self.send_msgs([{
                        "cmd": "Set",
                        "key": f"skyward_sword_cubes_{self.team}_{self.slot}",
                        "default": 0,
                        "want_reply": True,
                        "operations": [{"operation": "or", "value": bit}],
                    }])

            # Send the list of newly-checked locations & hints to the server.
            locations_checked = self.locations_checked.difference(self.checked_locations)
            hints_checked = self.hints_checked.difference(self.checked_hints)
            if locations_checked:
                await self.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}]) 
            if hints_checked:
                for hint in hints_checked:
                    await self.send_msgs([{"cmd": "CreateHints", "locations": [hint.location], "player": hint.player, "status": hint.status}])

            self.checked_hints |= hints_checked


    async def check_current_stage_changed(self) -> None:
        """
        Check if the player has moved to a new stage.
        If so, update all trackers with the new stage name.
        If the stage has never been visited, additionally update the server.

        :param ctx: The SS client context.
        """
        new_stage_name = self.status_report.stage_name.split(b'\x00')[0].decode('utf-8')

        current_stage_name = self.current_stage_name

        if new_stage_name != current_stage_name:
            if new_stage_name == BEEDLE_STAGE:
                await self.scout_beedle_checks()
            self.current_stage_name = new_stage_name
            # Send a Bounced message containing the new stage name to all trackers connected to the current slot.
            data_to_send = {"ss_stage_name": new_stage_name}
            message = {
                "cmd": "Bounce",
                "slots": [self.slot],
                "data": data_to_send,
            }
            await self.send_msgs([message])

            # If the stage has never been visited before, update the server's data storage to indicate that it has been
            # visited.
            visited_stage_names = self.visited_stage_names
            if (
                visited_stage_names is not None
                and new_stage_name not in visited_stage_names
            ):
                visited_stage_names.add(new_stage_name)
                await self.update_visited_stages(new_stage_name)

    async def scout_beedle_checks(self) -> None:
        locs_to_scout = set()
        for slot, purchased_idx in enumerate(self.beedle_items_purchased):
            if len(BEEDLE_CHECKS[slot]) > purchased_idx:
                locs_to_scout.add(SSLocation.get_apid(BEEDLE_CHECKS[slot][purchased_idx]))
        
        await self.send_msgs([{"cmd": "LocationScouts", "locations": locs_to_scout, "create_as_hint": 2}]) 

    async def check_death(self) -> None:
        """
        Check if the player is currently dead in-game.
        If DeathLink is on, notify the server of the player's death.

        :return: `True` if the player is dead, otherwise `False`.
        """
        if self.slot is not None and self.status_report.link_exists and not self.status_report.is_on_title_screen:
            if self.status_report.is_dead:
                if not self.has_send_death and time.time() >= self.last_death_link + 3:
                    self.has_send_death = True
                    await self.send_death(self.player_names[self.slot] + " ran out of hearts.")
            else:
                self.has_send_death = False
    
    async def check_out_of_breath(self) -> None:
        """
        Check if the player is out of stamina
        If BreathLink is on, notify the server of the player's breathlessness.

        :return: `True` if the player is out of stamina, otherwise `False`.
        """
        if self.slot is not None and self.status_report.link_exists and not self.status_report.is_on_title_screen:
            if self.status_report.is_out_of_stamina:
                if not self.has_send_breath and time.time() >= self.last_breath_link + 3:
                    self.has_send_breath = True
                    await self.send_breath(self.player_names[self.slot] + " ran out of stamina.")
            else:
                self.has_send_breath = False
    
    async def cache_status(self):
        self.status_report = await self.wii_memory_client.req_status()

    def can_receive_items(self) -> bool:
        """
        Link must meet all the item sending conditions, and be alive, to receive items.
        """

        return (
            self.can_send_items()
            and not self.status_report.is_dead
        )

    def can_send_items(self) -> bool:
        """
        Link must not be on the tile screen to send items.
        """
        return not self.status_report.is_on_title_screen

    def store_ip_in_cache(self):
        current_cache = Utils.persistent_load().get("groups_by_checksum", {}).get(self.checksums[self.game], {})
        ip_entry = {"console_ip_address": self.wii_ip}
        if self.game in current_cache:
            current_cache[self.game].update(ip_entry)
        else:
            current_cache[self.game] = ip_entry
        Utils.persistent_store("groups_by_checksum", self.checksums[self.game], current_cache, True)

    def load_ip_from_cache(self) -> str:
        current_cache = Utils.persistent_load().get("groups_by_checksum", {}).get(self.checksums[self.game], {})
        if self.game in current_cache:
            return current_cache[self.game].get("console_ip_address", LOCALHOST_IP)
        else:
            return LOCALHOST_IP

    def store_message_level_in_cache(self):
            current_cache = Utils.persistent_load().get("groups_by_checksum", {}).get(self.checksums[self.game], {})
            verbosity = {"message_verbosity": self.ingame_verbosity}
            if self.game in current_cache:
                current_cache[self.game].update(verbosity)
            else:
                current_cache[self.game] = verbosity
            Utils.persistent_store("groups_by_checksum", self.checksums[self.game], current_cache, True)
    
    def load_message_level_from_cache(self) -> VerbosityLevel:
        current_cache = Utils.persistent_load().get("groups_by_checksum", {}).get(self.checksums[self.game], {})
        if self.game in current_cache:
            return current_cache[self.game].get("message_verbosity", VerbosityLevel.Nothing)
        else:
            return VerbosityLevel.ItemsChatJoins # this was the old verbosity level

async def do_sync_task(ctx: SSContext) -> None:
    """
    Manages the connection to the game.

    While connected, send some commands over the socket to the console to look for any relevant changes made by the player in the game.

    :param ctx: The SS client context.
    """
    if ctx.wii_ip == LOCALHOST_IP:
        logger.info("Attempting to connect to localhost; if you're on an emulator this should connect you, otherwise, type /console (IP address shown in-game) to continue.")
    else:
        logger.info(f"Attempting to connect to the console (using last used IP address {ctx.wii_ip}); if your console's IP address has changed, type /console (new IP address shown in-game) to continue.")

    lvl = ctx.ingame_verbosity
    if lvl == VerbosityLevel.Nothing:
        logger.info("Msg forwarding set to None, so no client messages will appear in-game.")
    elif lvl == VerbosityLevel.ItemsChat:
            logger.info("Msg forwarding set to Low, so items sent to/received from this slot will appear in-game.")
    elif lvl == VerbosityLevel.ItemsChat:
        logger.info("Msg forwarding set to Medium, so chat messages & items sent to/received from this slot will appear in-game.")
    elif lvl == VerbosityLevel.ItemsChatJoins:
        logger.info("Msg forwarding set to High, so chat messages, items sent to/received from this slot, & players joining/leaving will appear in-game.")
    elif lvl == VerbosityLevel.All:
        logger.info("Msg forwarding set to All, so all client messages will appear in-game.")
    logger.info("You may change this with the /msg_forwarding command.")
    while not ctx.exit_event.is_set():
        try:
            if ctx.is_hooked():
                await ctx.show_messages_ingame()
                
                if ctx.slot is not None:
                    await ctx.cache_status()
                    if not ctx.status_report.link_exists:
                        await asyncio.sleep(0.1)
                        continue
                    if "DeathLink" in ctx.tags:
                        await ctx.check_death()
                    if "BreathLink" in ctx.tags:
                        await ctx.check_out_of_breath()
                    await ctx.give_items()
                    await ctx.check_locations()
                    await ctx.check_current_stage_changed()
                else:
                    if not ctx.auth:
                        ctx.auth = await ctx.wii_memory_client.req_slot_name()
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                await asyncio.sleep(0.1)
            else:
                logger.info("Attempting to connect to the console...")
                await ctx.close_wii_client()
                ctx.start_wii_client(ctx.wii_ip)
                await ctx.wii_memory_client.connect()

                if ctx.wii_memory_client.established:
                    logger.info(CONSOLE_CONNECTED_STATUS)
                    ctx.locations_checked = set()
                    await ctx.cache_status()
                else:
                    logger.info(
                        "Connection to console failed, attempting again in 5 seconds..."
                    )
                    await asyncio.sleep(5)
                    continue
        except TimeoutError:
            print("Lost packet from console, attempting to reconnect...")
            await ctx.close_wii_client()
            ctx.start_wii_client(ctx.wii_ip)
            if not await ctx.wii_memory_client.connect():
                logger.info("Lost packet from console and couldn't reconnect. Attempting again in 5 seconds...")
                await asyncio.sleep(5)
            else:
                print("Reconnected successfully.")
            continue
        except Exception:
            await ctx.close_wii_client()
            logger.info(
                "Connection to console failed, attempting again in 5 seconds..."
            )
            logger.error(traceback.format_exc())
            await asyncio.sleep(5)
            continue

def main(connect: Optional[str] = None, password: Optional[str] = None) -> None:
    """
    Run the main async loop for the SS client.

    :param connect: Address of the Archipelago server.
    :param password: Password for server authentication.
    """
    Utils.init_logging("Skyward Sword Client")

    async def _main(connect: Optional[str], password: Optional[str]) -> None:
        ctx = SSContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await asyncio.sleep(1)

        ctx.sync_task = asyncio.create_task(
            do_sync_task(ctx), name="GameSync"
        )

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

        if ctx.sync_task:
            await asyncio.sleep(3)
            await ctx.sync_task

    import colorama

    colorama.init()
    asyncio.run(_main(connect, password))
    colorama.deinit()


if __name__ == "__main__":
    parser = get_base_parser()
    args = parser.parse_args()
    main(args.connect, args.password)


