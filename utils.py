from datetime import datetime
def get_time() -> str:
    return f'<Time>{datetime.now().strftime("%Y-%m-%d %H:%M")}</Time>'