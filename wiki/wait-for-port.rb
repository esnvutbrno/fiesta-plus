require "socket"
require "timeout"

def port_open?(ip, port)
  begin
    TCPSocket.new(ip, port).close
    true
  rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH
    false
  end
end

def wait_for_port(ip, port)
  until port_open?(ip, port)
    sleep(0.5)
  end
end
