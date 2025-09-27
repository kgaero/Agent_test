"""Tools for the time agent."""

import datetime

def get_current_time() -> str:
  """Gets the current date and time.

  Returns:
    The current date and time as a string.
  """
  return datetime.datetime.now().isoformat()