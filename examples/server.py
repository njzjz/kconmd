from kconMD import kconMD
from kconMD.server import kconMD_server

kconMD_server(kconMD("ch4all-120762.pb","ch4.xyz","force",cell=[31.219299,31.219299,31.219299])).response()
