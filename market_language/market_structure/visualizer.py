"""
APEX Quant OS - Market Structure Visual Backtester & Auditor
Renders OHLCV candles with Swings, BOS/CHOCH lines, Anchors, and Dealing Ranges.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone
from typing import List, Optional

from market_language.market_structure.compiler import MarketStructureState
from market_language.market_structure.models import Candle, SwingOrientation, EventType


class StructureVisualizer:
    """
    Visual verification engine to audit market structure output against human chart reading.
    """

    @staticmethod
    def plot_structure(
        candles: List[Candle],
        state: MarketStructureState,
        output_filename: str = "structure_audit.png"
    ) -> str:
        fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#0e1117')

        # Convert timestamps to datetime strings/indices
        indices = list(range(len(candles)))
        ts_map = {c.timestamp: idx for idx, c in enumerate(candles)}

        # --- 1. DRAW CANDLESTICKS ---
        for idx, c in enumerate(candles):
            color = '#00c853' if c.close >= c.open else '#ff3d00'
            # Wick
            ax.plot([idx, idx], [c.low, c.high], color=color, linewidth=0.8, alpha=0.7)
            # Body
            body_bottom = min(c.open, c.close)
            body_top = max(c.open, c.close)
            body_height = max(body_top - body_bottom, (c.high - c.low) * 0.01) # Min height for dojis
            rect = plt.Rectangle((idx - 0.35, body_bottom), 0.7, body_height, color=color, alpha=0.9)
            ax.add_patch(rect)

        # --- 2. DRAW SWINGS ---
        for s in state.active_swings:
            if s.price_point.timestamp in ts_map:
                s_idx = ts_map[s.price_point.timestamp]
                if s.orientation == SwingOrientation.HIGH:
                    color = '#00e5ff' if s.relationship.value == "HH" else '#18ffff'
                    ax.plot(s_idx, s.price_point.price, marker='v', markersize=7, color=color)
                    ax.text(s_idx, s.price_point.price * 1.002, f"{s.relationship.value}", 
                            color='#18ffff', fontsize=7, ha='center', fontweight='bold')
                else:
                    color = '#ff4081' if s.relationship.value == "LL" else '#ff80ab'
                    ax.plot(s_idx, s.price_point.price, marker='^', markersize=7, color=color)
                    ax.text(s_idx, s.price_point.price * 0.998, f"{s.relationship.value}", 
                            color='#ff80ab', fontsize=7, ha='center', va='top', fontweight='bold')

        # --- 3. DRAW STRUCTURAL EVENTS (BOS / CHOCH) ---
        for evt in state.recent_events:
            if evt.trigger_timestamp in ts_map:
                e_idx = ts_map[evt.trigger_timestamp]
                line_color = '#00e676' if 'BULLISH' in evt.event_type.value else '#ff1744'
                label = evt.event_type.value.split('_')[0] # BOS or CHOCH
                ax.axhline(y=evt.trigger_price, color=line_color, linestyle='--', linewidth=0.8, alpha=0.6)
                ax.text(e_idx, evt.trigger_price, f" {label}", color=line_color, fontsize=8, fontweight='bold', va='bottom')

        # --- 4. DRAW DEALING RANGE & EQUILIBRIUM ---
        if state.dealing_range:
            dr = state.dealing_range
            ax.axhline(y=dr.high_price, color='#ffd600', linestyle='-', linewidth=1.2, alpha=0.8, label='Range High')
            ax.axhline(y=dr.low_price, color='#ffd600', linestyle='-', linewidth=1.2, alpha=0.8, label='Range Low')
            ax.axhline(y=dr.equilibrium_price, color='#b0bec5', linestyle=':', linewidth=1.0, alpha=0.7, label='50% Equilibrium')

        # --- 5. CHART METADATA & STYLING ---
        title_str = (
            f"APEX QUANT OS — MARKET STRUCTURE AUDIT\n"
            f"Symbol: {state.metadata.symbol} [{state.metadata.timeframe}] | "
            f"Trend: {state.trend.direction.value} ({state.trend.maturity.value}) | "
            f"Quality: {state.quality.classification} ({state.quality.quality_score})"
        )
        ax.set_title(title_str, color='white', fontsize=10, pad=12, loc='left')
        ax.tick_params(colors='gray', labelsize=8)
        ax.grid(True, color='#1e222d', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Set dark limits
        y_vals = [c.high for c in candles] + [c.low for c in candles]
        if y_vals:
            ax.set_ylim(min(y_vals) * 0.995, max(y_vals) * 1.005)
        ax.set_xlim(-1, len(candles) + 1)

        plt.tight_layout()
        plt.savefig(output_filename, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        return output_filename
