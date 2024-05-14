import os
dev = True
if os.name == 'posix':
  dev = False 

# Linux machine is production server (Raspberry Pi)
# All other machines are development servers

ADMIN = [955187087911555152,1020995268159754321]
SHOP_CHANNEL = 1215343913121095722 if dev else 1142779979931856896
MOD_CHANNEL = 1215939069452877924 if dev else 1128038759083032657
TICKET_CHANNEL = 1215343913121095722 if dev else 1141476223546032278
GUILD = 1215342207385468978 if dev else 1097164415901650966