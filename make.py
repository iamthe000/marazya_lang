import sqlite3
import os
import re

# ファイル名の設定
MD_FILE_NAME = 'マラシア語概論.md'
DB_FILE_NAME = 'marazya.db'

def parse_and_insert():
    # ファイルの存在確認
    if not os.path.exists(MD_FILE_NAME):
        print(f"エラー: '{MD_FILE_NAME}' が見つかりません。スクリプトと同じディレクトリに配置してください。")
        return

    # データベースへの接続（ファイルがなければ自動生成されます）
    conn = sqlite3.connect(DB_FILE_NAME)
    cursor = conn.cursor()

    # テーブルの作成
    # 複数要素（和訳、英訳、品詞など）はTEXTとしてそのまま格納します
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marazya TEXT NOT NULL,
        english TEXT,
        japanese TEXT,
        part_of_speech TEXT,
        notes TEXT
    )
    ''')
    
    # 既存のデータをクリア（スクリプトを何度実行しても重複しないようにするため）
    cursor.execute('DELETE FROM words')

    # Markdownファイルの読み込み
    with open(MD_FILE_NAME, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    is_vocab_table = False
    inserted_count = 0

    for line in lines:
        line = line.strip()
        
        # 「単語一覧」テーブルのヘッダーを検知
        if "| Marazya語 | 英語" in line:
            is_vocab_table = True
            continue
            
        # ヘッダー下の区切り線（|---|---|...）をスキップ
        if is_vocab_table and re.match(r'^\|[-\s|]+\|$', line):
            continue
            
        # テーブルの終端（空行やテーブル外のテキスト）を検知したらループを抜ける
        if is_vocab_table and not line.startswith('|'):
            if inserted_count > 0: 
                break
            continue

        # テーブルの行データをパースしてDBに挿入
        if is_vocab_table and line.startswith('|'):
            # 行を '|' で分割し、前後の空白を削除。最初と最後の空要素をスライス [1:-1] で除外
            parts = [p.strip() for p in line.split('|')][1:-1]
            
            if len(parts) >= 5:
                # 検索時に邪魔になるマークダウンの太字指定（**）を削除
                marazya = parts[0].replace('**', '') 
                english = parts[1]
                japanese = parts[2]
                part_of_speech = parts[3]
                notes = parts[4]
                
                cursor.execute('''
                INSERT INTO words (marazya, english, japanese, part_of_speech, notes)
                VALUES (?, ?, ?, ?, ?)
                ''', (marazya, english, japanese, part_of_speech, notes))
                
                inserted_count += 1

    # 変更を保存して接続を閉じる
    conn.commit()
    conn.close()
    
    print(f"完了しました！ {inserted_count} 件の単語を '{DB_FILE_NAME}' に保存しました。")

if __name__ == '__main__':
    parse_and_insert()