from sshtunnel import SSHTunnelForwarder

server = SSHTunnelForwarder(
    ('34.56.206.36', 22),
    ssh_username='root',
    ssh_pkey='/home/thuya/.ssh/id_rsa',
    remote_bind_address=('127.0.0.1', 5432),
    local_bind_address=('127.0.0.1', 5433)
)

server.start()
print(f"Tunnel started: {server.local_bind_host}:{server.local_bind_port}")
server.stop()
