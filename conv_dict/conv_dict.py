import os
import zipfile
from datetime import datetime

import csv

# 品詞変換辞書（Mozc/Google → MSIME）
POS_MAP = {
    "名詞": "名詞",
    "*名詞": "*名詞",
    "名詞非接尾": "名詞非接尾",
    "短縮よみ": "短縮よみ",
    "サジェストのみ": "短縮よみ",
    "固有名詞": "固有名詞",
    "*固有名詞": "固有名詞",
    "固有商品": "固有名詞",
    "人名": "人名",
    "姓": "姓",
    "*姓": "姓",
    "名": "名",
    "*名": "名",
    "組織": "社名",
    "地名": "地名",
    "国": "国",
    "支庁": "支庁",
    "県": "県",
    "郡": "郡",
    "区": "区",
    "市": "市",
    "町": "町",
    "村": "村",
    "駅": "駅",
    "名詞サ変": "サ行(する)&名詞",
    "名詞サ変非接尾": "サ行(する)&名詞",
    "名詞ザ変": "サ行(する)&名詞",
    "名詞形動": "形容動詞&名詞",
    "名サ形動": "サ行(する)&名詞",
    "副詞的名詞": "副詞的名詞",
    "形容動詞": "形容動詞",
    "形容動詞サ変": "形容動詞",
    "形容動詞ノ": "形容動詞ノ",
    "形容動詞タル": "形容動詞タル",
    "数詞": "数詞",
    "冠数詞": "冠数詞",
    "記号": "単漢字",
    "アルファベット": "単漢字",
    "顔文字": "顔文字",
    "副詞04": "副詞",
    "連体詞": "連体詞",
    "接続詞": "接続詞",
    "感動詞": "感動詞",
    "接頭語": "接頭語",
    "接頭人名": "姓名接頭語",
    "接頭地名": "地名接頭語",
    "接頭数詞": "接頭助数詞",
    "助数詞": "助数詞",
    "接尾語": "接尾語",
    "*接尾語": "接尾語",
    "接尾人名": "姓名接尾語",
    "接尾地名": "地名接尾語",
    "動詞ワ行五段名": "ワ行五段",
    "動詞ワ行五段": "ワ行五段",
    "動詞ワう五段名": "ワ行五段",
    "動詞ワう五段": "ワ行五段",
    "動詞カ行五段名": "カ行五段",
    "動詞カ行五段": "カ行五段",
    "動詞カ促五段名": "カ行五段",
    "動詞カ促五段": "カ行五段",
    "動詞サ行五段名": "サ行五段",
    "動詞サ行五段": "サ行五段",
    "動詞タ行五段名": "タ行五段",
    "動詞タ行五段": "タ行五段",
    "動詞ナ行五段名": "名詞",
    "動詞ナ行五段": "名詞",
    "動詞マ行五段名": "マ行五段",
    "動詞マ行五段": "マ行五段",
    "動詞ラ行五段名": "ラ行五段",
    "動詞ラ行五段": "ラ行五段",
    "動詞ラい段名": "ラ行五段",
    "動詞ラい五段": "ラ行五段",
    "動詞ガ行五段名": "ガ行五段",
    "動詞ガ行五段": "ガ行五段",
    "動詞バ行五段名": "バ行五段",
    "動詞バ行五段": "バ行五段",
    "動詞ハ行四段": "名詞",
    "動詞一段": "一段動詞",
    "一段名詞": "一段&名詞",
    "動詞カ変": "名詞",
    "動詞サ変": "サ行(する)",
    "動詞ザ変": "ザ行(ずる)",
    "動詞ラ変": "名詞",
    "形容詞": "形容詞",
    "形容詞しく": "形容詞",
    "形容詞ガル": "形容詞ガル",
    "形容詞ュウ": "形容詞ュウ",
    "終助詞": "名詞",
    "句読点": "単漢字",
    "慣用句": "慣用句",
    "独立語": "慣用句",
    "単漢字": "単漢字",
    "抑制単語": "名詞"
}


def convert_dictionary(input_path, google_output_path, msime_output_path):
    google_entries = []
    msime_entries = []

    with open(input_path, 'r', encoding='utf-8') as infile:
        next(infile)  # ヘッダー行をスキップ
        for line in infile:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # コメント行または空行をスキップ

            parts = line.split('\t')
            if len(parts) < 3:
                continue  # 不正な行はスキップ
            elif len(parts) == 3:
                reading, word, pos, comment = parts[:3] + ['']
            else:
                reading, word, pos, comment = parts[:4]
            google_entries.append(f"{reading}\t{word}\t{pos}\t{comment}")

            msime_pos = POS_MAP.get(pos, "名詞")  # 未定義なら名詞にフォールバック
            msime_entries.append(f"{reading},{word},{msime_pos},{comment}")

    # Google日本語入力用に出力（TSV形式）
    with open(google_output_path, 'w', encoding='utf-8') as g_out:
        g_out.write('\n'.join(google_entries))

    # MS-IME用に出力（CSV形式）
    with open(msime_output_path, 'w', encoding='utf-16') as m_out:
        m_out.write('\n'.join(msime_entries))

def get_next_version(output_dir, date_str):
    existing = [
        f for f in os.listdir(output_dir)
        if f.startswith(f"dict_{date_str}_") and f.endswith(".zip")
    ]
    return f"v{len(existing) + 1}"


# 使用例
if __name__ == "__main__":

    convert_dictionary(
        input_path='曲名.tsv',
        google_output_path='conv_dict/tokisen_songs_google.txt',
        msime_output_path='conv_dict/tokisen_songs_microsoft.txt'
    )

    convert_dictionary(
        input_path='人名・固有名詞.tsv',
        google_output_path='conv_dict/tokisen_names_google.txt',
        msime_output_path='conv_dict/tokisen_names_microsoft.txt'
    )

    # Zipファイル名：tokisen_dict_YYYYMMDD_vX.zip
    date_str = datetime.now().strftime("%Y%m%d")
    version = get_next_version('conv_dict', date_str)
    zip_name = f"tokisen_dict_{date_str}_{version}.zip"
    zip_path = os.path.join('conv_dict', zip_name)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write('conv_dict/tokisen_songs_google.txt', arcname="tokisen_songs_google.txt")
        zipf.write('conv_dict/tokisen_songs_microsoft.txt', arcname="tokisen_songs_microsoft.txt")
        zipf.write('conv_dict/tokisen_names_google.txt', arcname="tokisen_names_google.txt")
        zipf.write('conv_dict/tokisen_names_microsoft.txt', arcname="tokisen_names_microsoft.txt")

    print(f"辞書ファイルを作成しました: {zip_path}")