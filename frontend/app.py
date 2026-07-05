import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
from src.api_client import ForexAPIClient

# Load environment variables
load_dotenv()

# Load custom CSS theme
css_path = os.path.join(os.path.dirname(__file__), "src", "theme.css")
css_content = ""
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css_content = f.read()

# Initialize API client
api_client = ForexAPIClient()

SYMBOLS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]


def build_card_html(symbol: str, data: dict | None) -> str:
    """Helper to generate premium HTML card representations of forex price ticks."""
    if not data:
        return f"""
        <div class="forex-card" style="opacity: 0.6;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; font-size:1.1rem; color:#f9fafb;">{symbol}</span>
                <span style="font-size:0.8rem; color:#ef4444; font-weight:bold;">Offline</span>
            </div>
            <p style="font-size:0.85rem; color:#9ca3af; margin-top:1rem;">Awaiting data ingestion ticks...</p>
        </div>
        """
        
    price = data.get("price", 0.0)
    bid = data.get("bid") or price
    ask = data.get("ask") or price
    high = data.get("high", price)
    low = data.get("low", price)
    
    # Pip calculation for spreads
    pip_factor = 0.01 if "JPY" in symbol else 0.0001
    spread_pips = round(abs(ask - bid) / pip_factor, 1)
    
    # Calculate a simulated change percentage based on base prices
    base_prices = {"EUR/USD": 1.0850, "GBP/USD": 1.2720, "USD/JPY": 155.40, "AUD/USD": 0.6650}
    base = base_prices.get(symbol, price)
    change_pct = ((price - base) / base) * 100.0 if base else 0.0
    
    change_class = "price-up" if change_pct >= 0 else "price-down"
    change_icon = "▲" if change_pct >= 0 else "▼"
    change_prefix = "+" if change_pct > 0 else ""
    
    return f"""
    <div class="forex-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <span style="font-weight:700; font-size:1.1rem; color:#f9fafb;">{symbol}</span>
            <span style="font-size:0.85rem; color:#9ca3af; background-color:#374151; padding:2px 6px; border-radius:4px;">Active</span>
        </div>
        <div style="display:flex; gap:1.5rem; align-items:baseline; margin-bottom:0.5rem;">
            <div>
                <span style="font-size:0.75rem; color:#9ca3af; display:block;">BID</span>
                <span style="font-size:1.5rem; font-weight:800; font-family:monospace; color:#f9fafb;">{bid:.5f}</span>
            </div>
            <div>
                <span style="font-size:0.75rem; color:#9ca3af; display:block;">ASK</span>
                <span style="font-size:1.5rem; font-weight:800; font-family:monospace; color:#f9fafb;">{ask:.5f}</span>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.85rem; border-top:1px solid #374151; padding-top:0.5rem; margin-top:0.5rem;">
            <span class="{change_class}" style="display:flex; align-items:center; gap:4px;">
                <span style="font-size:1rem;">{change_icon}</span> {change_prefix}{change_pct:.2f}%
            </span>
            <span style="color:#9ca3af;">Spread: {spread_pips} pips</span>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6b7280; margin-top:0.25rem;">
            <span>L: {low:.5f}</span>
            <span>H: {high:.5f}</span>
        </div>
    </div>
    """


async def get_dashboard_updates(watchlist_symbols: list[str]) -> tuple:
    """Polled function that fetches current rates and rebuilds UI components."""
    # 1. Fetch live prices for all pairs
    tasks = [api_client.get_live_price(sym) for sym in SYMBOLS]
    prices = await asyncio.gather(*tasks)
    price_map = {sym: price for sym, price in zip(SYMBOLS, prices)}
    
    # 2. Build live currency HTML card components
    cards_html = []
    for symbol in SYMBOLS:
        cards_html.append(build_card_html(symbol, price_map.get(symbol)))
        
    # 3. Build Watchlist HTML
    watchlist_html = ""
    if not watchlist_symbols:
        watchlist_html = "<p style='color:#9ca3af; font-size:0.9rem;'>Your watchlist is empty. Check pairs above to add.</p>"
    else:
        for symbol in watchlist_symbols:
            data = price_map.get(symbol)
            price = data.get("price", 0.0) if data else 0.0
            bid = data.get("bid", price) if data else 0.0
            ask = data.get("ask", price) if data else 0.0
            
            watchlist_html += f"""
            <div class="watchlist-item">
                <span style="font-weight:600; color:#f9fafb;">{symbol}</span>
                <span style="font-family:monospace; color:#3b82f6; font-weight:700;">Bid: {bid:.5f} | Ask: {ask:.5f}</span>
            </div>
            """
            
    # 4. Build Movers HTML (Sorted by absolute change percentage)
    movers = []
    base_prices = {"EUR/USD": 1.0850, "GBP/USD": 1.2720, "USD/JPY": 155.40, "AUD/USD": 0.6650}
    for symbol in SYMBOLS:
        data = price_map.get(symbol)
        if data:
            price = data.get("price", 0.0)
            base = base_prices.get(symbol, price)
            change_pct = ((price - base) / base) * 100.0 if base else 0.0
            movers.append((symbol, change_pct, price))
            
    # Sort descending by absolute percentage change
    movers.sort(key=lambda x: abs(x[1]), reverse=True)
    
    movers_html = ""
    for symbol, change, val in movers:
        color = "#10b981" if change >= 0 else "#ef4444"
        icon = "▲" if change >= 0 else "▼"
        prefix = "+" if change > 0 else ""
        movers_html += f"""
        <div class="watchlist-item">
            <span style="font-weight:600; color:#f9fafb;">{symbol}</span>
            <span style="font-family:monospace; color:{color}; font-weight:700;">{icon} {prefix}{change:.2f}% ({val:.4f})</span>
        </div>
        """
        
    return cards_html[0], cards_html[1], cards_html[2], cards_html[3], watchlist_html, movers_html


# Assemble Gradio Layout
with gr.Blocks(title="AI Forex Trading Assistant", css=css_content) as demo:
    gr.Markdown("# AI Forex Trading Assistant")
    gr.Markdown("An intelligent, secure, decision-support platform for foreign exchange traders.")
    
    with gr.Tab("Dashboard"):
        with gr.Row():
            # Left Side - Live price cards
            with gr.Column(scale=2):
                gr.Markdown("### Live Forex Quote Streams (Near-Real-Time)")
                
                with gr.Row():
                    card_eur_usd = gr.HTML(build_card_html("EUR/USD", None))
                    card_gbp_usd = gr.HTML(build_card_html("GBP/USD", None))
                    
                with gr.Row():
                    card_usd_jpy = gr.HTML(build_card_html("USD/JPY", None))
                    card_aud_usd = gr.HTML(build_card_html("AUD/USD", None))
                    
                # Watchlist selector checkboxes
                watchlist_select = gr.CheckboxGroup(
                    choices=SYMBOLS,
                    value=["EUR/USD"],
                    label="Configure Watchlist Pairs",
                    info="Check pairs to pin them to the watchlist overview below."
                )
                
            # Right Side - Portfolio, Movers & Calendar
            with gr.Column(scale=1):
                gr.Markdown("### Simulated Portfolio")
                # Portfolio stats box
                gr.HTML("""
                <div class="forex-card" style="margin-bottom: 1.5rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
                        <span style="color:#9ca3af;">Simulated Balance</span>
                        <span style="font-weight:700; color:#f9fafb;">$10,000.00</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
                        <span style="color:#9ca3af;">Equity</span>
                        <span style="font-weight:700; color:#f9fafb;">$10,000.00</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
                        <span style="color:#9ca3af;">Margin Free</span>
                        <span style="font-weight:700; color:#10b981;">100%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#9ca3af;">Open Positions</span>
                        <span style="font-weight:700; color:#9ca3af;">0 active</span>
                    </div>
                </div>
                """)
                
                gr.Markdown("### Watchlist Overview")
                watchlist_box = gr.HTML("<p style='color:#9ca3af;'>Loading watchlist details...</p>")
                
                gr.Markdown("### Daily Market Movers")
                movers_box = gr.HTML("<p style='color:#9ca3af;'>Loading movers rankings...</p>")

        # AI Insights card
        gr.Markdown("### Daily AI Forex Intelligence (Grounding & News Sentiment)")
        gr.HTML("""
        <div class="forex-card">
            <h4 style="margin:0 0 0.5rem 0; color:#3b82f6;">Market Coordinator Agent Notice</h4>
            <p style="color:#9ca3af; font-size:0.9rem; line-height:1.4;">
                Macro economic sentiment is currently neutral. The economic calendar agent reports high-impact inflation metrics scheduled for release tomorrow. 
                Specialist technical analysis agents note that EUR/USD maintains a bullish consolidation pattern.
            </p>
            <span style="font-size:0.75rem; color:#6b7280; display:block; margin-top:0.5rem;">Generated by Coordinator Agent • Grounded • Informational Only</span>
        </div>
        """)

    with gr.Tab("AI Chat"):
        gr.Markdown("### Interactive AI Trading Partner")
        chatbot = gr.Chatbot(label="Forex Assistant Chat")
        msg = gr.Textbox(placeholder="Ask about market conditions, indicator explanations, etc...")
        clear = gr.Button("Clear")

        def user(user_message, history):
            return "", history + [[user_message, None]]

        def bot(history):
            user_message = history[-1][0]
            bot_message = f"Thank you for asking about '{user_message}'. The AI Forex Assistant is currently initializing. Real-time agent logic will be connected in Milestone 12."
            history[-1][1] = bot_message
            return history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    with gr.Tab("Technical Analysis"):
        gr.Markdown("### Tech Analysis & Indicator Explanation")
        gr.Markdown("Calculators and charts for RSI, MACD, and Bollinger Bands will be added in Milestone 6.")

    with gr.Tab("Trading Journal"):
        gr.Markdown("### Paper Trading Log & Journal Reviews")
        gr.Markdown("Simulated trade logs, performance metrics, and emotional reflections will be added in Milestone 14.")

    # Timer component for real-time polling updates
    timer = gr.Timer(2.0)
    timer.tick(
        get_dashboard_updates,
        inputs=[watchlist_select],
        outputs=[
            card_eur_usd,
            card_gbp_usd,
            card_usd_jpy,
            card_aud_usd,
            watchlist_box,
            movers_box,
        ]
    )

if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 7860))
    host = os.getenv("FRONTEND_HOST", "0.0.0.0")
    demo.launch(server_name=host, server_port=port)
