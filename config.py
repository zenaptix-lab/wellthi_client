FILE_DROP_CONFIG = {
    'known_files': [".DS_Store"],
    'path_load': "test/resources/",  # "/path/to/listen/folder/"
    # 'user_id': "mourits",
    'file_timestamp': 1541515173
}
CHAT_BOT_CONFIG = {
    'chat_server_version': '2018-09-20'
}
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'events': ['ian', 'd01d68b2-3864-4401-a26d-92b10ef74e48']  # user id events sub
}
WELLTHI_SERVER_CONFIG = {
    'biometric_data_endpoint': 'http://0.0.0.0:8080/biometric/',
    'assessment_data_endpoint': 'http://0.0.0.0:8080/assessment/'
}
