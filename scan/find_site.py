import ipaddress
import subprocess
import json
import argparse

'''
    check ports 80 and 443 across a range of ip addresses
    requires
        masscan https://github.com/robertdavidgraham/masscan
        httpx   https://github.com/projectdiscovery/httpx
'''

''' global '''
masscan_output_file = 'masscan_output.json'
ip_list_file = 'ip_list.txt'
paused_file = 'paused.conf'

parser = argparse.ArgumentParser()
parser.add_argument('start', help='start of ip address range')
parser.add_argument('end', help='end of ip address range')

args = parser.parse_args()

start_address = args.start
end_address = args.end



def cleanup():
    global masscan_output_file
    global ip_list_file
    global paused_file

    # remove masscan_output_file
    cmd = f'rm {masscan_output_file}'
    r = subprocess.run(cmd.split(' '), capture_output=True, text=True)

    # remove ip_list_file
    cmd = f'rm {ip_list_file}'
    r = subprocess.run(cmd.split(' '), capture_output=True, text=True)

    # delete paused.conf
    cmd = f'rm {paused_file}'
    r = subprocess.run(cmd.split(' '), capture_output=True, text=True)


def get_cidr_range():
    global start_address
    global end_address
    # convert to cidr range
    start = ipaddress.IPv4Address(start_address)
    end = ipaddress.IPv4Address(end_address)
    cidr = list(ipaddress.summarize_address_range(start, end))
    cidr = [str(x) for x in cidr]
    return cidr
    
def do_masscan(cidr):
    global masscan_output_file
    global ip_list_file
    print(f'performing masscan on cidr range {cidr}')
    # masscan -p80,443 --rate 1000 101.44.16.0/20
    masscan = f'masscan -p80,443 --rate 1000 -oJ {masscan_output_file} {cidr}'
    r = subprocess.run(masscan.split(' '), capture_output=True, text=True)
    exit_status = r.returncode
    if (exit_status != 0):
        print(f'masscan ERROR: {r.stderr}')
        cleanup()
        exit()

    # process results
    with open(masscan_output_file, 'r') as file:
        file_text = file.read()
    if (len(file_text) == 0):
        print('no results were found')
        cleanup
        exit()
    file_contents = json.loads(file_text)

    # get list of ips
    ips = [x['ip'] for x in file_contents]
    ips = set(ips)
    ips = '\n'.join(ips)
    print(f'found {len(ips)} possible ips')

    # write to ip_list_file
    with open(ip_list_file, 'w') as file:
        file.write(ips)

def do_httpx():
    global ip_list_file
    print(f'performing httpx on {ip_list_file}')
    run_httpx = f'httpx -status-code -title -server -tech-detect -location -nf -list {ip_list_file}'
    r = subprocess.run(run_httpx.split(' '), capture_output=True, text=True, errors='ignore')
    exit_status = r.returncode

    # parse, sort and print output
    r = r.stdout
    r = r.strip()
    r = r.split('\n')
    r = sorted(r, key=lambda x: x.split('//')[1])
    for thing in r: print(thing)

def pick_cidr_range(cidr_ranges):
    for i, cidr_range in enumerate(cidr_ranges):
        print(f'[{i}] {cidr_range}')
    while True:
        range_index = input('range index> ')
        if range_index.isnumeric():
            range_index = int(range_index)
            if range_index >= 0 and range_index < len(cidr_ranges): break
            else:
                print('invalid choice')
        else:
            print('invalid choice')
    return range_index

''' main '''
# get cidr range
cidr_ranges = get_cidr_range()
assert len(cidr_ranges) > 0, f'no cidr ranges found'

if (len(cidr_ranges) > 1):
    range_index = pick_cidr_range(cidr_ranges)
    cidr_range = cidr_ranges[range_index]
else:
    cidr_range = cidr_ranges[0]

# run masscan
do_masscan(cidr_range)

# run httpx
do_httpx()

# cleanup
cleanup()