# ui.py - Beautiful Pastel Terminal UI
"""
Provides pastel-colored terminal output with elegant formatting.
Uses ANSI color codes for beautiful, readable terminal displays.
"""

class PastelUI:
    """Pastel color scheme for terminal output"""
    
    # Pastel Colors (light, soft tones)
    PASTEL_PINK = '\033[38;5;217m'        # Light pink
    PASTEL_BLUE = '\033[38;5;153m'        # Light blue
    PASTEL_GREEN = '\033[38;5;158m'       # Light green
    PASTEL_YELLOW = '\033[38;5;229m'      # Light yellow
    PASTEL_PURPLE = '\033[38;5;183m'      # Light purple
    PASTEL_CYAN = '\033[38;5;159m'        # Light cyan
    PASTEL_ORANGE = '\033[38;5;223m'      # Light orange
    PASTEL_LAVENDER = '\033[38;5;189m'    # Lavender
    
    # Bright accent colors for important info
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_MAGENTA = '\033[95m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Box drawing characters
    TOP_LEFT = '╭'
    TOP_RIGHT = '╮'
    BOTTOM_LEFT = '╰'
    BOTTOM_RIGHT = '╯'
    HORIZONTAL = '─'
    VERTICAL = '│'
    T_DOWN = '┬'
    T_UP = '┴'
    T_RIGHT = '├'
    T_LEFT = '┤'
    CROSS = '┼'
    
    # Special symbols
    SPARKLE = '✨'
    ROCKET = '🚀'
    CHECK = '✓'
    CROSS_MARK = '✗'
    ARROW = '→'
    BULLET = '•'
    STAR = '⭐'
    
    @staticmethod
    def visible_len(text):
        """Get visible length of text (ignoring ANSI codes)"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return len(ansi_escape.sub('', text))

    @staticmethod
    def gradient_banner(text, width=80):
        """Create a beautiful gradient banner"""
        colors = [
            '\033[38;5;183m',  # Lavender
            '\033[38;5;189m',  # Light purple
            '\033[38;5;153m',  # Light blue
            '\033[38;5;159m',  # Light cyan
        ]
        
        # Create top border with gradient
        top = ""
        for i in range(width):
            color_idx = (i * len(colors)) // width
            top += f"{colors[color_idx]}━"
        top += PastelUI.RESET
        
        # Center text
        padding = (width - len(text) - 4) // 2
        middle = f"{PastelUI.BRIGHT_CYAN}{PastelUI.BOLD}{'  ' + text + '  '}{PastelUI.RESET}"
        middle_line = f"{colors[0]}┃{' ' * padding}{middle}{' ' * padding}{colors[-1]}┃{PastelUI.RESET}"
        
        # Bottom border
        bottom = ""
        for i in range(width):
            color_idx = (i * len(colors)) // width
            bottom += f"{colors[color_idx]}━"
        bottom += PastelUI.RESET
        
        return f"\n{top}\n{middle_line}\n{bottom}\n"
    
    @staticmethod
    def progress_bar(current, total, width=40, label=""):
        """Create a beautiful progress bar"""
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int((current / total) * 100)
        
        return f"{PastelUI.PASTEL_CYAN}{label}{PastelUI.RESET} [{PastelUI.PASTEL_GREEN}{bar}{PastelUI.RESET}] {PastelUI.BOLD}{percentage}%{PastelUI.RESET}"
    
    @staticmethod
    def box(text, color='', width=70, title=''):
        """Create a beautiful box around text"""
        lines = text.split('\n')
        
        # Word wrap lines if they are too long
        import textwrap
        wrapped_lines = []
        max_content_width = width - 4
        
        for line in lines:
            # Preserve empty lines
            if not line.strip():
                wrapped_lines.append("")
                continue
                
            # Use textwrap to wrap gracefully at word boundaries
            wrapped = textwrap.wrap(line, width=max_content_width, break_long_words=True, break_on_hyphens=True)
            wrapped_lines.extend(wrapped)
        
        lines = wrapped_lines
        
        # Top border
        if title:
            title_text = f' {title} '
            text_len = len(title_text)
            padding = (width - text_len - 2) // 2
            rem = (width - text_len - 2) % 2
            top = f"{color}{PastelUI.TOP_LEFT}{PastelUI.HORIZONTAL * padding}{PastelUI.BOLD}{title_text}{PastelUI.RESET}{color}{PastelUI.HORIZONTAL * (padding + rem)}{PastelUI.TOP_RIGHT}{PastelUI.RESET}"
        else:
            top = f"{color}{PastelUI.TOP_LEFT}{PastelUI.HORIZONTAL * (width - 2)}{PastelUI.TOP_RIGHT}{PastelUI.RESET}"
        
        # Content
        content = []
        for line in lines:
            vis_len = PastelUI.visible_len(line)
            padding = width - vis_len - 4
            if padding < 0: padding = 0
            content.append(f"{color}{PastelUI.VERTICAL}{PastelUI.RESET} {line}{' ' * padding} {color}{PastelUI.VERTICAL}{PastelUI.RESET}")
        
        # Bottom border
        bottom = f"{color}{PastelUI.BOTTOM_LEFT}{PastelUI.HORIZONTAL * (width - 2)}{PastelUI.BOTTOM_RIGHT}{PastelUI.RESET}"
        
        return '\n'.join([top] + content + [bottom])
    
    @staticmethod
    def header(text, color=''):
        """Create a beautiful header"""
        width = 70
        vis_len = len(text)
        padding = (width - vis_len - 2) // 2
        line = PastelUI.HORIZONTAL * width
        
        return f"\n{color}{PastelUI.BOLD}{line}\n{' ' * padding}{text}\n{line}{PastelUI.RESET}\n"
    
    @staticmethod
    def section(title, color=''):
        """Create a section divider"""
        return f"\n{color}{PastelUI.BOLD}▸ {title}{PastelUI.RESET}\n"
    
    @staticmethod
    def info(text, icon='ℹ'):
        """Info message with icon"""
        return f"{PastelUI.PASTEL_BLUE}{icon}  {text}{PastelUI.RESET}"
    
    @staticmethod
    def success(text, icon='✓'):
        """Success message with icon"""
        return f"{PastelUI.BRIGHT_GREEN}{icon}  {text}{PastelUI.RESET}"
    
    @staticmethod
    def warning(text, icon='⚠'):
        """Warning message with icon"""
        return f"{PastelUI.PASTEL_YELLOW}{icon}  {text}{PastelUI.RESET}"
    
    @staticmethod
    def error(text, icon='✗'):
        """Error message with icon"""
        return f"{PastelUI.PASTEL_PINK}{icon}  {text}{PastelUI.RESET}"
    
    @staticmethod
    def workflow_arrow():
        """Pretty arrow for workflow"""
        return f"{PastelUI.PASTEL_PURPLE}→{PastelUI.RESET}"
    
    @staticmethod
    def agent_badge(name, color=''):
        """Create a badge for agent name"""
        if not color:
            color = PastelUI.PASTEL_CYAN
        return f"{color}{PastelUI.BOLD}[{name}]{PastelUI.RESET}"
    
    @staticmethod
    def divider(char='─', width=70, color=''):
        """Create a divider line"""
        if not color:
            color = PastelUI.DIM
        return f"{color}{char * width}{PastelUI.RESET}"
    
    @staticmethod
    def key_value(key, value, key_color='', value_color=''):
        """Format key-value pair"""
        if not key_color:
            key_color = PastelUI.PASTEL_LAVENDER
        if not value_color:
            value_color = PastelUI.PASTEL_CYAN
        return f"{key_color}{key}:{PastelUI.RESET} {value_color}{value}{PastelUI.RESET}"
    
    @staticmethod
    def spinner_frame(frame_num):
        """Get spinner animation frame"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        return f"{PastelUI.PASTEL_CYAN}{frames[frame_num % len(frames)]}{PastelUI.RESET}"

    @staticmethod
    def table(headers, rows, width=80):
        """Create a beautiful table"""
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    vis_len = PastelUI.visible_len(str(cell))
                    if vis_len > col_widths[i]:
                        col_widths[i] = vis_len
        
        # Adjust for total width limit if needed (simplistic approach)
        total_width = sum(col_widths) + (len(headers) * 3) + 4
        if total_width < width:
            # Distribute extra space
            extra = width - total_width
            per_col = extra // len(headers)
            col_widths = [w + per_col for w in col_widths]
        
        # Helper to create row
        def create_row(cells, colors=None, is_header=False):
            line = f"{PastelUI.PASTEL_PURPLE}│{PastelUI.RESET} "
            for i, cell in enumerate(cells):
                w = col_widths[i]
                content = str(cell)
                vis_len = PastelUI.visible_len(content)
                padding = w - vis_len
                
                color = PastelUI.RESET
                if is_header:
                    color = PastelUI.BOLD + PastelUI.PASTEL_CYAN
                elif colors and i < len(colors) and colors[i]:
                    color = colors[i]
                
                line += f"{color}{content}{PastelUI.RESET}{' ' * padding} {PastelUI.PASTEL_PURPLE}│{PastelUI.RESET} "
            return line

        # Top border
        top = f"{PastelUI.PASTEL_PURPLE}╭"
        for i, w in enumerate(col_widths):
            top += "─" * (w + 2)
            if i < len(col_widths) - 1:
                top += "┬"
        top += "╮" + PastelUI.RESET

        # Header
        header_row = create_row(headers, is_header=True)
        
        # Separator
        sep = f"{PastelUI.PASTEL_PURPLE}├"
        for i, w in enumerate(col_widths):
            sep += "─" * (w + 2)
            if i < len(col_widths) - 1:
                sep += "┼"
        sep += "┤" + PastelUI.RESET

        # Rows
        content_rows = []
        for row in rows:
            content_rows.append(create_row(row))
            
        # Bottom border
        bottom = f"{PastelUI.PASTEL_PURPLE}╰"
        for i, w in enumerate(col_widths):
            bottom += "─" * (w + 2)
            if i < len(col_widths) - 1:
                bottom += "┴"
        bottom += "╯" + PastelUI.RESET
        
        return f"\n{top}\n{header_row}\n{sep}\n" + "\n".join(content_rows) + f"\n{bottom}\n"


# Convenience functions
def print_header(text):
    """Print a beautiful header"""
    print(PastelUI.header(text, PastelUI.PASTEL_PURPLE))

def print_section(title):
    """Print a section title"""
    print(PastelUI.section(title, PastelUI.PASTEL_CYAN))

def print_box(text, title='', color=''):
    """Print text in a box"""
    if not color:
        color = PastelUI.PASTEL_BLUE
    print(PastelUI.box(text, color, title=title))

def print_banner(text):
    """Print a beautiful gradient banner"""
    print(PastelUI.gradient_banner(text))

def print_workflow(agents, workflow_type='sequential'):
    """Print workflow visualization"""
    arrow = f" {PastelUI.workflow_arrow()} "
    
    if workflow_type == 'parallel':
        parallel_text = f"{PastelUI.PASTEL_ORANGE}{PastelUI.BOLD}[PARALLEL]{PastelUI.RESET}"
        agents_text = arrow.join([PastelUI.agent_badge(a, PastelUI.PASTEL_GREEN) for a in agents])
        print(f"{parallel_text} {agents_text}")
    else:
        agents_text = arrow.join([PastelUI.agent_badge(a, PastelUI.PASTEL_BLUE) for a in agents])
        print(agents_text)

def print_agent_output(agent_name, artifact, model_info=None):
    """Print agent output beautifully in a box"""
    # Create title
    title = f"[{agent_name}]"
    
    # Create content with model footer if available
    content = artifact.strip()
    
    if model_info:
        # Add a subtle separator and metadata
        content += f"\n{PastelUI.divider('─', 66, PastelUI.DIM)}\n" 
        content += f"{PastelUI.DIM}Model: {model_info['model']} | Provider: {model_info['provider']} | Latency: {model_info['latency']}s{PastelUI.RESET}"
    
    print("\n")
    print_box(content, title=title, color=PastelUI.PASTEL_CYAN)
    print("\n")
