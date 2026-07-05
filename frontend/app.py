import os
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Basic layout using Blocks
with gr.Blocks(title="AI Forex Trading Assistant") as demo:
    gr.Markdown("# AI Forex Trading Assistant")
    gr.Markdown("An intelligent decision-support platform for forex traders.")

    with gr.Tab("Dashboard"):
        gr.Markdown("### Market Watchlist & AI Insights")
        gr.Markdown("Live currency feeds and daily news analysis will be rendered here.")

    with gr.Tab("AI Chat"):
        gr.Markdown("### Interactive AI Trading Partner")
        chatbot = gr.Chatbot(label="Forex Assistant Chat")
        msg = gr.Textbox(placeholder="Ask about market conditions, indicator explanations, etc...")
        clear = gr.Button("Clear")

        def user(user_message, history):
            return "", history + [[user_message, None]]

        def bot(history):
            user_message = history[-1][0]
            # Simple placeholder response
            bot_message = f"Thank you for asking about '{user_message}'. The AI Forex Assistant is currently initializing. Real-time agent logic will be connected in Milestone 12."
            history[-1][1] = bot_message
            return history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    with gr.Tab("Technical Analysis"):
        gr.Markdown("### Tech Analysis & Indicator Explanation")

    with gr.Tab("Trading Journal"):
        gr.Markdown("### Paper Trading Log & Journal Reviews")

if __name__ == "__main__":
    port = int(os.getenv("FRONTEND_PORT", 7860))
    host = os.getenv("FRONTEND_HOST", "0.0.0.0")
    demo.launch(server_name=host, server_port=port)
