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

# global
masscan_output_file = 'masscan_output.json'
ip_list_file = 'ip_list.txt'

parser = argparse.ArgumentParser()
parser.add_argument('start', help='start of ip address range')
parser.add_argument('end', help='end of ip address range')

args = parser.parse_args()

start_address = args.start
end_address = args.end



def cleanup():
    # remove masscan_output_file
    delete_paused = f'rm {masscan_output_file}'
    r = subprocess.run(delete_paused.split(' '), capture_output=True, text=True)
    exit_status = r.returncode

    # remove ip_list_file
    delete_paused = f'rm {ip_list_file}'
    r = subprocess.run(delete_paused.split(' '), capture_output=True, text=True)
    exit_status = r.returncode

''' get cidr range '''

# convert to cidr range
start = ipaddress.IPv4Address(start_address)
end = ipaddress.IPv4Address(end_address)
cidr = list(ipaddress.summarize_address_range(start, end))
cidr = [str(x) for x in cidr]
assert len(cidr) == 1, "number of cidr ranges found does not equal 1"
cidr = cidr[0]

''' run masscan '''

print(f'performing masscan on cidr range {cidr}')
# masscan -p80,443 --rate 1000 101.44.16.0/20
masscan = f'masscan -p80,443 --rate 1000 -oJ {masscan_output_file} {cidr}'
r = subprocess.run(masscan.split(' '), capture_output=True, text=True)
exit_status = r.returncode
if (exit_status != 0):
    print(f'masscan ERROR: {r.stderr}')
    cleanup()
    exit()

# delete paused.conf
delete_paused = 'rm paused.conf'
r = subprocess.run(delete_paused.split(' '), capture_output=True, text=True)
exit_status = r.returncode
#assert exit_status == 0, 'unable to delete paused.conf'

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
# write to ip_list_file
with open(ip_list_file, 'w') as file:
    file.write(ips)

''' run httpx '''

print(f'performing httpx on {ip_list_file}')
run_httpx = f'httpx -status-code -title -server -tech-detect -location -nf -list {ip_list_file}'
r = subprocess.run(run_httpx.split(' '), capture_output=True, text=True)
exit_status = r.returncode

# parse, sort and print output
r = r.stdout
r = r.strip()
r = r.split('\n')
r = sorted(r, key=lambda x: x.split('//')[1])
for thing in r: print(thing)

''' cleanup '''
cleanup()