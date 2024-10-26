"""fb test"""
from typing import cast
import fdb
import fdb.ibase as ib

# conn = fdb.connect(user='SADMIN', password='Fory_ip6',
#                    host='localhost', database='employee', port=3053,
#                    role='RDB$ADMIN',
#             fb_library_name=r'd:\git\sex\src\vendor\fbclient.dll_32_3_0', charset='WIN1251')
conn = fdb.connect(user='SADMIN', password='Fory_ip6',
                   host='localhost', database='GMLocal', port=3050,
                   role='RDB$ADMIN',
            fb_library_name=r'd:\git\sex\src\vendor\fbclient.dll_32_2_1', charset='WIN1251')
sconn = fdb.services.connect(host='localhost/3050', user='SADMIN', password='Fory_ip6')
sconn.get_statistics('GMLocal', show_only_db_header_pages=1)
while (line := sconn.readline()) is not None:
    print(line)
d = conn.database_info(fdb.isc_info_creation_date, 'b')

o_buf = b'\x00' * 127
api = fdb.fbcore.api
ts = ib.ISC_TIMESTAMP.from_buffer_copy(d, 0)
cast(ib.fbclient_API, api).isc_decode_timestamp(ts, o_buf)
print(d)
