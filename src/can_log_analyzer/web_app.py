import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import can
import cantools
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

APP_TITLE = "CAN Log Analyzer"
CAN_DB_EXTENSIONS = [".dbc"]
CAN_LOG_EXTENSIONS = [".asc", ".blf"]
PLOT_TYPES = ["Scatter", "Line", "Heatmap"]
PLOT_MODES = ["Separate Plots", "Single Plot"]
DEFAULT_SHOW_GRID = True

st.set_page_config(page_title=APP_TITLE, layout="wide")


class WebApp:
    """
    Streamlit CAN Log Analyzer Web Application.

    Provides a Streamlit-based web interface for uploading, parsing, and visualizing CAN log files and databases.
    Supports DBC and ARXML database formats, ASC and BLF log formats, and interactive signal plotting using Plotly.

    Features:
        - Upload and parse CAN log and database files.
        - Select channels, messages, and signals for plotting.
        - Visualize signals as scatter, line, or heatmap plots.
    """

    # ----------- File Upload -----------

    @staticmethod
    def upload_files() -> Tuple[Optional[Any], Optional[Any]]:
        """
        Display file upload widgets for CAN log and database files in the sidebar.

        Returns:
            Tuple[Optional[Any], Optional[Any]]: The uploaded CAN log file and database file objects,
            or None if not provided.
        """
        with st.sidebar:
            st.header("Upload CAN Log and Database Files")
            log_file = st.file_uploader(
                f"Browse CAN log file ({', '.join(CAN_LOG_EXTENSIONS)})",
                type=[e[1:] for e in CAN_LOG_EXTENSIONS],
                key="can_log_upload"
            )
            db_file = st.file_uploader(
                f"Load CAN database ({', '.join(CAN_DB_EXTENSIONS)})",
                type=[e[1:] for e in CAN_DB_EXTENSIONS],
                key="can_db_upload"
            )
        return log_file, db_file

    # ----------- CAN Database Loader -----------

    @staticmethod
    @st.cache_resource(show_spinner="Loading CAN database...")
    def load_database(file: Any) -> Optional[cantools.database.Database]:
        """
        Load a CAN database file (.dbc) using cantools.

        Args:
            file (Any): Uploaded file object from Streamlit.

        Returns:
            Optional[cantools.database.Database]: Parsed CAN database object, or None on failure.
        """
        if not file:
            return None
        ext = os.path.splitext(file.name)[1].lower()
        if ext != ".dbc":
            st.error(f"Unsupported database format: {ext}. Only .dbc files are supported.")
            return None
        try:
            file.seek(0)
            content = file.read().decode()
            return cantools.database.load_string(content, "dbc")
        except UnicodeDecodeError:
            st.error("Failed to decode database file. Please upload a valid DBC file.")
        except Exception as e:
            st.error(f"Failed to load database: {e}")
        return None

    # ----------- CAN Log Loader -----------

    @staticmethod
    @st.cache_data(show_spinner="Parsing CAN log file...")
    def load_log(log_bytes: bytes, ext: str) -> Dict[int, Dict[int, List[dict]]]:
        """
        Parse a CAN log file (.asc or .blf) and return structured data.

        Args:
            log_bytes (bytes): Raw bytes of the uploaded CAN log file.
            ext (str): File extension (should be '.asc' or '.blf').

        Returns:
            Dict[int, Dict[int, List[dict]]]: Nested dictionary mapping channel and message ID
            to a list of message entries with timestamp and data.
        """
        if not log_bytes or ext not in CAN_LOG_EXTENSIONS:
            st.warning("Unsupported log format. Showing dummy data.")
            return {
                1: {0x100: [{"timestamp": 0.1, "data": [1,2,3,4,5,6,7,8]}, {"timestamp": 0.2, "data": [1,2,3,4,5,6,7,8]}],
                   0x101: [{"timestamp": 0.3, "data": [1,2,3,4,5,6,7,8]}]},
                2: {0x102: [{"timestamp": 0.4, "data": [1,2,3,4,5,6,7,8]}]}
            }
        parsed: Dict[int, Dict[int, List[dict]]] = {}
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(log_bytes)
            tmp_path = tmp.name
        try:
            for msg in can.LogReader(tmp_path):
                if not isinstance(msg, can.Message):
                    continue
                channel = getattr(msg, "channel", 0)
                msg_id = msg.arbitration_id
                entry = {"timestamp": msg.timestamp, "data": list(msg.data)}
                parsed.setdefault(channel, {}).setdefault(msg_id, []).append(entry)
        except Exception as e:
            st.error(f"Failed to parse {ext} file: {e}")
        finally:
            os.remove(tmp_path)
        return parsed

    # ----------- Signal Plotting -----------

    @staticmethod
    def plot_signals(
        entries: List[dict],
        message: cantools.database.can.message.Message,
        signals: List[str],
        plot_type: str,
        plot_mode: str,
        show_grid: bool,
        xaxis_grid_dtick: Optional[float] = None,
    ) -> None:
        """
        Plot selected CAN signals using Plotly.

        Args:
            entries (List[dict]): List of CAN message entries (timestamp and data).
            message (cantools.database.can.message.Message): CAN message definition.
            signals (List[str]): List of signal names to plot.
            plot_type (str): Type of plot ('Scatter', 'Line', or 'Heatmap').
            plot_mode (str): Plot mode ('Separate Plots' or 'Single Plot').
            show_grid (bool): Whether to show grid lines on the plot.
            xaxis_grid_dtick (Optional[float]): X-axis grid interval (None for auto).
        """
        if not signals:
            st.warning("Please select at least one signal.")
            return

        times = {sig: [] for sig in signals}
        values = {sig: [] for sig in signals}
        for entry in entries:
            try:
                decoded = message.decode(bytes(entry["data"]))
            except Exception:
                decoded = {}
            for sig in signals:
                val = decoded.get(sig)
                if val is not None:
                    times[sig].append(entry["timestamp"])
                    values[sig].append(val)

        all_times = [t for ts in times.values() for t in ts]
        min_time = min(all_times) if all_times else 0.0
        for sig in signals:
            times[sig] = [t - min_time for t in times[sig]]

        if plot_type == "Heatmap":
            if len(signals) < 2:
                st.warning("Heatmap requires at least two signals.")
                return
            sig_x, sig_y = signals[:2]
            data = sorted(zip(times[sig_x], values[sig_x], values[sig_y]))
            if not data:
                st.warning(f"No data for signals '{sig_x}' and '{sig_y}'.")
                return
            _, v_x, v_y = zip(*data)
            fig = go.Figure(data=go.Histogram2d(
                x=v_x,
                y=v_y,
                colorscale='Viridis',
                colorbar=dict(title="Count"),
            ))
            fig.update_layout(
                title=f"Heatmap of {sig_x} vs {sig_y}",
                xaxis_title=sig_x,
                yaxis_title=sig_y,
                xaxis=dict(showgrid=show_grid, dtick=xaxis_grid_dtick or None),
                yaxis=dict(showgrid=show_grid)
            )
            st.plotly_chart(fig, use_container_width=True)
            return

        if plot_mode == "Single Plot":
            fig = go.Figure()
            for sig in signals:
                data = sorted(zip(times[sig], values[sig]))
                if not data:
                    st.warning(f"No data for signal '{sig}'.")
                    continue
                t, v = zip(*data)
                fig.add_trace(go.Scatter(
                    x=t, y=v, mode='lines+markers' if plot_type == "Line" else 'markers', name=sig
                ))
            fig.update_layout(
                title="Signals over timestamp",
                xaxis_title="timestamp (s)",
                yaxis_title="Value",
                xaxis=dict(showgrid=show_grid, dtick=xaxis_grid_dtick or None),
                yaxis=dict(showgrid=show_grid)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            for sig in signals:
                data = sorted(zip(times[sig], values[sig]))
                if not data:
                    st.warning(f"No data for signal '{sig}'.")
                    continue
                t, v = zip(*data)
                fig = (
                    px.line(x=t, y=v, labels={'x': 'timestamp (s)', 'y': sig}, title=f"{sig} over timestamp")
                    if plot_type == "Line"
                    else px.scatter(x=t, y=v, labels={'x': 'timestamp (s)', 'y': sig}, title=f"{sig} over timestamp")
                )
                fig.update_xaxes(showgrid=show_grid, dtick=xaxis_grid_dtick or None)
                fig.update_yaxes(showgrid=show_grid)
                st.plotly_chart(fig, use_container_width=True)

    # ----------- Main App -----------

    @classmethod
    def run(cls) -> None:
        """
        Main entry point for the Streamlit web app.

        Handles the UI workflow: file upload, database and log parsing,
        selection of channels/messages/signals, and plotting.
        """
        log_file, db_file = cls.upload_files()
        if not log_file or not db_file:
            st.info("Please upload both a CAN log file and a database file to begin.")
            return

        with st.spinner("Loading database..."):
            db = cls.load_database(db_file)
        if db is None:
            st.error("Failed to load CAN database.")
            return

        log_bytes = log_file.getvalue()
        ext = os.path.splitext(log_file.name)[1].lower()
        with st.spinner("Parsing CAN log..."):
            can_data = cls.load_log(log_bytes, ext)
        if not can_data:
            st.warning("No CAN data loaded.")
            return

        st.markdown("#### Select Data to Plot")
        col_chan, col_msg, col_sig = st.columns([1, 2, 2])
        with col_chan:
            channels = sorted(can_data.keys())
            if not channels:
                st.warning("No channels found in CAN log.")
                return
            channel_display = [f"CAN{c+1}" for c in channels]
            channel_map = dict(zip(channel_display, channels))
            channel_label = st.selectbox("Select CAN channel", channel_display)
            channel = channel_map[channel_label]
        with col_msg:
            msg_id_to_name = {msg.frame_id: msg.name for msg in db.messages}
            available_ids = set(can_data[channel].keys())
            msg_options = [
                f"{hex(mid)} ({msg_id_to_name.get(mid, 'Unknown')})"
                for mid in available_ids
            ]
            if not msg_options:
                st.warning("No messages found for selected channel.")
                return
            msg_selections = st.multiselect("Select Message ID(s)/Name(s)", msg_options)
            selected_ids = [int(sel.split()[0], 16) for sel in msg_selections]
            selected_msgs = [db.get_message_by_frame_id(mid) for mid in selected_ids]
            selected_msgs = [m for m in selected_msgs if m is not None]
            if not selected_msgs:
                st.warning("No valid messages selected.")
                return

        msg_to_signals = {}
        with col_sig:
            for msg in selected_msgs:
                signal_names = [sig.name for sig in msg.signals]
                default_label = f"Select Signal(s) for {msg.name} ({hex(msg.frame_id)})"
                selected_signals = st.multiselect(default_label, signal_names, key=f"sig_{msg.frame_id}")
                if selected_signals:
                    msg_to_signals[msg] = selected_signals

            if not msg_to_signals:
                st.warning("Please select at least one signal for at least one message.")
                return
        st.markdown("---")
        col_type, col_mode, col_grid = st.columns([1, 1, 1])
        with col_type:
            plot_type = st.selectbox("Plot Type", PLOT_TYPES)
        with col_mode:
            plot_mode = st.radio("Plot Mode", PLOT_MODES)
        with col_grid:
            show_grid = st.checkbox("Show Grid", value=DEFAULT_SHOW_GRID)
            xaxis_grid_dtick = st.number_input(
                "X-axis grid interval (leave 0 for auto)", min_value=0.0, value=0.0, step=0.1
            )
        xaxis_grid_dtick = xaxis_grid_dtick if xaxis_grid_dtick > 0 else None

        st.markdown("---")
        st.subheader("Signal Plots")
        for msg, signals in msg_to_signals.items():
            entries = can_data.get(channel, {}).get(msg.frame_id, [])
            if not entries:
                st.warning(f"No data for message {msg.name} ({hex(msg.frame_id)}).")
                continue
            st.markdown(f"**{msg.name} ({hex(msg.frame_id)})**")
            cls.plot_signals(
                entries, msg, signals, plot_type, plot_mode, show_grid, xaxis_grid_dtick
            )


if __name__ == "__main__":
    WebApp.run()
