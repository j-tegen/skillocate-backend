import os

db_name = os.environ['SKILLOCATE_DB']
db_uid = os.environ['SKILLOCATE_UID']
db_pw = os.environ['SKILLOCATE_PW']
#driver = os.environ['SKILLOCATE_DRIVER']#"SQL+Server+Native+Client+10.0"#
server_name = os.environ['SKILLOCATE_SERVER']
host_ip = os.environ['SKILLOCATE_HOST']
secret_key = 'qwertyasdfghzxcvb'

print(host_ip)

ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])


connection_string = "postgresql://{uid}:{pw}@{server}:5432/{db}".format(server=server_name,
                                                                             uid=db_uid,
                                                                             pw=db_pw,
                                                                             db=db_name)
