import socket
import threading
import re
import time
from typing import Optional


class RobotSensorInterfaceBridge:
    """
    RobotSensorInterfaceBridge

    - Binds a UDP socket to (local_ip, local_port).
    - Receives <Rob ...> XML packets from the robot.
    - Parses RIst, AIPos, IPOC fields into data_sub.
    - Echoes IPOC and correction data from data_pub in <Sen ...> replies.
    - On stop request, sends a final reply with STOP_RSI=1 on the next incoming packet.
    """

    def __init__(self, local_ip: str = "192.168.1.4", local_port: int = 59152):
        self.local_ip = local_ip
        self.local_port = local_port
        self.buffer_size: int = 65535

        # From robot (subscribe)
        self.data_sub = {
            "X": 0.0, "Y": 0.0, "Z": 0.0,
            "A": 0.0, "B": 0.0, "C": 0.0,
            "A1": 0.0, "A2": 0.0, "A3": 0.0,
            "A4": 0.0, "A5": 0.0, "A6": 0.0,
            "ipoc": 0,
        }

        # To robot (publish)
        self.data_pub = {
            "X": 0.0, "Y": 0.0, "Z": 0.0,
            "A": 0.0, "B": 0.0, "C": 0.0,
            "stop_rsi": 0,
            "dio": 125,
            "ipoc": 0,
        }

        # Independent mutexes for sub/pub
        self._sub_lock = threading.Lock()
        self._pub_lock = threading.Lock()

        # Precompiled regex patterns for parsing
        self.RE_RIST = re.compile(
            r'<RIst\s+X="([^"]+)"\s+Y="([^"]+)"\s+Z="([^"]+)"\s+'
            r'A="([^"]+)"\s+B="([^"]+)"\s+C="([^"]+)"'
        )
        self.RE_AIPOS = re.compile(
            r'<AIPos\s+A1="([^"]+)"\s+A2="([^"]+)"\s+A3="([^"]+)"\s+'
            r'A4="([^"]+)"\s+A5="([^"]+)"\s+A6="([^"]+)"'
        )
        self.RE_IPOC = re.compile(r"<IPOC>\s*(\d+)\s*</IPOC>")

        self.sock: Optional[socket.socket] = None
        self.local_ipoc: int = 0
        self.echo_counter: int = 0

        self._running = False
        self._stop_requested = False
        self._thread: Optional[threading.Thread] = None
        self.debug: bool = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the UDP server and background thread."""
        if self._running:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))
        # Optional timeout to allow graceful exit if no more packets arrive
        self.sock.settimeout(0.5)

        self._running = True
        self._stop_requested = False

        self._thread = threading.Thread(
            target=self._run_loop,
            name="RobotSensorInterfaceBridge-UDP",
            daemon=True,
        )
        self._thread.start()
        print(f"[RSI Bridge] Listening UDP on {self.local_ip}:{self.local_port} ...")

    def stop(self) -> None:
        """
        Request a graceful stop.

        - The next incoming packet will be answered with STOP_RSI=1.
        - After sending that final reply, the loop terminates and the socket is closed.
        """
        if not self._running:
            return

        # Signal the loop to send STOP_RSI on the next packet
        self._stop_requested = True

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

        # Ensure socket is closed
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

        self._running = False
        print("[RSI Bridge] Stopped.")

    # ------------------------------------------------------------------
    # Thread-safe getters / setter
    # ------------------------------------------------------------------
    def get_data_sub(self) -> dict:
        """Return a thread-safe snapshot (shallow copy) of data_sub."""
        with self._sub_lock:
            return dict(self.data_sub)

    def get_data_pub(self) -> dict:
        """Return a thread-safe snapshot (shallow copy) of data_pub."""
        with self._pub_lock:
            return dict(self.data_pub)

    def set_data_pub(self, **kwargs) -> None:
        """
        Thread-safe update of data_pub.

        Example:
            bridge.set_data_pub(X=0.1, Z=-0.2, stop_rsi=0)
        """
        with self._pub_lock:
            for key, value in kwargs.items():
                if key not in self.data_pub:
                    raise KeyError(f"Invalid data_pub key: {key}")
                self.data_pub[key] = value

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------
    def _run_loop(self) -> None:
        """Main UDP receive/reply loop."""
        assert self.sock is not None

        while True:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
            except socket.timeout:
                # If stop was requested and no more packets arrive, exit
                if self._stop_requested:
                    break
                else:
                    continue
            except OSError:
                # Socket closed or other I/O error
                break

            if not data:
                if self.debug:
                    print("[RSI Bridge] Received empty UDP packet; skipping.")
                continue

            try:
                text = data.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                print(f"[RSI Bridge] Failed to decode incoming bytes from {addr}.")
                continue

            if self.debug:
                print(f"[RSI Bridge] From {addr[0]}:{addr[1]} -> {text}")

            # 1) Parse & update data_sub
            incoming_ipoc = self._unpack_incoming(text)

            # 2) If stop is requested, send one final reply with STOP_RSI=1 and exit
            if self._stop_requested:
                with self._pub_lock:
                    self.data_pub["ipoc"] = incoming_ipoc
                    self.data_pub["stop_rsi"] = 1
                reply_xml = self._pack_outcoming()
                try:
                    self.sock.sendto(reply_xml.encode("utf-8"), addr)
                    if self.debug:
                        print(
                            f"[RSI Bridge] Sent final STOP_RSI=1 to "
                            f"{addr[0]}:{addr[1]} IPOC={incoming_ipoc}"
                        )
                except OSError as e:
                    print(f"[RSI Bridge] Failed to send final STOP_RSI packet: {e}")
                break

            # 3) Normal behavior: echo IPOC and send reply
            with self._pub_lock:
                self.data_pub["ipoc"] = incoming_ipoc

            reply_xml = self._pack_outcoming()

            try:
                self.sock.sendto(reply_xml.encode("utf-8"), addr)
                if self.debug:
                    print(f"[RSI Bridge] Sent reply to {addr[0]}:{addr[1]} IPOC={incoming_ipoc}")
            except OSError as e:
                print(f"[RSI Bridge] Failed to send reply to {addr}: {e}")

        # Cleanup when loop ends
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

        self._running = False

    # ------------------------------------------------------------------
    # Incoming parsing
    # ------------------------------------------------------------------
    def _unpack_incoming(self, xml_text: str) -> int:
        """
        Parse incoming XML, update data_sub, and return the IPOC value (int).
        If IPOC is missing, a local IPOC counter is used.
        """
        m_rist = self.RE_RIST.search(xml_text)
        m_aipos = self.RE_AIPOS.search(xml_text)
        m_ipoc = self.RE_IPOC.search(xml_text)

        if m_ipoc is None:
            self.local_ipoc += 1
            ipoc_val = self.local_ipoc
        else:
            ipoc_val = int(m_ipoc.group(1))

        with self._sub_lock:
            if m_rist:
                self.data_sub["X"] = float(m_rist.group(1))
                self.data_sub["Y"] = float(m_rist.group(2))
                self.data_sub["Z"] = float(m_rist.group(3))
                self.data_sub["A"] = float(m_rist.group(4))
                self.data_sub["B"] = float(m_rist.group(5))
                self.data_sub["C"] = float(m_rist.group(6))

            if m_aipos:
                self.data_sub["A1"] = float(m_aipos.group(1))
                self.data_sub["A2"] = float(m_aipos.group(2))
                self.data_sub["A3"] = float(m_aipos.group(3))
                self.data_sub["A4"] = float(m_aipos.group(4))
                self.data_sub["A5"] = float(m_aipos.group(5))
                self.data_sub["A6"] = float(m_aipos.group(6))

            self.data_sub["ipoc"] = ipoc_val
            self.echo_counter += 1

        if self.debug:
            print(f"[RSI Bridge] Echoing incoming IPOC: {ipoc_val}")

        return ipoc_val

    # ------------------------------------------------------------------
    # Reply construction
    # ------------------------------------------------------------------
    def _pack_outcoming(self) -> str:
        """Construct the <Sen Type="ImFree"> reply using the current data_pub."""
        with self._pub_lock:
            x = f'{self.data_pub["X"]:.4f}'
            y = f'{self.data_pub["Y"]:.4f}'
            z = f'{self.data_pub["Z"]:.4f}'
            a = f'{self.data_pub["A"]:.4f}'
            b = f'{self.data_pub["B"]:.4f}'
            c = f'{self.data_pub["C"]:.4f}'
            stop_rsi = int(self.data_pub["stop_rsi"])
            dio = int(self.data_pub["dio"])
            ipoc_str = str(int(self.data_pub["ipoc"]))

        reply = f"""<Sen Type="ImFree">
                    <EStr>Message from RSI TestServer</EStr>
                    <Tech T21="1.09" T22="2.08" T23="3.07" T24="4.06" T25="5.05" T26="6.04" T27="7.03" T28="8.02" T29="9.01" T30="10.00"/>
                    <RKorr X="{x}" Y="{y}" Z="{z}" A="{a}" B="{b}" C="{c}"/>
                    <STOP_RSI>{stop_rsi}</STOP_RSI>
                    <DiO>{dio}</DiO>
                    <IPOC>{ipoc_str}</IPOC>
                </Sen>"""
        return reply
