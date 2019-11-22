import pyvisa
from pyvisa import ResourceManager
m = ResourceManager()
resources_list = m.list_resources()
inst = m.open_resource(resources_list[0])
print(resources_list)
inst.write_raw(b"*CONN")
inst.read_raw(3)
inst.close()