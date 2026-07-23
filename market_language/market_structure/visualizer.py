"""
APEX Quant OS - Dual-Layer Visual Auditor (v3.0)
Renders External Structure, Internal Structure, Inducement (IDM), and Dealing Ranges.
"""

import matplotlib.pyplot as plt
from typing import List
from market_language.market_structure.compiler import MarketStructureState
from market_language.market_structure.models import Candle, SwingOrientation


class StructureVisualizer:

    @staticmethod
    def plot_structure(
        candles: List[Candle],
        state: MarketStructureState,
        output_filename: str = "btc_structure_audit.png"
    ) -> str:
        fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#0e1117')

        ts_map = {c.timestamp: idx for idx, c in enumerate(candles)}

        # 1. Candlesticks
        for idx, c in enumerate(candles):
            color = '#00c853' if c.close >= c.open else '#ff3d00'
            ax.plot([idx, idx], [c.low, c.high], color=color, linewidth=0.8, alpha=0.7)
            body_bottom = min(c.open, c.close)
            body_top = max(c.open, c.close)
            body_height = max(body_top - body_bottom, (c.high - c.low) * 0.01)
            rect = plt.Rectangle((idx - 0.35, body_bottom), 0.7, body_height, color=color, alpha=0.9)
            ax.add_patch(rect)

        # 2. Render Internal Swings (Smaller Markers)
        for s in state.internal_swings:
            if s.price_point.timestamp in ts_map:
                s_idx = ts_map[s.price_point.timestamp]
                if s.is_idm:
                    ax.plot(s_idx, s.price_point.price, marker='o', markersize=5, color='#ffea00')
                    ax.text(s_idx, s.price_point.price, " IDM", color='#ffea00', fontsize=7, fontweight='bold')

        # 3. Render External Swings (Prominent Markers + Labels)
        for s in state.external_swings:
            if s.price_point.timestamp in ts_map:
                s_idx = ts_map[s.price_point.timestamp]
                if s.orientation == SwingOrientation.HIGH:
                    ax.plot(s_idx, s.price_point.price, marker='v', markersize=9, color='#00e5ff')
                    ax.text(s_idx, s.price_point.price * 1.002, f"EXT {s.relationship.value}", 
                            color='#00e5ff', fontsize=8, ha='center', fontweight='bold')
                else:
                    ax.plot(s_idx, s.price_point.price, marker='^', markersize=9, color='#ff4081')
                    ax.text(s_idx, s.price_point.price * 0.998, f"EXT {s.relationship.value}", 
                            color='#ff4081', fontsize=8, ha='center', va='top', fontweight='bold')

        # 4. Dealing Range
        if state.dealing_range:
            dr = state.dealing_range
            ax.axhline(y=dr.high_price, color='#ffd600', linestyle='-', linewidth=1.2, alpha=0.8)
            ax.axhline(y=dr.low_price, color='#ffd600', linestyle='-', linewidth=1.2, alpha=0.8)
            ax.axhline(y=dr.equilibrium_price, color='#b0bec5', linestyle=':', linewidth=1.0, alpha=0.7)

        title_str = (
            f"APEX QUANT OS (v3.0 DUAL-LAYER) — MARKET STRUCTURE AUDIT\n"
            f"Symbol: {state.metadata.symbol} [{state.metadata.timeframe}] | "
            f"Trend: {state.trend.direction.value} | "
            f"Ext Swings: {len(state.external_swings)} | Int Swings: {len(state.internal_swings)}"
        )
        ax.set_title(title_str, color='white', fontsize=10, pad=12, loc='left')
        ax.tick_params(colors='gray', labelsize=8)
        ax.grid(True, color='#1e222d', linestyle='--', linewidth=0.5, alpha=0.5)

        y_vals = [c.high for c in candles] + [c.low for c in candles]
        if y_vals:
            ax.set_ylim(min(y_vals) * 0.995, max(y_vals) * 1.005)
        ax.set_xlim(-1, len(candles) + 1)

        plt.tight_layout()
        plt.savefig(output_filename, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        return output_filename
