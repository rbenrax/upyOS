# jq like util
# TODO: this can be improved

import json
import utls

def pretty_print_json(obj, indent=0):
    result = []
    pad = ' ' * indent
    
    if isinstance(obj, dict):
        result.append(pad + '{\n')
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            comma = ',' if i < len(items) - 1 else ''
            key_str = json.dumps(key)
            
            if isinstance(value, (dict, list)):
                result.append(f'{" " * (indent + 2)}{key_str}: \n')
                result.append(pretty_print_json(value, indent + 2))
                if comma:
                    result.append(f'{" " * (indent + 2)}{comma}\n')
            else:
                result.append(f'{" " * (indent + 2)}{key_str}: {json.dumps(value)}{comma}\n')
                
        result.append(pad + '}\n')
        
    elif isinstance(obj, list):
        result.append(pad + '[\n')
        for i, item in enumerate(obj):
            comma = ',' if i < len(obj) - 1 else ''
            
            if isinstance(item, (dict, list)):
                result.append(pretty_print_json(item, indent + 2))
                if comma:
                    result.append(f'{" " * (indent + 2)}{comma}\n')
            else:
                result.append(f'{" " * (indent + 2)}{json.dumps(item)}{comma}\n')
                
        result.append(pad + ']\n')
        
    else:
        result.append(pad + json.dumps(obj) + '\n')
    
    return ''.join(result)

def __main__(args):

    #json_str = '{"method":"GET","headers":{"host":"mockhttp.org","x-forwarded-for":"79.117.243.67,188.114.111.212,34.111.9.76","user-agent":"upyOS-curl/1.0","cf-ray":"9a5b131f79d5ec8e-MAD","accept":"*/*","cdn-loop":"cloudflare; loops=1","cf-connecting-ip":"79.117.243.67","cf-ipcountry":"ES","cf-visitor":"{\\"scheme\\":\\"https\\"}","x-cloud-trace-context":"a2aaa6dabf5befb3189bd49998a98365/16631107423835223681;o=1","x-forwarded-proto":"https","via":"1.1 google","traceparent":"00-a2aaa6dabf5befb3189bd49998a98365-e6cd90162b0f7681-01","forwarded":"for=\\"188.114.111.212\\";proto=https","accept-encoding":"gzip, br"},"queryParams":{}}'
    
    if len(args) == 0 or "--h" in args:
        print("json jq utility\nUsage: jq <file>/<var> [>[>]] <file>/<envar>")
        return
    
    try:
        if utls.file_exists(args[0]): # file
            data = utls.load_conf_file(args[0])
        else:  # env var
            data = json.loads(utls.getenv(args[0]))
        formatted = pretty_print_json(data)
        utls.outs(args, formatted)
    except Exception as e:
        print("jq error:", e)
