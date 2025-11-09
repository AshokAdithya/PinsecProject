from datetime import datetime,timezone,timedelta

IST = timezone(timedelta(hours=5,minutes=30))

# Getting time in IST - Indian time
def format_timestamp(ms: int) -> str:
    try:
        dt = datetime.fromtimestamp(ms / 1000, tz=IST)
        return dt.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return str(ms)  