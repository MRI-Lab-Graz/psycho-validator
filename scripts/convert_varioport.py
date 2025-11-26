import struct
import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

def read_varioport_header(f):
    """
    Reads the Varioport file header and channel definitions.
    Based on the R code 'read_vpd.R' and inspection of VPDATA.RAW.
    """
    f.seek(0)
    
    # 1. File Header
    # Byte 2: Header Length
    f.seek(2)
    hdrlen = struct.unpack('>H', f.read(2))[0]
    
    # Byte 4: Channel Offset
    f.seek(4)
    choffs = struct.unpack('>H', f.read(2))[0]
    
    # Byte 6: Header Type
    f.seek(6)
    hdrtype = struct.unpack('>B', f.read(1))[0]
    
    # Byte 7: Channel Count
    f.seek(7)
    chcnt = struct.unpack('>B', f.read(1))[0]
    
    # Byte 20: Global Scan Rate (Not in R code, but found in file)
    f.seek(20)
    scnrate = struct.unpack('>H', f.read(2))[0]
    if scnrate == 0:
        print("Warning: Global Scan Rate at offset 20 is 0. Defaulting to 150 Hz.")
        scnrate = 150
        
    print(f"Header Info: Length={hdrlen}, Type={hdrtype}, Channels={chcnt}, BaseRate={scnrate}")
    
    # 2. Channel Definitions
    channels = []
    for i in range(chcnt):
        offset = choffs + i * 40
        f.seek(offset)
        ch_def = f.read(40)
        
        name = ch_def[0:6].decode('ascii', errors='ignore').strip()
        unit = ch_def[6:10].decode('ascii', errors='ignore').strip()
        # data_size: 0=uint8, 1=uint16. Actual bytes = val + 1
        dsize_code = ch_def[11]
        dsize = dsize_code + 1
        
        scnfac = ch_def[12]
        strfac = ch_def[14]
        
        mul = struct.unpack('>H', ch_def[16:18])[0]
        doffs = struct.unpack('>H', ch_def[18:20])[0]
        div = struct.unpack('>H', ch_def[20:22])[0]
        
        # Offset to data (relative to some base, R code adds hdrlen)
        offs_val = struct.unpack('>I', ch_def[24:28])[0]
        abs_offs = offs_val + hdrlen
        
        chlen = struct.unpack('>I', ch_def[28:32])[0]
        
        # Calculate effective sampling rate
        # chscnrate = scnrate / scnfac
        # chstrrate = chscnrate / strfac
        if scnfac == 0: scnfac = 1
        if strfac == 0: strfac = 1
        fs = scnrate / (scnfac * strfac)
        
        chan_info = {
            'index': i,
            'name': name,
            'unit': unit,
            'dsize': dsize,
            'scnfac': scnfac,
            'strfac': strfac,
            'mul': mul,
            'doffs': doffs,
            'div': div,
            'abs_offs': abs_offs,
            'chlen': chlen,
            'fs': fs
        }
        channels.append(chan_info)
        print(f"Channel {i}: {name} ({unit}), fs={fs:.2f}Hz, len={chlen}, dsize={dsize}")
        
    return hdrlen, hdrtype, channels

def convert_varioport(raw_path, output_path, sidecar_path):
    """
    Converts a Varioport .RAW file to BIDS .tsv.gz and .json.
    """
    file_size = os.path.getsize(raw_path)
    
    with open(raw_path, 'rb') as f:
        hdrlen, hdrtype, channels = read_varioport_header(f)
        
        # Identify active channels
        # In the test file, EKG has len=-1 (0xFFFFFFFF), others have 0.
        # We assume only channels with len != 0 are active.
        active_channels = [c for c in channels if c['chlen'] != 0]
        
        if not active_channels:
            print("No active channels found (all have length 0). Assuming all are active?")
            active_channels = channels
            
        # For now, we only support the case where there is one main data stream
        # or we assume the file is just the data for the active channels.
        # Given the analysis, it seems the file contains only EKG data.
        
        # We will process the first active channel as the main signal
        target_channel = active_channels[0]
        print(f"Processing target channel: {target_channel['name']}")
        
        # Move to data start
        if hdrtype == 6:
            # Type 6: Reconfigured / Demultiplexed
            # Data for each channel is at specific offsets
            print("Detected Type 6 (Reconfigured) file. Reading channels independently.")
            
            # We can process all active channels or just the target one
            # For now, let's stick to the target channel logic but use correct offsets
            
            # The R script says:
            # offs = readBin(..., size=4) + hdrlen
            # seek(offs)
            # readBin(..., n=nofdatapoints)
            
            data_start = target_channel['abs_offs']
            data_len_bytes = target_channel['chlen']
            
            f.seek(data_start)
            raw_bytes = f.read(data_len_bytes)
            num_bytes = len(raw_bytes)
            
            dsize = target_channel['dsize']
            num_samples = num_bytes // dsize
            
            print(f"Read {num_bytes} bytes from offset {data_start}. Samples: {num_samples}")
            
        else:
            # Type 7: Raw / Multiplexed (or other)
            # The data starts after the header and is interleaved.
            # We currently treat it as a single stream, which is imperfect for Type 7.
            print(f"Detected Type {hdrtype} (Raw/Multiplexed). Warning: Data may be interleaved.")
            
            data_start = hdrlen
            f.seek(data_start)
            
            # Read all remaining data
            raw_bytes = f.read()
            num_bytes = len(raw_bytes)
            
            # Assume data is a sequence of samples for the target channel
            dsize = target_channel['dsize']
            num_samples = num_bytes // dsize
            
            print(f"Read {num_bytes} bytes. Expected {num_samples} samples (dsize={dsize}).")
        
        # Decode
        
        # Decode
        if dsize == 2:
            # Big Endian uint16
            fmt = f'>{num_samples}H'
            raw_values = struct.unpack(fmt, raw_bytes[:num_samples*dsize])
        elif dsize == 1:
            fmt = f'>{num_samples}B'
            raw_values = struct.unpack(fmt, raw_bytes[:num_samples*dsize])
        else:
            raise ValueError(f"Unsupported data size: {dsize}")
            
        # Apply scaling
        # value = (raw - doffs) * mul / div
        doffs = target_channel['doffs']
        mul = target_channel['mul']
        div = target_channel['div']
        if div == 0: div = 1
        
        data_array = np.array(raw_values, dtype=float)
        data_array = (data_array - doffs) * mul / div
        
        # Create DataFrame
        df = pd.DataFrame({
            target_channel['name']: data_array
        })
        
        # Save to TSV
        print(f"Saving to {output_path}...")
        df.to_csv(output_path, sep='\t', index=False, compression='gzip')
        
        # Create Sidecar JSON
        sidecar = {
            "SamplingFrequency": target_channel['fs'],
            "StartTime": 0,
            "Columns": [target_channel['name']],
            "Manufacturer": "Becker Meditec",
            "ManufacturersModelName": "Varioport",
            "Note": "Converted from VPDATA.RAW using reverse-engineered specs."
        }
        
        with open(sidecar_path, 'w') as jf:
            json.dump(sidecar, jf, indent=4)
            
        print("Conversion complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Varioport RAW to BIDS")
    parser.add_argument("input_file", help="Path to VPDATA.RAW")
    parser.add_argument("output_tsv", help="Path to output .tsv.gz")
    parser.add_argument("output_json", help="Path to output .json")
    
    args = parser.parse_args()
    
    convert_varioport(args.input_file, args.output_tsv, args.output_json)
