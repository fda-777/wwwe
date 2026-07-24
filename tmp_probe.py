import socket
from agents.health_agent import check_port_free

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    print('port', port)
    result = check_port_free(port)
    print(result)

    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(('127.0.0.1', port))
    except OSError as exc:
        print('connect failed', repr(exc), getattr(exc, 'errno', None))
    else:
        print('connect ok')
    finally:
        probe.close()
