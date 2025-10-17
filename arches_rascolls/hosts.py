import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_rascolls"),
        "arches_rascolls.urls",
        name="arches_rascolls",
    ),
)
