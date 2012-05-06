import urllib

log_output_file = 'log/gps.log'
gps_output_file = '/home/daniel/com.itemcase.spider/src/out/gps-laptop-query.html'
local_gps_search_url = 'http://localhost/gps-laptop-query.html'
curl_files = [
    'http://50.116.1.34/spider/curl.php',                           # linode
    'http://www.personality-research.com/_moraes/curl.php',         # sonovitta
    'http://www.vestibularseriado.com.br/curl.php',                 # vestibularseriado
    'http://www.webulando.com.br/curl.php',                         # webulando
    'http://dbm01.no-ip.org/curl.php',                              # rafael
    'http://141.30.221.111:8787/curl.php',                          # filipe
    'http://www.students.ic.unicamp.br/~ra123530/_spider/curl.php', # unicamp
    'http://gpsc.comli.com/curl.php'                                # 000webhost
]

# http://50.116.1.34/spider/curl.php?url=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS9zZWFyY2g/cT1sYXB0b3Amc3RhcnQ9MCZ0Ym09c2hvcCZobD1lbi1VUw==
def mount_gps_search_url(query, page, curl_index):
    gps_search_param = urllib.urlencode({
        'q': query,
        'hl': 'en-US',
        'tbm': 'shop',
        'start': page*10-10
    })
    return curl_files[curl_index] + '?url=%s' % ('https://www.google.com/search?' + gps_search_param).encode('base64', 'strict')