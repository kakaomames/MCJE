import hashlib
import json
import os
import platform
import socket
import subprocess

# --------------------------------------------------
# 【設定項目】お使いのLAN環境に合わせて書き換えてください
# --------------------------------------------------
# ※共有フォルダのパス形式はOSごとに異なるため、ご自身のマウント方法に合わせて指定してください
# 例 (Windows): r"\\192.168.1.50\Shared\minecraft"
# 例 (Mac/Linux): "/Volumes/Shared/minecraft" や "/mnt/minecraft"
LAN_MINECRAFT_DIR = r"./Minecraft"

VERSION = "26.2"
ASSET_INDEX = "26.2"
# --------------------------------------------------

# 1. どのOSでも動く方法で「デバイス名（ホスト名）」を取得
# 例: "My-MacBook", "DESKTOP-123", "ubuntu-server"
device_name = socket.gethostname()
PLAYER_NAME = device_name.replace(".", "_")  # マイクラの仕様上、ドットはアンダースコアに置換

# 2. デバイス固有の不変IDから、マイクラ用の決定論的UUID（Offline UUID）を生成
# 機体名からハッシュ値を作り、常にそのマシン固定のUUID(バージョン4風)を生成
hash_input = f"minecraft-lan-id-{device_name}".encode("utf-8")
hasher = hashlib.md5(hash_input).hexdigest()
AUTH_UUID = f"{hasher[0:8]}-{hasher[8:12]}-4{hasher[13:16]}-a{hasher[17:20]}-{hasher[20:32]}"

print(f"Detected OS: {platform.system()}")
print(f"Device-Based Player Name: {PLAYER_NAME}")
print(f"Device-Based Hardware UUID: {AUTH_UUID}")
# --------------------------------------------------

# 各種パスの自動組み立て
json_path = "Minecraft/versions/26.2/26.2.json"
client_jar = "release/26.2.jar"
libraries_dir = "lib/*"
assets_dir = "assets/


# 44行目の「with open...」の直前にこれを貼り付けてください
print(f"[DEBUG] 探しているJSONの絶対パス: {os.path.abspath(json_path)}")
parent_dir = os.path.dirname(json_path)
if os.path.exists(parent_dir):
    print(f"[DEBUG] フォルダは存在します。中身のファイル一覧: {os.listdir(parent_dir)}")
else:
    print(f"[DEBUG] エラー：そもそもフォルダ '{parent_dir}' が存在しません！")

# JSONの読み込み
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 置き換えマッピング
replacements = {
    "${auth_player_name}": PLAYER_NAME,
    "${version_name}": VERSION,
    "${game_directory}": LAN_MINECRAFT_DIR,
    "${assets_root}": assets_dir,
    "${assets_index_name}": ASSET_INDEX,
    "${auth_uuid}": AUTH_UUID,
    "${auth_access_token}": "dummy_token",
    "${clientid}": "dummy_client",
    "${auth_xuid}": "dummy_xuid",
    "${version_type}": "release",
}

# 3. OSごとに「クラスパスの区切り文字」を自動判定
# Windowsは「;」、MacやLinuxは「:」
path_separator = ";" if platform.system() == "Windows" else ":"
classpath = f"{client_jar}{path_separator}{libraries_dir}"

# Javaコマンドのベース作成
cmd = ["java", "-Xmx2G", "-cp", classpath, "net.minecraft.client.main.Main"]

# 引数の解析と追加
if "arguments" in data and "game" in data["arguments"]:
    for arg in data["arguments"]["game"]:
        if isinstance(arg, str):
            cmd.append(replacements.get(arg, arg))
elif "minecraftArguments" in data:
    arg_string = data["minecraftArguments"]
    for k, v in replacements.items():
        arg_string = arg_string.replace(k, v)
    cmd.extend(arg_string.split(" "))

print("Starting Cross-Platform Minecraft from LAN...")
subprocess.run(cmd)
