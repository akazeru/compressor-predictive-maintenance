"""
KAESER MCS .dat File Parser
============================
Device  : KAESER CSDX165 rotary screw compressor
Software: fluid_6.5.1 (KAESER MCS data recorder)

FILE STRUCTURE SPECIFICATION
-----------------------------
Offset      Size    Type        Description
0           4       uint32 LE   Format version (= 2)
4           8       uint32 LE   File start Unix timestamp (UTC seconds)
8           12      char[12]    Software version string "fluid_6.5.1\0"
40          3744    char[N*32]  Main channel names: 117 slots × 32 bytes (null-padded ASCII)
3784        96      bytes       Padding (zeros)
3880        192     char[6*32]  Secondary channel names: 6 slots × 32 bytes
4072        64      bytes       Padding (zeros)
4136        128     uint8[128]  Unit-type codes, one per channel index 0..127
4264        950400  record[3600] Data section: 3600 records × 264 bytes each

RECORD LAYOUT (264 bytes each)
-------------------------------
Offset      Size    Type        Description
0           4       uint32 LE   Record Unix timestamp (UTC seconds)
4           260     int16 LE    130 channel values, channel index 0..129

ENCODING
--------
- All channel values: signed 16-bit little-endian integer
- Missing / sensor-not-installed sentinel: -32768 (0x8000) → mapped to NaN
- Sampling rate: exactly 1 Hz (3600 records per 1-hour file)
- Timestamps: increment by exactly 1 second; first record = file-hour start

UNIT TYPE CODES (byte at offset 4136 + channel_index)
------------------------------------------------------
0x04  Status bitmask (unsigned, no scale)
0x05  Status word / flag register (unsigned, no scale)
0x64  Pressure            scale 0.01  unit bar    CONFIRMED (System pressure anchor)
0x65  Temperature         scale 0.01  unit °C     CONFIRMED for oil/compressor-path sensors
                          scale 0.1   unit °C     OBSERVED for electronic-board sensors
                          NOTE: scale disambiguation needed per sensor range (see SCALE NOTES)
0x67  Speed               scale 10    unit RPM    ESTIMATED (speed SP 240-255 × 10 = 2400-2550 RPM)
0x66  DC-Bus voltage      scale Unknown            (raw 805-808, physical reference unavailable)
0x6A  Current             scale Unknown            (raw 806-808, physical reference unavailable)
0x6B  Torque              scale Unknown            (raw 513-523, physical reference unavailable)
0x69  Percentage (0..100) scale 0.1   unit %      ESTIMATED (fan speed SP 998-1000 × 0.1 ≈ 100%)
0x73  Rate                scale Unknown            (ADT rise dT/dt)
0x72  Cold-run value      scale Unknown
0x6C  Raw ADC count       scale 1     unit counts  (calibration raw values)
0x7D  Unknown             scale Unknown
0x00  Undefined / padding

SCALE NOTES
-----------
- For channels with raw values consistently above 3000: apply 0.01 (centidegrees).
  e.g. Oil separator temp 6289 × 0.01 = 62.89 °C ✓
- For channels with raw values consistently below 500: apply 0.1 (decidegrees).
  e.g. Second IOM temp 252 × 0.1 = 25.2 °C ✓
- Inlet temperature (ch 9) raw 61-90 may indicate 6-9°C ambient (cold installation site).
- ADT (ch 2) raw constant = 2 indicates sensor fault or sensor not installed on this unit.
- Scale factors for voltage/current/torque require physical reference measurements.

CHANNEL MAPPING SUMMARY (128 named + 2 unnamed tail channels)
--------------------------------------------------------------
See CHANNEL_NAMES list in this file for all 130 positions.
"""

import struct
import numpy as np
import pandas as pd

# ── constants ─────────────────────────────────────────────────────────────────
_HEADER_VERSION_OFFSET  = 0
_FILE_TIMESTAMP_OFFSET  = 4
_MAIN_NAMES_OFFSET      = 40
_MAIN_NAMES_COUNT       = 117
_SEC_NAMES_OFFSET       = 3880
_SEC_NAMES_COUNT        = 6
_NAME_SLOT_SIZE         = 32
_UNIT_CODES_OFFSET      = 4136
_DATA_OFFSET            = 4264
_RECORD_SIZE            = 264        # bytes per record
_RECORD_TIMESTAMP_SIZE  = 4          # bytes (uint32 LE)
_CHANNELS_PER_RECORD    = 130        # int16 values after timestamp
_RECORDS_PER_FILE       = 3600       # 1 Hz × 3600 s = 1 hour
_MISSING_VALUE          = -32768     # 0x8000 sentinel → NaN


def _read_channel_names(data: bytes) -> list[str]:
    """Return list of 130 column names (channel index → name or 'ch_NNN')."""
    names = []

    # Main block: indices 0-116
    for i in range(_MAIN_NAMES_COUNT):
        off = _MAIN_NAMES_OFFSET + i * _NAME_SLOT_SIZE
        raw = data[off: off + _NAME_SLOT_SIZE]
        names.append(raw.split(b'\x00')[0].decode('ascii', errors='replace').strip())

    # Padding block (indices 117-119): three empty slots between main and secondary
    for i in range(3):
        off = _SEC_NAMES_OFFSET + i * _NAME_SLOT_SIZE
        raw = data[off: off + _NAME_SLOT_SIZE]
        n = raw.split(b'\x00')[0].decode('ascii', errors='replace').strip()
        names.append(n if n else f'ch_{117 + i}')

    # Secondary block: indices 120-122
    for i in range(3, _SEC_NAMES_COUNT):
        off = _SEC_NAMES_OFFSET + i * _NAME_SLOT_SIZE
        raw = data[off: off + _NAME_SLOT_SIZE]
        n = raw.split(b'\x00')[0].decode('ascii', errors='replace').strip()
        names.append(n if n else f'ch_{117 + i}')

    # Unnamed tail: indices 123-129
    for i in range(123, _CHANNELS_PER_RECORD):
        names.append(f'ch_{i}')

    return names


def read_dat(filepath: str) -> pd.DataFrame:
    """
    Parse a single KAESER MCS .dat file.

    Parameters
    ----------
    filepath : str
        Path to a .dat file (e.g. mcs_12.dat).

    Returns
    -------
    pd.DataFrame
        Columns: 'timestamp' (datetime64[UTC]) + 130 sensor channels.
        Missing values encoded as NaN.
        Sensor values are raw int16; apply per-channel scale factors
        documented in the module docstring to convert to engineering units.
    """
    with open(filepath, 'rb') as fh:
        data = fh.read()

    col_names = _read_channel_names(data)

    timestamps = []
    rows = []

    for rec in range(_RECORDS_PER_FILE):
        offset = _DATA_OFFSET + rec * _RECORD_SIZE
        ts_raw = struct.unpack_from('<I', data, offset)[0]
        values = struct.unpack_from(f'<{_CHANNELS_PER_RECORD}h', data, offset + _RECORD_TIMESTAMP_SIZE)
        timestamps.append(ts_raw)
        rows.append(values)

    arr = np.array(rows, dtype=np.float64)
    arr[arr == _MISSING_VALUE] = np.nan
    df = pd.DataFrame(arr, columns=col_names)
    df.insert(0, 'timestamp', pd.to_datetime(timestamps, unit='s', utc=True))

    return df
