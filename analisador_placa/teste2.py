import pyvisa
from pyvisa import ResourceManager
m = ResourceManager()
resources_list = m.list_resources()
print(resources_list)
inst = m.open_resource(resources_list[1])

print("eae")
a = inst.write_raw(b"*IDN?")
f = inst.read_raw()
print(a)
inst.close()