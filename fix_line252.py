# 252行目の\rを削除するスクリプト
with open('システム評価', 'rb') as f:
    lines = f.readlines()

# 252行目（インデックス251）の\rを削除
if len(lines) > 251:
    lines[251] = lines[251].replace(b'\r', b'')
    
    with open('システム評価', 'wb') as f:
        f.writelines(lines)
    print('252行目の\\rを削除しました')
else:
    print('エラー: 252行目が見つかりません')


