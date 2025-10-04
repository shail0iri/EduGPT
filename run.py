import os
import time
import asyncio
import yaml
import gradio as gr
from generating_syllabus import generate_syllabus
from teaching_agent import teaching_agent

# Import MCP tools
try:
    from mcp_tools import mcp_tool_manager
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP tools not available - running without external tools")

# Load Gemini API key from .env file ONLY
try:
    with open(".env", "r") as f:
        env_file = f.readlines()
    envs_dict = {
        key.strip().strip("'"): value.strip().strip("\n").strip("'")
        for key, value in [(i.split("=", 1)) for i in env_file if "=" in i]
    }
    if "GOOGLE_API_KEY" in envs_dict:
        os.environ["GOOGLE_API_KEY"] = envs_dict["GOOGLE_API_KEY"]
        print("✅ Google API key loaded from .env file")
    else:
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("Please set GOOGLE_API_KEY=your_actual_key in .env file")
except FileNotFoundError:
    print("❌ .env file not found")
    print("Please create a .env file with GOOGLE_API_KEY=your_actual_key")

# Initialize MCP servers if available
async def initialize_mcp_servers():
    """Initialize MCP servers on startup"""
    if not MCP_AVAILABLE:
        return "MCP tools not available"
    
    try:
        # Create default config if doesn't exist
        if not os.path.exists("mcp_config.yaml"):
            default_config = {
                'servers': [
                    {
                        'id': 'filesystem',
                        'name': 'File System',
                        'command': 'npx',
                        'args': ['@modelcontextprotocol/server-filesystem', '.'],
                        'description': 'Access local files for educational content'
                    }
                ]
            }
            with open("mcp_config.yaml", "w") as f:
                yaml.dump(default_config, f)
            print("Created default MCP config file")
        
        # Load and initialize servers
        with open("mcp_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        await mcp_tool_manager.initialize_servers(config.get("servers", []))
        
        server_count = len(config.get("servers", []))
        return f"✅ {server_count} MCP server(s) initialized successfully"
        
    except Exception as e:
        return f"❌ Failed to initialize MCP servers: {str(e)}"

# Run MCP initialization
mcp_status = asyncio.run(initialize_mcp_servers())
print(mcp_status)

# MCP Management Functions
def get_mcp_status():
    """Get current MCP server status"""
    if not MCP_AVAILABLE:
        return "MCP tools not installed"
    
    try:
        servers = mcp_tool_manager.mcp_service.get_available_servers()
        if not servers:
            return "No MCP servers running"
        
        status_lines = []
        for server_id in servers:
            server_info = mcp_tool_manager.mcp_service.servers.get(server_id, {})
            status = server_info.get('status', 'unknown')
            config = server_info.get('config', {})
            name = config.get('name', server_id)
            status_lines.append(f"✅ {name} ({server_id}): {status}")
        
        return "\n".join(status_lines)
    except Exception as e:
        return f"Error getting MCP status: {str(e)}"

async def add_mcp_server(server_data):
    """Add a new MCP server"""
    if not MCP_AVAILABLE:
        return "MCP tools not available"
    
    try:
        # Load existing config
        with open("mcp_config.yaml", "r") as f:
            config = yaml.safe_load(f) or {'servers': []}
        
        # Add new server
        new_server = {
            'id': server_data['id'],
            'name': server_data['name'],
            'command': server_data['command'],
            'args': server_data.get('args', []),
            'description': server_data.get('description', ''),
            'env': server_data.get('env', {})
        }
        
        config['servers'].append(new_server)
        
        # Save config
        with open("mcp_config.yaml", "w") as f:
            yaml.dump(config, f)
        
        # Initialize the new server
        await mcp_tool_manager.initialize_servers([new_server])
        
        return f"✅ Server '{server_data['name']}' added successfully"
        
    except Exception as e:
        return f"❌ Failed to add server: {str(e)}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎓 EduGPT - Your AI Instructor with Gemini
    
    *Powered by Google Gemini AI • Enhanced with MCP Tools*
    """)
    
    with gr.Tab("📚 Input Your Learning Topic"):
        gr.Markdown("### What would you like to learn today?")
        
        def perform_task(input_text):
            """Generate syllabus based on user input"""
            if not input_text.strip():
                return "Please enter a topic to learn"
                
            try:
                task = f"Generate a course syllabus to teach the topic: {input_text}"
                syllabus = generate_syllabus(input_text, task)
                
                # Seed the teaching agent with the generated syllabus
                teaching_agent.seed_agent(syllabus, task)
                
                return f"✅ Syllabus generated successfully!\n\n{syllabus}"
                
            except Exception as e:
                return f"❌ Error generating syllabus: {str(e)}"
        
        with gr.Row():
            text_input = gr.Textbox(
                label="Enter your learning topic:",
                placeholder="e.g., Machine Learning, Python Programming, Data Science...",
                lines=2
            )
        
        with gr.Row():
            text_button = gr.Button("🚀 Generate Syllabus", variant="primary")
        
        with gr.Row():
            text_output = gr.Textbox(
                label="Generated Syllabus:",
                lines=10,
                max_lines=20,
                show_copy_button=True
            )
        
        text_button.click(
            perform_task,
            inputs=text_input,
            outputs=text_output
        )
    
    with gr.Tab("👨‍🏫 AI Instructor"):
        gr.Markdown("### Chat with your AI Instructor")
        
        chatbot = gr.Chatbot(
            label="Learning Conversation",
            height=500,
            show_copy_button=True,
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your question or response:",
                placeholder="Ask about the topic, request examples, or continue the lesson...",
                scale=4
            )
            send_btn = gr.Button("📤 Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            new_topic_btn = gr.Button("🔄 New Topic", variant="secondary")
        
        def user(user_message, history):
            """Process user input"""
            if not user_message.strip():
                return "", history
                
            teaching_agent.human_step(user_message)
            return "", history + [[user_message, None]]
        
        async def bot(history):
            """Generate AI instructor response"""
            try:
                # Use async instructor step if MCP tools are available
                if MCP_AVAILABLE and teaching_agent.mcp_tools_enabled:
                    bot_message = await teaching_agent._callinstructor({})
                else:
                    bot_message = teaching_agent.instructor_step()
                
                # Clean the message - remove <END_OF_TURN> and any extra whitespace
                
                clean_message = bot_message.replace('<END_OF_TURN>', '').strip()
                
                # Stream the response
                history[-1][1] = ""
                for character in clean_message:
                    history[-1][1] += character
                    time.sleep(0.01)  # Smooth streaming
                    yield history
                    
            except Exception as e:
                error_msg = f"❌ Error generating response: {str(e)}"
                history[-1][1] = error_msg
                yield history
        
        # Event handlers
        msg_submit = msg.submit(
            user, 
            [msg, chatbot], 
            [msg, chatbot], 
            queue=False
        ).then(
            bot, 
            chatbot, 
            chatbot
        )
        
        send_btn.click(
            user,
            [msg, chatbot],
            [msg, chatbot],
            queue=False
        ).then(
            bot,
            chatbot,
            chatbot
        )
        
        clear_btn.click(
            lambda: None,
            None,
            chatbot,
            queue=False
        )
        
        def new_topic():
            """Reset conversation for new topic"""
            teaching_agent.conversation_history = []
            return None
        
        new_topic_btn.click(
            new_topic,
            None,
            chatbot,
            queue=False
        )
    
    with gr.Tab("⚙️ MCP Tools Management"):
        gr.Markdown("### Manage External Tools Integration")
        
        if not MCP_AVAILABLE:
            gr.Markdown("""
            ## ⚠️ MCP Tools Not Available
            
            To enable MCP tools, install the required dependencies:
            ```bash
            pip install pyyaml aiofiles
            ```
            
            And create the MCP service files.
            """)
        else:
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("#### Server Status")
                    status_display = gr.Textbox(
                        label="Current MCP Servers",
                        lines=6,
                        interactive=False
                    )
                    refresh_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                
                with gr.Column(scale=3):
                    gr.Markdown("#### Add New MCP Server")
                    
                    server_id = gr.Textbox(
                        label="Server ID",
                        placeholder="e.g., brave-search"
                    )
                    server_name = gr.Textbox(
                        label="Server Name", 
                        placeholder="e.g., Web Search"
                    )
                    server_command = gr.Textbox(
                        label="Command",
                        placeholder="e.g., npx, python, node"
                    )
                    server_args = gr.Textbox(
                        label="Arguments (space separated)",
                        placeholder="e.g., @modelcontextprotocol/server-filesystem ."
                    )
                    server_desc = gr.Textbox(
                        label="Description",
                        placeholder="What does this server provide?"
                    )
                    
                    add_server_btn = gr.Button("➕ Add Server", variant="primary")
                    add_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                gr.Markdown("#### Available MCP Servers")
                available_servers = gr.JSON(
                    label="Pre-configured Servers",
                    value=[
                        {
                            "id": "filesystem",
                            "name": "File System Access",
                            "command": "npx",
                            "args": ["@modelcontextprotocol/server-filesystem", "."],
                            "description": "Read and browse local files"
                        },
                        {
                            "id": "brave-search", 
                            "name": "Web Search",
                            "command": "npx",
                            "args": ["@modelcontextprotocol/server-brave-search"],
                            "description": "Search the web for current information",
                            "env": {"BRAVE_API_KEY": "your-key-here"}
                        }
                    ]
                )
            
            # MCP Tool Controls
            with gr.Row():
                enable_tools = gr.Checkbox(
                    label="Enable MCP Tools in Teaching",
                    value=True,
                    info="Allow AI instructor to use external tools"
                )
                tools_status = gr.Textbox(
                    label="Tools Status",
                    value="MCP tools enabled" if teaching_agent.mcp_tools_enabled else "MCP tools disabled",
                    interactive=False
                )
            
            # Event handlers for MCP tab
            def refresh_status():
                return get_mcp_status()
            
            async def add_server(server_id, server_name, server_command, server_args, server_desc):
                if not all([server_id, server_name, server_command]):
                    return "Please fill in all required fields"
                
                server_data = {
                    'id': server_id,
                    'name': server_name,
                    'command': server_command,
                    'args': server_args.split() if server_args else [],
                    'description': server_desc
                }
                
                return await add_mcp_server(server_data)
            
            def toggle_tools(enable):
                if enable:
                    teaching_agent.enable_mcp_tools()
                    return "MCP tools enabled"
                else:
                    teaching_agent.disable_mcp_tools()
                    return "MCP tools disabled"
            
            refresh_btn.click(refresh_status, outputs=status_display)
            add_server_btn.click(
                add_server,
                inputs=[server_id, server_name, server_command, server_args, server_desc],
                outputs=add_status
            )
            enable_tools.change(
                toggle_tools,
                inputs=enable_tools,
                outputs=tools_status
            )
    
    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        ## About EduGPT with Gemini
        
        **Features:**
        - 🤖 Powered by Google Gemini AI (Free tier)
        - 📚 Automated syllabus generation
        - 👨‍🏫 Interactive AI instructor
        - 🔧 MCP tool integration for enhanced capabilities
        - 💬 Real-time chat interface
        
        **How to Use:**
        1. Enter your learning topic in the first tab
        2. Generate a customized syllabus
        3. Chat with your AI instructor in the second tab
        4. Use MCP tools to enhance learning with external resources
        
        **Getting Google Gemini API Key:**
        1. Visit [Google AI Studio](https://aistudio.google.com/)
        2. Sign in with your Google account
        3. Create a new API key
        4. Add it to your `.env` file as `GOOGLE_API_KEY=your_key_here`
        
        **MCP Tools:**
        - File system access for reading examples
        - Web search for current information
        - Database querying for data examples
        """)

# Launch the application
demo.queue(max_size=20).launch(
    debug=True, 
    share=True,
    show_error=True,
    inbrowser=True
)