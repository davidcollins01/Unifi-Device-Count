from datetime import datetime
import os
import time
import zstandard
import pathlib
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt

dirname = os.path.join(os.getcwd(), 'log')
file_list = []
written_logs = []

# Decompress the zstandard files from the switch
for download in os.listdir(dirname):
    if download.endswith("zst"):
        with open (os.path.join(dirname,download), 'rb') as compressed:
            decomp = zstandard.ZstdDecompressor()
            decomp_path = pathlib.Path(compressed.name[:-4])
            with open(decomp_path,'wb') as destination:
                decomp.copy_stream(compressed, destination)

# Create a list of log files
for file in os.listdir(dirname):
    if file.startswith("daemon.log") and not file.endswith("zst"):
        file_list.append(os.path.join(dirname,file))

# Work through the log files to get the data
for log_file in file_list:
    with open(log_file, "r", encoding='latin-1') as f:
        lines = f.readlines()
        for line in lines:
            if ('dnsmasq-dhcp[' in line) and ('DHCPACK(br0)' in line):
                line.strip()
                timestr = time.strftime("%Y%m%d")
                with open ('logoutput-' + timestr + '.txt', 'a') as output_file:
                    output_file.write(line)
            else:
                pass
    f.close()

df = pd.read_csv('logoutput-' + timestr + '.txt', sep='\s+', names = ['DateTime','Device','Stamp1','Stamp2','IP','MAC','DeviceName'])
df = df.drop(columns=['Device','Stamp1','Stamp2','IP','MAC'])
df['DateTime'] = pd.to_datetime(df['DateTime']).dt.strftime('%Y-%m-%d')
df = df[df['DeviceName'].str.contains('DESKTOP-', na=False)]
df_summary = df.groupby('DateTime')['DeviceName'].nunique()
display(df_summary)