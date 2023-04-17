import pwd

# This module presumes these users are already setup in the system.
# Otherwise, this will raise an exception on import, and it is OK
# to have that exception. I mean, seriously: why would anyone want
# to get into the console and break the users? Games will run in
# the lowest possible context (the "gamer" user, which lacks not
# only of permissions, but also of home directory on itself) which
# means they won't have any kind of ability to destroy these users,
# which leaves everything to the entire user responsibility.
#
# Three users are defined here:
# - root: This one deserves no explanation and should seldom to
#         never directly be used. It will run this overall service.
# - pi: The main user. It is a sudo-enabled user and will never be
#       directly used outside of the common interface, unless the
#       user explicitly invokes a terminal or external software.
#       Using this user is something that must be done CAREFULLY,
#       anyway, because there are things about this console that
#       are accessible by the user and the entire experience could
#       also be broken. Users should take the same, or similar,
#       care that is taken when using root. This user will be the
#       one who prepares everything to run a game.
# - gamer: This is the user that plays games. It has the lowest
#          possible privilege and will only run games and write
#          in a permission-less filesystem.
ROOT_NAME = "root"
ROOT = pwd.getpwnam(ROOT_NAME)
ROOT_UID = ROOT.pw_uid
ROOT_GID = ROOT.pw_gid
PI_NAME = "pi"
PI = pwd.getpwnam(PI_NAME)
PI_UID = PI.pw_uid
PI_GID = PI.pw_gid
GAMER_NAME = "gamer"
GAMER = pwd.getpwnam(GAMER_NAME)
GAMER_UID = GAMER.pw_uid
GAMER_GID = GAMER.pw_gid
