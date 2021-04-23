import amuse
if amuse.config.community.mesa_version == "2208":
    from amuse.community.mesa_2208.interface import *
elif amuse.config.community.mesa_version == "15140":
    from amuse.community.mesa_15140.interface import *
elif amuse.config.community.mesa_version == "latest":
    from amuse.community.mesa_15140.interface import *
else:
    from amuse.community.mesa_2208.interface import *
