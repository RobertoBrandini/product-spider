import urllib

log_output_file = 'log/gps.log'
gps_output_file = '/home/daniel/com.itemcase.spider/src/out/gps-laptop-query.html'
local_gps_search_url = 'http://localhost/gps-laptop-query.html'
curl_files = [
    'http://localhost/spider/curl.php',     # local
    'http://50.116.1.34/spider/curl.php',   # linode
    'http://141.30.221.111:8787/curl.php'   # lopes
]

def mount_gps_search_url(query, page):
    gps_search_param = urllib.urlencode({
        'q': query,
        'hl': 'en-US',
        'tbm': 'shop',
        'start': page*10-10
    })
    return curl_files[2] + '?url=%s' % ('https://www.google.com/search?' + gps_search_param).encode('base64', 'strict')
